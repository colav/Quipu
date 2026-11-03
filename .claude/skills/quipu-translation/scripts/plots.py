"""Write the English indicator pages (api-reference/*/plots/*.mdx) from the Spanish ones.

Usage:
    python plots.py REPO [PAGE...] [--dry-run]

The indicator pages are produced by the generate_*plot_pages.py scripts from one template, so a
phrase dictionary translates them: references/plot_phrases.json (Spanish -> English, longest
first). The three overview.mdx catalogues are translated too. Without PAGE, every plot page is
written. Lines that still look Spanish afterwards are listed: add their phrases to the
dictionary and run again. --dry-run lists them without writing.
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import en_path, load_json, relink, repo

HERE = pathlib.Path(__file__).resolve().parent
SPANISH = re.compile(r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|en|un|una|que|por|con|para|sin|se|es|y|o|Debe|Tipo)\b")
FENCE = re.compile(r"^[ \t>]*```")

ENTITY = {  # Spanish article, Spanish products page title, English article, English products page title
    "affiliation": ("una afiliación", "Productos de una afiliación", "an affiliation", "Affiliation products"),
    "person": ("un autor", "Productos de un autor", "an author", "Author products"),
    "source": ("una fuente", "Productos de una fuente", "a source", "Source products"),
}


def overview_phrases(entity, phrases):
    es_art, es_prod, art, prod = ENTITY[entity]
    rep = {
        f'title: "Indicadores de {es_art}"': f'title: "Indicators of {art}"',
        f'description: "Catálogo de indicadores que devuelve el endpoint de productos de {es_art} con el parámetro plot."':
            f'description: "Catalogue of the indicators returned by the products endpoint of {art} with the plot parameter."',
        'sidebarTitle: "Catálogo"': 'sidebarTitle: "Catalogue"',
        f"Con el parámetro `plot`, el endpoint [{es_prod}]": f"With the `plot` parameter, the [{prod}]",
        "devuelve un indicador en lugar de la lista de productos.": "endpoint returns an indicator instead of the product list.",
        "?plot=<indicador>": "?plot=<indicator>",
        "Los indicadores aceptan los mismos filtros que el listado de productos.": "Indicators accept the same filters as the product list.",
        "| Indicador | Valor de `plot` | Gráfico | Tipos de afiliación con datos |": "| Indicator | `plot` value | Chart | Affiliation types with data |",
        "| Indicador | Valor de `plot` | Gráfico |": "| Indicator | `plot` value | Chart |",
        "| Barras |": "| Bar |", "| Torta |": "| Pie |", "| Mapa |": "| Map |", "| Red |": "| Network |",
        "| Diagrama de Venn |": "| Venn diagram |",
    }
    for k, v in phrases.items():  # indicator titles inside the catalogue's links
        if len(k) > 12 and not k.startswith(("Tipo de gráfico", "```", "<", "#", "|", "Debe")):
            rep.setdefault(f"[{k}]", f"[{v}]")
    return rep


def translate(text, rep):
    for k in sorted(rep, key=len, reverse=True):
        text = text.replace(k, rep[k])
    return text


def leftovers(text):
    inside = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            continue
        bare = re.sub(r"`[^`]*`|\]\([^)]*\)|\w+=\"[^\"]*\"|\"[^\"]*\"(?=\s*[,}\]])", "", line)
        if not inside and not line.startswith("api:") and SPANISH.search(bare):
            yield n, line


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    root, pages = repo(args[0]), args[1:]
    phrases = load_json(HERE.parent / "references/plot_phrases.json")
    files = [root / p for p in pages] or sorted(root.glob("api-reference/*/plots/*.mdx"))
    bad = 0
    for src in files:
        rel = src.relative_to(root)
        rep = overview_phrases(rel.parts[1], phrases) if src.name == "overview.mdx" else phrases
        text = relink(translate(src.read_text(encoding="utf-8"), rep))
        left = list(leftovers(text))
        for n, line in left:
            print(f"{en_path(rel)}:{n}: {line.strip()}")
        bad += len(left)
        if "--dry-run" not in sys.argv:
            out = root / en_path(rel)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
    print(f"{len(files)} plot page(s); {bad} line(s) still look Spanish"
          + (" - add their phrases to references/plot_phrases.json" if bad else ""))


if __name__ == "__main__":
    main()
