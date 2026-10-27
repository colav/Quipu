import json
import time
from pathlib import Path

import requests

BASE = "https://api.dev.impactu.colav.co"
OUT = Path("api-reference/person/plots")
FENCE = "`" * 3

# Muestra representativa de autores por volumen de producción
SAMPLES = {
    "high": ("0000150053", "Autor con alta producción"),
    "mid":  ("0000026847", "Autor con producción media"),
}

KIND = {"bar": "Barras", "pie": "Torta", "venn": "Diagrama de Venn", "map": "Mapa", "network": "Red"}

# Plots compartidos con la entidad Affiliation
SIMPLE_PLOTS = [
    ("annual_evolution_by_impactu_classification", "Evolución anual por clasificación ImpactU", "Productos por año según la clasificación de ImpactU.", "bar"),
    ("annual_citation_count", "Citas por año", "Cantidad de citas recibidas por año.", "bar"),
    ("annual_articles_open_access", "Artículos de acceso abierto por año", "Artículos por año según su estado de acceso abierto.", "bar"),
    ("annual_articles_by_top_publishers", "Artículos por año de las principales editoriales", "Artículos por año de las editoriales con más artículos.", "bar"),
    ("annual_apc_expenses", "Gasto anual en APC", "Gasto en cargos por procesamiento de artículos (APC) por año.", "bar"),
    ("most_used_title_words", "Palabras más usadas en los títulos", "Palabras más frecuentes en los títulos de los productos.", "pie"),
    ("articles_by_publisher", "Artículos por editorial", "Distribución de artículos por editorial.", "pie"),
    ("products_by_subject", "Productos por área de conocimiento", "Distribución de productos por tópico principal.", "pie"),
    ("articles_by_access_route", "Artículos por ruta de acceso", "Distribución de artículos por ruta de acceso abierto.", "pie"),
    ("articles_by_scienti_category", "Artículos por categoría Scienti", "Distribución de artículos por categoría Scienti.", "pie"),
    ("articles_by_scimago_quartile", "Artículos por cuartil Scimago", "Distribución de artículos por cuartil Scimago de su fuente.", "pie"),
    ("articles_by_publishing_institution", "Artículos por institución editora", "Distribución de artículos por institución editora.", "pie"),
    ("products_by_database", "Productos por base de datos", "Productos presentes en cada base de datos y sus intersecciones.", "venn"),
    ("coauthorship_by_country_map", "Coautoría por país", "Mapa de coautoría con otros países.", "map"),
    ("coauthorship_by_colombian_department_map", "Coautoría por departamento de Colombia", "Mapa de coautoría con los departamentos de Colombia.", "map"),
]

# Plot exclusivo de la entidad Person
PERSON_ONLY_PLOTS = [
    ("author_coauthorship_network", "Red de coautoría del autor", "Red de coautoría entre el autor y sus colaboradores más frecuentes.", "network"),
]

RESPONSE_SCHEMAS = {
    "bar": """\
<ResponseField name="plot" type="object[]">
  Lista de puntos del gráfico de barras.
  <Expandable title="propiedades de cada punto">
    <ResponseField name="x" type="string">
      Etiqueta del eje X (año, nombre de categoría, etc.).
    </ResponseField>
    <ResponseField name="y" type="number">
      Valor numérico del eje Y.
    </ResponseField>
  </Expandable>
</ResponseField>""",
    "pie": """\
<ResponseField name="plot" type="object[]">
  Segmentos del gráfico de torta.
  <Expandable title="propiedades de cada segmento">
    <ResponseField name="x" type="string">
      Etiqueta del segmento.
    </ResponseField>
    <ResponseField name="y" type="number">
      Valor numérico del segmento.
    </ResponseField>
  </Expandable>
</ResponseField>""",
    "venn": """\
<ResponseField name="plot" type="object[]">
  Conjuntos del diagrama de Venn. Cada elemento puede representar un conjunto
  individual o la intersección entre varios.
  <Expandable title="propiedades de cada conjunto">
    <ResponseField name="sets" type="string[]">
      Nombres de los conjuntos que forman este elemento.
    </ResponseField>
    <ResponseField name="size" type="number">
      Cantidad de productos en este conjunto o intersección.
    </ResponseField>
    <ResponseField name="label" type="string">
      Etiqueta visible en el diagrama.
    </ResponseField>
  </Expandable>
</ResponseField>""",
    "map": """\
<ResponseField name="plot" type="object[]">
  Países o departamentos con datos de coautoría.
  <Expandable title="propiedades de cada elemento">
    <ResponseField name="id" type="string">
      Código del país (ISO 3166-1 alfa-2) o del departamento.
    </ResponseField>
    <ResponseField name="name" type="string">
      Nombre del país o departamento.
    </ResponseField>
    <ResponseField name="value" type="number">
      Número de productos en coautoría.
    </ResponseField>
  </Expandable>
</ResponseField>""",
    "network": """\
<ResponseField name="plot" type="object">
  Red de coautoría.
  <Expandable title="propiedades">
    <ResponseField name="nodes" type="object[]">
      Nodos de la red (hasta 50, ordenados por grado descendente).
      <Expandable title="propiedades de cada nodo">
        <ResponseField name="id" type="string">Identificador del autor.</ResponseField>
        <ResponseField name="label" type="string">Nombre del autor.</ResponseField>
        <ResponseField name="degree" type="integer">Número de conexiones del nodo.</ResponseField>
        <ResponseField name="size" type="float">Tamaño visual proporcional a su relevancia.</ResponseField>
      </Expandable>
    </ResponseField>
    <ResponseField name="edges" type="object[]">
      Aristas entre nodos incluidos en la respuesta.
      <Expandable title="propiedades de cada arista">
        <ResponseField name="source" type="string">Identificador del nodo origen.</ResponseField>
        <ResponseField name="target" type="string">Identificador del nodo destino.</ResponseField>
        <ResponseField name="coauthorships" type="integer">Productos en coautoría entre ambos autores.</ResponseField>
        <ResponseField name="size" type="float">Grosor visual de la arista.</ResponseField>
      </Expandable>
    </ResponseField>
  </Expandable>
</ResponseField>""",
}


def shrink(value, items=4, text=100):
    if isinstance(value, list):
        return [shrink(v, items, text) for v in value[:items]]
    if isinstance(value, dict):
        return {k: shrink(v, items, text) for k, v in value.items()}
    if isinstance(value, str) and len(value) > text:
        return value[:text] + "…"
    return value


def fetch(plot, person_id):
    url = f"{BASE}/person/{person_id}/research/products"
    try:
        response = requests.get(url, params={"plot": plot}, timeout=180)
        if response.status_code != 200:
            return None
        data = response.json()
        return data if data else None
    except (requests.RequestException, ValueError):
        return None


def page(plot, title, description, kind, examples):
    available = ", ".join(f"`{label}`" for _, label in SAMPLES.values() if label in [v for _, v in SAMPLES.values()])
    tabs = "\n\n".join(
        f"{FENCE}json {label}\n{json.dumps(shrink(data), ensure_ascii=False, indent=2)}\n{FENCE}"
        for label, data in examples.items()
    )
    schema = RESPONSE_SCHEMAS.get(kind, "")
    return f"""---
title: "{title}"
api: "GET https://api.dev.impactu.colav.co/person/{{person_id}}/research/products"
description: "{description}"
sidebarTitle: "{title}"
---

{description} Tipo de gráfico: **{KIND[kind]}**.

## Parámetros

<ParamField path="person_id" type="string" required>
  Identificador del autor.
</ParamField>

<ParamField query="plot" type="string" required>
  Debe ser `{plot}`.
</ParamField>

Acepta además los [filtros de productos](/api-reference/person/get-research-products). No aplican `max`, `page` ni `sort`.

## Respuesta

{schema}

<ResponseExample>
{tabs}
</ResponseExample>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_plots = SIMPLE_PLOTS + PERSON_ONLY_PLOTS
    pages, overview = [], []

    for plot, title, description, kind in all_plots:
        examples = {}
        for person_id, label in SAMPLES.values():
            data = fetch(plot, person_id)
            if data is not None:
                examples[label] = data
            time.sleep(0.3)

        slug = plot.replace("_", "-")
        # No sobreescribir author-coauthorship-network (tiene documentación manual)
        if slug == "author-coauthorship-network":
            print(f"{plot}: omitido (documentación manual)")
            pages.append(f"api-reference/person/plots/{slug}")
            overview.append(f"| [{title}](/api-reference/person/plots/{slug}) | `{plot}` | {KIND[kind]} |")
            continue

        (OUT / f"{slug}.mdx").write_text(page(plot, title, description, kind, examples), encoding="utf-8")
        pages.append(f"api-reference/person/plots/{slug}")
        overview.append(f"| [{title}](/api-reference/person/plots/{slug}) | `{plot}` | {KIND[kind]} |")
        print(f"{plot}: {', '.join(examples) or 'sin datos'}")

    overview_page = f"""---
title: "Indicadores de un autor"
description: "Catálogo de indicadores que devuelve el endpoint de productos de un autor con el parámetro plot."
sidebarTitle: "Catálogo"
---

Con el parámetro `plot`, el endpoint [Productos de un autor](/api-reference/person/get-research-products) devuelve un indicador en lugar de la lista de productos.

```text
GET /person/{{person_id}}/research/products?plot=<indicador>
```

Los indicadores aceptan los mismos filtros que el listado de productos.

| Indicador | Valor de `plot` | Gráfico |
| --- | --- | --- |
{chr(10).join(overview)}
"""
    (OUT / "overview.mdx").write_text(overview_page, encoding="utf-8")
    print("\nPáginas para docs.json:")
    print(json.dumps(["api-reference/person/plots/overview"] + pages, indent=2))


if __name__ == "__main__":
    main()
