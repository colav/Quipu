"""Find Spanish left in the English pages of Quipu, outside code blocks and response examples.

Usage:
    python check.py REPO [PAGE...]

PAGE is an English path (en/..., snippets/en/...); without it every English page is checked.
Each hit is printed as path:line. Proper names (Universidad de Antioquia, Minciencias) and
catalogue values in backticks are expected; translate everything else. It also reports English
pages whose links point to Spanish pages (/api-reference/... instead of /en/api-reference/...) or
import Spanish snippets.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import english_files, repo

SPANISH = re.compile(r"\b(de|del|la|las|los|el|en|un|una|que|por|con|para|sin|se|es|al|su|sus|y|más|según|cada|solo|"
                     r"como|Ver|Ejemplo|Ejemplos|propiedades|Respuesta|Parámetros|Identificador|Nombre|Cantidad|"
                     r"Lista|Tipo|Tipos|Fecha|Número)\b|[ñ¿¡]|ción\b")
FENCE = re.compile(r"^[ \t>]*```")
NAMES = re.compile(r"Universidad de \w+|^\s*de Antioquia\b|Santiago de Cali|Bogotá, D\.C\.")


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    root = repo(args[0])
    pages = args[1:] or [str(p) for p in english_files(root)]
    hits = 0
    for page in pages:
        inside = False
        for n, line in enumerate((root / page).read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                inside = not inside
                continue
            if re.search(r'from "/snippets/(?!en/)|(?:href="|\]\()/(?:api-reference|guides|index)\b', line):
                print(f"{page}:{n}: link or import to a Spanish page: {line.strip()[:150]}")
                hits += 1
            if inside or line.startswith(("import ", "api:")):
                continue
            front = line.startswith(("title:", "description:", "sidebarTitle:"))
            strip = r"`[^`]*`|\]\([^)]*\)|https?://\S+" + ("" if front else r"|\"[^\"]*\"")
            bare = NAMES.sub("", re.sub(strip, "", line))
            if SPANISH.search(bare):
                print(f"{page}:{n}: {line.strip()[:150]}")
                hits += 1
    print(f"{len(pages)} English page(s) checked, {hits} hit(s)")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
