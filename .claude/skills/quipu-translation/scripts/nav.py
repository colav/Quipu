"""Rebuild the English navigation of Quipu's docs.json from the Spanish one.

Usage:
    python nav.py REPO           # show what would change
    python nav.py REPO --write   # rewrite the "en" language in docs.json

The "es" language (first, default) is the source: the "en" entry gets the same tree, with every
page path prefixed by en/ and tab and group names taken from references/nav_names.json. Names
missing from that file are listed and kept in Spanish: add them and run again.
"""
import copy
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import load_json, repo

HERE = pathlib.Path(__file__).resolve().parent


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = repo(args[0] if args else None)
    names = load_json(HERE.parent / "references/nav_names.json")
    docs_path = root / "docs.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    langs = docs.get("navigation", {}).get("languages")
    if not langs:
        raise SystemExit("docs.json has no navigation.languages; add the es and en entries first (see SKILL.md)")
    es = next(x for x in langs if x["language"] == "es")
    missing = set()

    def to_en(node):
        if isinstance(node, str):
            return "en/" + node
        if isinstance(node, list):
            return [to_en(x) for x in node]
        out = {}
        for k, v in node.items():
            if k in ("tab", "group"):
                table = names["tabs" if k == "tab" else "groups"]
                if v not in table:
                    missing.add(f"{k}: {v}")
                out[k] = table.get(v, v)
            elif k in ("language", "default"):
                continue
            else:
                out[k] = to_en(v)
        return out

    new_en = {"language": "en", **to_en(copy.deepcopy({k: v for k, v in es.items() if k != "language"}))}
    old_en = next((x for x in langs if x["language"] == "en"), None)
    if old_en == new_en:
        print("en navigation already matches es")
    else:
        old = set(json.dumps(old_en or {}, ensure_ascii=False, indent=0).splitlines())
        new = json.dumps(new_en, ensure_ascii=False, indent=0).splitlines()
        print("en navigation differs; lines new or changed:")
        for line in new:
            if line not in old:
                print("  +", line)
        if "--write" in sys.argv:
            docs["navigation"]["languages"] = [x for x in langs if x["language"] != "en"] + [new_en]
            docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("docs.json updated")
    for m in sorted(missing):
        print(f"MISSING NAME ({m}): add it to references/nav_names.json")


if __name__ == "__main__":
    main()
