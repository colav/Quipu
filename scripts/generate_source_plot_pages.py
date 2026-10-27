import json
import time
from pathlib import Path

import requests

BASE = "https://api.dev.impactu.colav.co"
OUT = Path("api-reference/source/plots")
FENCE = "`" * 3

# Muestras representativas de fuentes por volumen de producción colombiana
SAMPLES = {
    "high": ("6aad68732be7843cde64e41c", "Fuente con alta producción"),
    "mid":  ("6aad68732be7843cde64e41b", "Fuente con producción media"),
}

# (plot, título, descripción)
# El tipo de gráfico es "bar" pero con y categórico (cuartil como string)
PLOTS = [
    (
        "annual_scimago_quartile",
        "Cuartil Scimago por año",
        "Cuartil Scimago de la fuente en cada año disponible.",
    ),
]

RESPONSE_SCHEMA = """\
<ResponseField name="plot" type="object[]">
  Lista de puntos del gráfico, ordenados por año ascendente.
  <Expandable title="propiedades de cada punto">
    <ResponseField name="x" type="integer">
      Año.
    </ResponseField>
    <ResponseField name="y" type="string">
      Cuartil Scimago de la fuente en ese año: `"Q1"`, `"Q2"`, `"Q3"`, `"Q4"`
      o `"Sin cuartil"` cuando no hay clasificación disponible.
    </ResponseField>
  </Expandable>
</ResponseField>"""


def shrink(value, items=4, text=100):
    if isinstance(value, list):
        return [shrink(v, items, text) for v in value[:items]]
    if isinstance(value, dict):
        return {k: shrink(v, items, text) for k, v in value.items()}
    if isinstance(value, str) and len(value) > text:
        return value[:text] + "..."
    return value


def fetch(plot, source_id):
    url = f"{BASE}/source/{source_id}/products"
    try:
        response = requests.get(url, params={"plot": plot}, timeout=180)
        if response.status_code != 200:
            return None
        data = response.json()
        return data if data else None
    except (requests.RequestException, ValueError):
        return None


def page(plot, title, description, examples):
    tabs = "\n\n".join(
        f"{FENCE}json {label}\n{json.dumps(shrink(data), ensure_ascii=False, indent=2)}\n{FENCE}"
        for label, data in examples.items()
    )
    note = """\
<Note>
  A diferencia de los demás indicadores de barras, el eje Y contiene el cuartil
  como cadena de texto (`"Q1"`, `"Q2"`, `"Q3"`, `"Q4"` o `"Sin cuartil"`), no
  un valor numérico.
</Note>

"""
    return f"""---
title: "{title}"
api: "GET https://api.dev.impactu.colav.co/source/{{source_id}}/products"
description: "{description}"
sidebarTitle: "{title}"
---

{description} Tipo de gráfico: **Barras**.

{note}## Parámetros

<ParamField path="source_id" type="string" required>
  Identificador de la fuente.
</ParamField>

<ParamField query="plot" type="string" required>
  Debe ser `{plot}`.
</ParamField>

## Respuesta

{RESPONSE_SCHEMA}

<ResponseExample>
{tabs}
</ResponseExample>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages, overview = [], []

    for plot, title, description in PLOTS:
        examples = {}
        for source_id, label in SAMPLES.values():
            data = fetch(plot, source_id)
            if data is not None:
                examples[label] = data
            time.sleep(0.3)

        slug = plot.replace("_", "-")
        (OUT / f"{slug}.mdx").write_text(page(plot, title, description, examples), encoding="utf-8")
        pages.append(f"api-reference/source/plots/{slug}")
        overview.append(f"| [{title}](/api-reference/source/plots/{slug}) | `{plot}` | Barras |")
        print(f"{plot}: {', '.join(examples) or 'sin datos'}")

    overview_page = f"""---
title: "Indicadores de una fuente"
description: "Catálogo de indicadores que devuelve el endpoint de productos de una fuente con el parámetro plot."
sidebarTitle: "Catálogo"
---

Con el parámetro `plot`, el endpoint [Productos de una fuente](/api-reference/source/get-products) devuelve un indicador en lugar de la lista de productos.

```text
GET /source/{{source_id}}/products?plot=<indicador>
```

Los indicadores aceptan los mismos filtros que el listado de productos.

| Indicador | Valor de `plot` | Gráfico |
| --- | --- | --- |
{chr(10).join(overview)}
"""
    (OUT / "overview.mdx").write_text(overview_page, encoding="utf-8")
    print("\nPáginas para docs.json:")
    print(json.dumps(["api-reference/source/plots/overview"] + pages, indent=2))


if __name__ == "__main__":
    main()
