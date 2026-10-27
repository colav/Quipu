"""Genera las páginas MDX de los indicadores (plot) de afiliaciones
consultando la API y guardando las respuestas reales como ejemplos."""
import json
import time
from pathlib import Path

import requests

BASE = "https://api.dev.impactu.colav.co"
OUT = Path("api-reference/affiliation/plots")
FENCE = "`" * 3

SAMPLES = {
    "institution": ("03bp5hc83", "Institución"),
    "faculty": ("03bp5hc83_20", "Facultad"),
    "department": ("03bp5hc83_2_21620003_3154", "Departamento"),
    "group": ("COL0001262", "Grupo"),
}

KIND = {"bar": "Barras", "pie": "Torta", "venn": "Diagrama de Venn", "map": "Mapa", "network": "Red"}

RELATIONS = {"faculty": "facultades", "department": "departamentos", "group": "grupos de investigación"}
RELATION_PLOTS = [
    # (prefijo del nombre, sufijos por relación, métrica, tipo de gráfico)
    ("{}_by_product_type", {"faculty": "faculties", "department": "departments", "group": "research_groups"},
     "Cantidad de productos por tipo de producto de las {}", "bar"),
    ("citations_by_{}", {"faculty": "faculty", "department": "department", "group": "research_group"},
     "Distribución de citas entre las {}", "pie"),
    ("apc_expenses_by_{}", {"faculty": "faculty", "department": "department", "group": "group"},
     "Distribución del gasto en APC entre las {}", "pie"),
    ("h_index_by_{}", {"faculty": "faculty", "department": "department", "group": "research_group"},
     "Índice h de las {}", "pie"),
]

# (plot, título, descripción, tipo de gráfico)
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
    ("active_authors_by_sex", "Autores activos por sexo", "Distribución de autores activos por sexo.", "pie"),
    ("active_authors_by_age_range", "Autores activos por rango de edad", "Distribución de autores activos por rango de edad.", "pie"),
    ("articles_by_scienti_category", "Artículos por categoría Scienti", "Distribución de artículos por categoría Scienti.", "pie"),
    ("articles_by_scimago_quartile", "Artículos por cuartil Scimago", "Distribución de artículos por cuartil Scimago de su fuente.", "pie"),
    ("articles_by_publishing_institution", "Artículos por institución editora", "Distribución de artículos por institución editora.", "pie"),
    ("products_by_database", "Productos por base de datos", "Productos presentes en cada base de datos y sus intersecciones.", "venn"),
    ("coauthorship_by_country_map", "Coautoría por país", "Mapa de coautoría con otros países.", "map"),
    ("coauthorship_by_colombian_department_map", "Coautoría por departamento de Colombia", "Mapa de coautoría con los departamentos de Colombia.", "map"),
    ("institutional_coauthorship_network", "Red de coautoría institucional", "Red de coautoría entre instituciones.", "network"),
]


def build_catalog():
    catalog = []
    for template, names, description, kind in RELATION_PLOTS:
        for relation, name in names.items():
            plot = template.format(name)
            title = description.format(RELATIONS[relation])
            catalog.append((plot, title, title + ".", kind))
    catalog += SIMPLE_PLOTS
    return catalog


def shrink(value, items=4, text=100):
    """Recorta listas y textos largos para que los ejemplos sean legibles."""
    if isinstance(value, list):
        return [shrink(v, items, text) for v in value[:items]]
    if isinstance(value, dict):
        return {k: shrink(v, items, text) for k, v in value.items()}
    if isinstance(value, str) and len(value) > text:
        return value[:text] + "…"
    return value


def fetch(plot, affiliation_type, affiliation_id):
    url = f"{BASE}/affiliation/{affiliation_type}/{affiliation_id}/research/products"
    try:
        response = requests.get(url, params={"plot": plot}, timeout=180)
        if response.status_code != 200:
            return None
        data = response.json()
        return data if data else None
    except (requests.RequestException, ValueError):
        return None


def page(plot, title, description, kind, examples):
    available = ", ".join(f"`{t}`" for t in SAMPLES if t in examples) or "ninguno"
    rows = "\n".join(
        f"| `{t}` | {'✅' if t in examples else 'Sin datos'} |" for t in SAMPLES
    )
    tabs = "\n\n".join(
        f"{FENCE}json {SAMPLES[t][1]}\n{json.dumps(shrink(examples[t]), ensure_ascii=False, indent=2)}\n{FENCE}"
        for t in SAMPLES if t in examples
    )
    return f"""---
title: "{title}"
api: "GET https://api.dev.impactu.colav.co/affiliation/{{affiliation_type}}/{{affiliation_id}}/research/products"
description: "{description}"
sidebarTitle: "{title}"
---

{description} Tipo de gráfico: **{KIND[kind]}**.

## Parámetros

<ParamField path="affiliation_type" type="string" required>
  Tipo de afiliación. Este indicador devuelve datos con: {available}.
</ParamField>

<ParamField path="affiliation_id" type="string" required>
  Identificador de la afiliación.
</ParamField>

<ParamField query="plot" type="string" required>
  Debe ser `{plot}`.
</ParamField>

Acepta además los [filtros de productos](/api-reference/affiliation/get-research-products). No aplican `max`, `page` ni `sort`.

## Disponibilidad por tipo de afiliación

| `affiliation_type` | Datos |
| --- | --- |
{rows}

## Respuesta

<ResponseExample>
{tabs}
</ResponseExample>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages, overview = [], []
    for plot, title, description, kind in build_catalog():
        examples = {}
        for affiliation_type, (affiliation_id, _) in SAMPLES.items():
            data = fetch(plot, affiliation_type, affiliation_id)
            if data is not None:
                examples[affiliation_type] = data
            time.sleep(0.3)
        slug = plot.replace("_", "-")
        (OUT / f"{slug}.mdx").write_text(page(plot, title, description, kind, examples), encoding="utf-8")
        pages.append(f"api-reference/affiliation/plots/{slug}")
        types = ", ".join(f"`{t}`" for t in examples) or "—"
        overview.append(f"| [{title}](/api-reference/affiliation/plots/{slug}) | `{plot}` | {KIND[kind]} | {types} |")
        print(f"{plot}: {', '.join(examples) or 'sin datos'}")

    overview_page = f"""---
title: "Indicadores de una afiliación"
description: "Catálogo de indicadores que devuelve el endpoint de productos de una afiliación con el parámetro plot."
sidebarTitle: "Catálogo"
---

Con el parámetro `plot`, el endpoint [Productos de una afiliación](/api-reference/affiliation/get-research-products) devuelve un indicador en lugar de la lista de productos.

```text
GET /affiliation/{{affiliation_type}}/{{affiliation_id}}/research/products?plot=<indicador>
```

Los indicadores aceptan los mismos filtros que el listado de productos.

| Indicador | Valor de `plot` | Gráfico | Tipos de afiliación con datos |
| --- | --- | --- | --- |
{chr(10).join(overview)}
"""
    (OUT / "overview.mdx").write_text(overview_page, encoding="utf-8")
    print("\nPáginas para docs.json:")
    print(json.dumps(["api-reference/affiliation/plots/overview"] + pages, indent=2))


if __name__ == "__main__":
    main()