import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_JSON = ROOT / "docs.json"


def collect_pages(node) -> list[str]:
    """Extrae todas las rutas de página del árbol de navegación."""
    pages = []
    if isinstance(node, str):
        pages.append(node)
    elif isinstance(node, list):
        for item in node:
            pages.extend(collect_pages(item))
    elif isinstance(node, dict):
        if "pages" in node:
            pages.extend(collect_pages(node["pages"]))
        if "tabs" in node:
            pages.extend(collect_pages(node["tabs"]))
        if "groups" in node:
            pages.extend(collect_pages(node["groups"]))
    return pages


def check_missing_files(pages: list[str]) -> list[str]:
    """Retorna páginas declaradas en docs.json sin archivo .mdx."""
    missing = []
    for page in pages:
        path = ROOT / f"{page}.mdx"
        if not path.exists():
            missing.append(page)
    return missing


def check_orphan_files(pages: list[str]) -> list[str]:
    """Retorna archivos .mdx en api-reference/ que no están en docs.json."""
    declared = set(pages)
    orphans = []
    for mdx in sorted((ROOT / "api-reference").rglob("*.mdx")):
        relative = mdx.relative_to(ROOT).with_suffix("").as_posix()
        if relative not in declared:
            orphans.append(relative)
    return orphans


def collect_groups(node, prefix="") -> set[str]:
    """Extrae los prefijos de grupo del árbol de navegación."""
    groups = set()
    if isinstance(node, dict):
        if "group" in node:
            groups.add(prefix)
        for key in ("tabs", "groups", "pages"):
            if key in node:
                groups |= collect_groups(node[key], prefix)
        if "tab" in node:
            groups |= collect_groups(node.get("groups", []), prefix)
    elif isinstance(node, list):
        for item in node:
            groups |= collect_groups(item, prefix)
    return groups


def check_broken_links(pages: list[str]) -> list[tuple[str, str]]:
    """Retorna pares (archivo, link) donde el link interno no existe."""
    declared = set(pages)
    broken = []
    # Matches: /api-reference/... links in href or markdown
    link_re = re.compile(r'(?:href="|]\()(/api-reference/[^\s")\'>]+)')
    for page in pages:
        path = ROOT / f"{page}.mdx"
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for match in link_re.finditer(content):
            link = match.group(1).rstrip("/")
            # Strip query strings or anchors
            link = re.split(r"[?#]", link)[0]
            # docs.json entries have no leading slash; strip it to compare
            link_key = link.lstrip("/")
            # Accept exact pages and section-level links (prefix of any known page)
            if link_key not in declared and not any(p.startswith(link_key + "/") for p in declared):
                broken.append((page, link))
    return broken


def main():
    data = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    pages = collect_pages(data.get("navigation", data))

    errors = 0

    missing = check_missing_files(pages)
    if missing:
        print(f"\n[ERROR] {len(missing)} página(s) en docs.json sin archivo .mdx:")
        for p in missing:
            print(f"   {p}")
        errors += len(missing)

    orphans = check_orphan_files(pages)
    if orphans:
        print(f"\n[WARN]  {len(orphans)} archivo(s) .mdx no registrados en docs.json:")
        for o in orphans:
            print(f"   {o}")
        # Orphans are warnings, not errors

    broken = check_broken_links(pages)
    if broken:
        print(f"\n[ERROR] {len(broken)} link(s) interno(s) roto(s):")
        for page, link in broken:
            print(f"   {page} -> {link}")
        errors += len(broken)

    if errors == 0:
        total = len(pages)
        print(f"[OK] {total} páginas validadas sin errores.")
    else:
        print(f"\nTotal de errores: {errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()
