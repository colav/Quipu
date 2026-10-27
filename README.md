<div align="center">

# 📚 Quipu

**Documentación de la API de [quyca](https://github.com/colav/quyca), el backend de ImpactU**

[![Documentación](https://img.shields.io/badge/docs-Mintlify-0D9373)](https://quyca.mintlify.site/index)
[![Hecho con Mintlify](https://img.shields.io/badge/hecho%20con-Mintlify-0D9373)](https://mintlify.com)
[![Licencia](https://img.shields.io/badge/licencia-BSD--3--Clause-blue)](#-licencia)

[Ver la documentación](https://quyca.mintlify.site/index) · [Repositorio de quyca](https://github.com/colav/quyca) · [Colav](http://colav.udea.edu.co/)

</div>

---

## ✨ ¿Qué es Quipu?

Quipu reúne la documentación de los endpoints de **quyca**, la API en Python (Flask + Pydantic + MongoDB) que sirve a la plataforma ImpactU de Colav.

Está construida con [Mintlify](https://mintlify.com) y escrita **a mano en MDX**, a partir del código real de quyca y de respuestas reales de la API. Esto es intencional: varios comentarios `apidoc` del código estaban desactualizados (por ejemplo, usaban `limit` en lugar de `max`, o rutas sin el prefijo `/search`), así que la fuente de verdad es el comportamiento actual de la API.

## 🗂️ Cobertura

| Grupo                      | Estado         | Endpoints | Indicadores |
| -------------------------- | -------------- | --------- | ----------- |
| **Search**                 | ✅ Documentado | 10        | —           |
| **Affiliation**            | ✅ Documentado | 9         | 28          |
| **Person**                 | ✅ Documentado | 8         | 16          |
| **Source**                 | ✅ Documentado | 5         | 1           |
| **Work**                   | ✅ Documentado | 3         | —           |
| **Patent**                 | ✅ Documentado | 2         | —           |
| Project (por id)           | ⏳ Pendiente   |           |             |
| APC                        | ⏳ Pendiente   |           |             |
| Completer                  | ⏳ Pendiente   |           |             |
| Usuarios y autenticación   | ⏳ Pendiente   |           |             |
| Submit                     | ⏳ Pendiente   |           |             |
| Sistema (info, ping, docs) | ⏳ Pendiente   |           |             |

### 🔍 Endpoints del grupo Search

| Página                              | Endpoint                                              |
| ----------------------------------- | ----------------------------------------------------- |
| Buscar personas                     | `GET /search/person`                                  |
| Buscar productos                    | `GET /search/works`                                   |
| Filtros disponibles de productos    | `GET /search/works/filters`                           |
| Buscar afiliaciones                 | `GET /search/affiliations/{affiliation_type}`         |
| Filtros disponibles de afiliaciones | `GET /search/affiliations/{affiliation_type}/filters` |
| Buscar fuentes                      | `GET /search/sources`                                 |
| Filtros disponibles de fuentes      | `GET /search/sources/filters`                         |
| Buscar patentes                     | `GET /search/patents`                                 |
| Buscar proyectos                    | `GET /search/projects`                                |
| Buscar entidades geográficas        | `GET /search/geo/{geo_type}`                          |

### 🏛️ Endpoints del grupo Affiliation

| Página                     | Endpoint                                                                         |
| -------------------------- | -------------------------------------------------------------------------------- |
| Obtener una afiliación     | `GET /affiliation/{affiliation_type}/{affiliation_id}`                           |
| Afiliaciones relacionadas  | `GET /affiliation/{affiliation_type}/{affiliation_id}/affiliations`              |
| Productos de investigación | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/products`         |
| Filtros de productos       | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/products/filters` |
| Exportar productos a CSV   | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/products/csv`     |
| Exportar productos a Excel | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/products/excel`   |
| Patentes                   | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/patents`          |
| Proyectos                  | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/projects`         |
| Noticias                   | `GET /affiliation/{affiliation_type}/{affiliation_id}/research/news`             |

El endpoint de productos acepta el parámetro `plot` para devolver uno de los **28 indicadores** del [catálogo de indicadores de afiliación](https://quyca.mintlify.site/api-reference/affiliation/plots/overview).

### 👤 Endpoints del grupo Person

| Página                     | Endpoint                                            |
| -------------------------- | --------------------------------------------------- |
| Obtener un autor           | `GET /person/{person_id}`                           |
| Productos de investigación | `GET /person/{person_id}/research/products`         |
| Filtros de productos       | `GET /person/{person_id}/research/products/filters` |
| Exportar productos a CSV   | `GET /person/{person_id}/research/products/csv`     |
| Exportar productos a Excel | `GET /person/{person_id}/research/products/excel`   |
| Patentes                   | `GET /person/{person_id}/research/patents`          |
| Proyectos                  | `GET /person/{person_id}/research/projects`         |
| Noticias                   | `GET /person/{person_id}/research/news`             |

El endpoint de productos acepta el parámetro `plot` para devolver uno de los **16 indicadores** del [catálogo de indicadores de autores](https://quyca.mintlify.site/api-reference/person/plots/overview).

### 🗞️ Endpoints del grupo Source

| Página                     | Endpoint                                   |
| -------------------------- | ------------------------------------------ |
| Obtener una fuente         | `GET /source/{source_id}`                  |
| Productos de investigación | `GET /source/{source_id}/products`         |
| Filtros de productos       | `GET /source/{source_id}/products/filters` |
| Exportar productos a CSV   | `GET /source/{source_id}/products/csv`     |
| Exportar productos a Excel | `GET /source/{source_id}/products/excel`   |

El CSV y el Excel tienen la misma estructura de columnas que la exportación de afiliación, con la columna adicional `scimago_quartile`.

El endpoint de productos acepta el parámetro `plot` para devolver el **1 indicador** del [catálogo de indicadores de fuentes](https://quyca.mintlify.site/api-reference/source/plots/overview).

### 📄 Endpoints del grupo Work

| Página                 | Endpoint                      |
| ---------------------- | ----------------------------- |
| Obtener un producto    | `GET /work/{work_id}`         |
| Buscar por DOI         | `GET /work?doi=<doi>`         |
| Autores de un producto | `GET /work/{work_id}/authors` |

## 📁 Estructura del repositorio

```
Quipu/
├── docs.json                        # Configuración y navegación de Mintlify
├── index.mdx                        # Página de inicio
├── api-reference/
│   ├── search/                      # Endpoints de búsqueda global
│   ├── affiliation/                 # Endpoints de la entidad Affiliation
│   │   └── plots/                   # 28 indicadores con ?plot=
│   ├── source/                      # Endpoints de la entidad Source (revistas)
│   ├── work/                        # Endpoints de la entidad Work (productos)
│   └── person/                      # Endpoints de la entidad Person (autores)
│       └── plots/                   # 16 indicadores con ?plot=
├── guides/                          # Guías transversales (filtros, paginación…)
├── snippets/                        # Fragmentos MDX reutilizables
│   ├── pagination-params.mdx        # Parámetros max y page
│   ├── meta-response.mdx            # Objeto meta de respuestas paginadas
│   ├── works-filter-params.mdx      # Filtros de productos de investigación
│   └── works-filters-response.mdx  # Estructura de respuesta de los filtros
├── scripts/                         # Scripts de automatización
│   ├── validate_docs.py             # Valida completitud de docs.json
│   ├── generate_plot_pages.py       # Regenera indicadores de Affiliation
│   ├── generate_person_plot_pages.py# Regenera indicadores de Person
│   └── generate_source_plot_pages.py# Regenera indicadores de Source
└── .github/workflows/
    ├── validate-docs.yml            # CI: valida en cada push/PR a main
    └── generate-plots.yml           # Manual: regenera indicadores desde la API
```

Cada carpeta de `api-reference/` corresponde a un blueprint del `router.py` de quyca.

## 🚀 Desarrollo local

**Requisitos:** [Node.js](https://nodejs.org/) y la CLI de Mintlify.

```bash
# Instalar la CLI
npm i -g mint

# Clonar el repositorio
git clone https://github.com/colav/Quipu.git
cd Quipu

# Previsualizar en http://localhost:3000
mint dev
```

Antes de abrir un pull request, revisa que no haya enlaces rotos:

```bash
mint broken-links
```

## ⚙️ Scripts de automatización

### Validación

Verifica que cada página de `docs.json` tenga su `.mdx`, detecta huérfanos y comprueba links internos:

```bash
python -X utf8 scripts/validate_docs.py
```

El workflow `validate-docs.yml` ejecuta este script automáticamente en cada push o PR a `main`.

### Regeneración de indicadores

Los indicadores (`?plot=`) se generan consultando la API desplegada en `api.dev.impactu.colav.co`:

```bash
# Indicadores de Affiliation (28 plots)
python scripts/generate_plot_pages.py

# Indicadores de Person (16 plots)
python scripts/generate_person_plot_pages.py

# Indicadores de Source (1 plot)
python scripts/generate_source_plot_pages.py
```

También puedes disparar la regeneración desde GitHub Actions con el workflow `generate-plots.yml` (pestaña _Actions_ → _Generate plot pages_ → _Run workflow_). Se abre un PR automáticamente con los archivos actualizados.

## ✍️ Cómo documentar un endpoint

1. **Parte del código real.** Toma la ruta del `router.py` (con su `url_prefix`) y el modelo Pydantic de los parámetros (`QueryParams` u otro). No copies el comentario `apidoc` sin verificarlo.
2. **Verifica con la API.** Usa `curl` o el navegador contra `api.dev.impactu.colav.co` para confirmar nombres de campos y estructura real.
3. **Crea la página** en la carpeta del grupo (por ejemplo, `api-reference/search/nuevo.mdx`).
4. **Agrégala a `docs.json`** dentro de su grupo.
5. **Valida** con `python -X utf8 scripts/validate_docs.py`.
6. **Previsualiza** con `mintlify dev` y abre un pull request.

### Plantilla de página

````mdx
---
title: "Buscar algo"
api: "GET https://api.dev.impactu.colav.co/search/algo"
description: "Descripción corta del endpoint."
---

import PaginationParams from "/snippets/pagination-params.mdx";
import MetaResponse from "/snippets/meta-response.mdx";

## Parámetros de consulta

<ParamField query="keywords" type="string">
  Texto de búsqueda.
</ParamField>

<PaginationParams />

## Respuesta

<ResponseField name="data" type="array">
  Lista de resultados.
</ResponseField>

<MetaResponse />

<ResponseExample>
```json 200
{ "data": [], "meta": { "count": 0, "page": 1, "size": 0 } }
```

```json 400
{ "error": "mensaje de error de validación" }
```

</ResponseExample>
````

## 📐 Convenciones

- **URL base:** `https://api.dev.impactu.colav.co`. En quyca, `API_URL_PREFIX` está vacío, así que las rutas son por ejemplo `/search/person`.
- **Paginación:** `max` (1 a 250) y `page`. Se documentan con el snippet `pagination-params`.
- **Ordenamiento:** `sort` con el formato `campo_direccion` (`asc` o `desc`). Los campos válidos dependen de la entidad y se documentan en cada página.
- **Filtros con varios valores:** se separan por coma (por ejemplo, `years=2020,2026`).
- **Fechas:** se expresan en segundos Unix; un `-1` en una fecha final indica vigente.
- **Opciones de los filtros:** cada listado enlaza a su endpoint de filtros disponibles, de donde salen los valores válidos.
- **Ejemplos de respuesta:** recortados y con datos ficticios. No uses nombres, edades, ORCID ni identificadores que correspondan a personas reales. Usa `0000000001`, `0000000002`… para `person_id` y `example-institution-id`, `COL0000000`… para afiliaciones.
- **Idioma:** español.

## 🌐 Publicación

La documentación se despliega con Mintlify:

1. Mintlify está conectado a este repositorio mediante su GitHub App.
2. Cada push a la rama principal redespliega el sitio automáticamente.
3. Los cambios se proponen mediante pull request y se revisan antes de publicarse.

Sitio publicado: https://quyca.mintlify.site/index

## 🤝 Contribuir

```bash
git checkout -b docs/nombre-del-cambio
# ...edita las páginas y previsualiza con mint dev...
git add .
git commit -m "docs: descripción del cambio"
git push -u origin docs/nombre-del-cambio
```

Abre un pull request hacia la rama principal.

## 🔗 Enlaces

- [Documentación publicada](https://quyca.mintlify.site/index)
- [quyca, el backend de ImpactU](https://github.com/colav/quyca)
- [Colav](http://colav.udea.edu.co/)
- [Documentación de Mintlify](https://mintlify.com/docs)

## 📄 Licencia

BSD-3-Clause License
