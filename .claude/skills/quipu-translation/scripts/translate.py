"""Translate whole Quipu pages without retyping their long JSON examples.

Usage:
    python translate.py skel  REPO WORK PAGE...   # WORK/skel/PAGE: Spanish text, long JSON bodies as @@BLOCK n@@
    python translate.py build REPO WORK PAGE...   # WORK/en/PAGE (your translation) -> REPO/en/PAGE

PAGE is the Spanish path relative to the repo (api-reference/work/get-work.mdx, snippets/view-param.mdx).
Write the English version of each skeleton to WORK/en/PAGE, keeping every @@BLOCK n@@ line where it
is. build puts the original JSON bodies back, points links to /en/... and snippet imports to
/snippets/en/..., and writes en/PAGE (snippets go to snippets/en/).
"""
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import en_path, relink, repo, split_blocks


def main():
    if len(sys.argv) < 5 or sys.argv[1] not in ("skel", "build"):
        raise SystemExit(__doc__)
    cmd, root, work, pages = sys.argv[1], repo(sys.argv[2]), pathlib.Path(sys.argv[3]), sys.argv[4:]
    for page in pages:
        src = root / page
        if not src.exists():
            raise SystemExit(f"{src} does not exist")
        skeleton, bodies = split_blocks(src.read_text(encoding="utf-8"))
        if cmd == "skel":
            out = work / "skel" / page
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(skeleton, encoding="utf-8")
            print(f"{out}  ({len(bodies)} JSON blocks kept out)")
            continue
        tr = work / "en" / page
        if not tr.exists():
            raise SystemExit(f"{tr} missing: translate WORK/skel/{page} into it first")
        text = tr.read_text(encoding="utf-8")
        found = sorted(int(n) for n in __import__("re").findall(r"@@BLOCK (\d+)@@", text))
        if found != list(range(len(bodies))):
            raise SystemExit(f"{tr}: placeholders {found} do not match the {len(bodies)} JSON blocks of {page}")
        for i, body in enumerate(bodies):
            text = text.replace(f"@@BLOCK {i}@@\n", body, 1)
        out = root / en_path(page)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(relink(text), encoding="utf-8")
        print(f"wrote {en_path(page)}")


if __name__ == "__main__":
    main()
