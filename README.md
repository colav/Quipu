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

| Grupo | Estado | Contenido |
| --- | --- | --- |
| **Search** | ✅ Documentado | Personas, productos, afiliaciones, fuentes, patentes, proyectos y geografía, además de los endpoints de filtros disponibles |
| Affiliation (por id) | ⏳ Pendiente | |
| Person (por id) | ⏳ Pendiente | |
| Source (por id) | ⏳ Pendiente | |
| Work (por id) | ⏳ Pendiente | |
| Patent y Project (por id) | ⏳ Pendiente | |
| APC | ⏳ Pendiente | |
| Completer | ⏳ Pendiente | |
| Usuarios y autenticación | ⏳ Pendiente | |
| Submit | ⏳ Pendiente | |
| Sistema (info, ping, docs) | ⏳ Pendiente | |

### Endpoints del grupo Search

| Página | Endpoint |
| --- | --- |
| Buscar personas | `GET /search/person` |
| Buscar productos | `GET /search/works` |
| Filtros disponibles de productos | `GET /search/works/filters` |
| Buscar afiliaciones | `GET /search/affiliations/{affiliation_type}` |
| Filtros disponibles de afiliaciones | `GET /search/affiliations/{affiliation_type}/filters` |
| Buscar fuentes | `GET /search/sources` |
| Filtros disponibles de fuentes | `GET /search/sources/filters` |
| Buscar patentes | `GET /search/patents` |
| Buscar proyectos | `GET /search/projects` |
| Buscar entidades geográficas | `GET /search/geo/{geo_type}` |

## 📁 Estructura del repositorio

```
Quipu/
├── docs.json                  # Configuración y navegación de Mintlify
├── index.mdx                  # Página de inicio
├── api-reference/
│   └── search/                # Una página por endpoint
│       ├── persons.mdx
│       ├── works.mdx
│       ├── works-filters.mdx
│       ├── affiliations.mdx
│       ├── affiliations-filters.mdx
│       ├── sources.mdx
│       ├── sources-filters.mdx
│       ├── patents.mdx
│       ├── projects.mdx
│       └── geo.mdx
└── snippets/                  # Fragmentos reutilizables
    ├── pagination-params.mdx  # max y page
    ├── sort-alphabetical.mdx  # sort alfabético (patentes y proyectos)
    └── meta-response.mdx      # Campo meta de las respuestas
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

## ✍️ Cómo documentar un endpoint

1. **Parte del código real.** Toma la ruta del `router.py` (con su `url_prefix`) y el modelo Pydantic de los parámetros (`QueryParams` u otro). No copies el comentario `apidoc` sin verificarlo.
2. **Usa una respuesta real** de la API para armar los campos y el ejemplo.
3. **Crea la página** en la carpeta del grupo (por ejemplo, `api-reference/search/nuevo.mdx`).
4. **Agrégala a `docs.json`** dentro de su grupo.
5. **Previsualiza** con `mint dev` y abre un pull request.

### Plantilla de página

````mdx
---
title: "Buscar algo"
api: "GET https://api.dev.impactu.colav.co/search/algo"
description: "Descripción corta del endpoint."
---

import PaginationParams from '/snippets/pagination-params.mdx';
import MetaResponse from '/snippets/meta-response.mdx';

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
- **Ejemplos de respuesta:** recortados y con datos de personas anonimizados. No publiques nombres, edades ni identificadores reales.
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
