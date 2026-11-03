# Quipu Spanish → English glossary and style

These are the choices made in the first full translation (colav/Quipu#13, 2026-11-03). Keep them so the English pages read as one text.

## Terms

| Spanish | English |
| --- | --- |
| producto, productos de investigación | product, research products |
| autor / persona | author / person (`/search/person` searches "persons") |
| afiliación, institución, facultad, departamento, grupo de investigación | affiliation, institution, faculty, department, research group |
| fuente (revista) | source (journal) |
| fuente de información / de datos (`source`) | information source / data source, or just "by source" |
| entidad geográfica; departamento (de Colombia); ciudad | geographic entity; department; city |
| indicador; catálogo de indicadores | indicator; indicator catalogue |
| Barras / Torta / Mapa / Red / Diagrama de Venn | Bar / Pie / Map / Network / Venn diagram |
| listado | list |
| filtros disponibles | available filters |
| ordenamiento, `campo_direccion` | sorting, `field_direction` |
| paginación | pagination |
| clasificación (Minciencias, grupos) | classification |
| cuartil Scimago | Scimago quartile |
| área de conocimiento | subject area |
| tópico (principal) | (primary) topic |
| acceso abierto; ruta de acceso | open access; access route |
| índice h | h-index (sentence start: H-index) |
| citas | citations |
| orden de firma | signing order |
| recortar la lista | cut the list ("the list is cut") |
| sin dato | without data ("fields without data are left out") |
| vigente | current / still current |
| segundos Unix | Unix seconds |
| sesión, iniciar / cerrar sesión, estado de sesión | session, log in / log out, session status |
| correo (electrónico) | email (address) |
| carga de archivos; reporte de calidad | file upload; quality report |
| talento humano (Staff) | human resources (Staff) |
| obligatorio / recomendado | mandatory / recommended |
| advertencia | warning |
| convocatoria | call |
| regalías | royalties |

## Page titles

Titles name the action or the thing, in sentence case: "Get an affiliation", "Search products", "Affiliation products", "Author product filters", "Export products to CSV", "Product authors", "Find a product by DOI", "Send Staff file", "Validate projects file", "Quality metrics". The English link text to a page must match its English title (the catalogues link "Affiliation products", "Author products", "Source products").

## Keep in Spanish

- Everything inside response examples and other code blocks that is API output: `error` and `msg` messages (`"Token inválido o expirado"`), example data (`"María Ejemplo García"`, `"Grupo de Investigación Ejemplo"`), catalogue values.
- Values in backticks that the API or a file format expects: `impactu_Artículo de revista`, `Investigador Junior`, `Sin cuartil`, `sesion_activa`, the column names of the Staff, CIARP and project files (`codigo_proyecto`, `fecha_inicio`, `desconocido`…), catalogue values (`investigación`, `en ejecución`).
- Proper names: Universidad de Antioquia, Minciencias, CvLAC, GrupLAC, Scienti, DANE, Bogotá, Medellín.

When a Spanish value needs explaining, add the English in parentheses: `"Proyecto de extensión"` (outreach project), `` `"Sin cuartil"` `` (no quartile).

## Style

- Second person, present tense, as the Spanish ("If you don't send `max`…").
- English number format: 1,024; 0.2%; 4.4 MB.
- Anchors change with the heading: `#exportaciones` → `#exports`.
- Keep the MDX structure line for line where possible (same components, same order); wrapped lines may be rewrapped.
