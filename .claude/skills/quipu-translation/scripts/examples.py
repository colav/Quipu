"""Copy the <ResponseExample> blocks of Spanish Quipu pages into their English copies.

Usage:
    python examples.py REPO PAGE... [--dry-run]

Response examples are API output, so both languages carry the same JSON; only the title after the
status code is translated (`json 200 — Institución` -> `json 200 — Institution`) with
references/example_titles.json. Use it when a Spanish page's examples changed by hand or in a
commit that did not touch the English page. Unknown titles are listed and kept in Spanish.
"""
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import en_path, load_json, repo

HERE = pathlib.Path(__file__).resolve().parent
EXAMPLE = re.compile(r"<ResponseExample>\n.*?</ResponseExample>", re.S)
TITLE = re.compile(r"^(```\w+ \d{3}) — (.+)$", re.M)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    root, pages = repo(args[0]), args[1:]
    titles = load_json(HERE.parent / "references/example_titles.json")
    for page in pages:
        es = (root / page).read_text(encoding="utf-8")
        en_file = root / en_path(page)
        en = en_file.read_text(encoding="utf-8")
        src, dst = EXAMPLE.search(es), EXAMPLE.search(en)
        if not src or not dst:
            print(f"{page}: no <ResponseExample> in {'Spanish' if not src else 'English'} page, skipped")
            continue

        def title(m):
            if m.group(2) not in titles:
                print(f"{page}: unknown example title '{m.group(2)}': add it to references/example_titles.json")
            return f"{m.group(1)} — {titles.get(m.group(2), m.group(2))}"

        block = TITLE.sub(title, src.group(0))
        new = en[: dst.start()] + block + en[dst.end():]
        state = "unchanged" if new == en else "updated"
        if new != en and "--dry-run" not in sys.argv:
            en_file.write_text(new, encoding="utf-8")
        print(f"{en_path(page)}: {state}")


if __name__ == "__main__":
    main()
