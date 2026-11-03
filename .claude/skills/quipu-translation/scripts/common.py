"""Shared helpers for the Quipu translation scripts (Spanish at the root, English under en/)."""
import json
import pathlib
import re
import subprocess

FENCE = re.compile(r"(^[ \t>]*```[^\n]*\n)(.*?)(^[ \t>]*```[ \t]*$)", re.S | re.M)
MIN_BLOCK_LINES = 12  # JSON blocks longer than this are kept out of the text to translate


def repo(path):
    """The Quipu checkout: PATH, or the current folder, or the repository this skill is installed in."""
    here = pathlib.Path(__file__).resolve()
    # installed as a project skill: REPO/.claude/skills/quipu-translation/scripts/common.py
    candidates = [pathlib.Path(path)] if path else [pathlib.Path.cwd()] + ([here.parents[4]] if len(here.parents) > 4 else [])
    for root in candidates:
        root = root.resolve()
        if (root / "docs.json").exists() and (root / "api-reference").is_dir():
            return root
    raise SystemExit(f"{candidates[0].resolve()} is not a Quipu checkout (no docs.json and api-reference/); "
                     "clone it with: git clone https://github.com/colav/Quipu.git")


def git(root, *args, check=True):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def spanish_files(root):
    """Every Spanish .mdx (pages and snippets), as paths relative to the repo."""
    out = []
    for p in sorted(root.rglob("*.mdx")):
        rel = p.relative_to(root)
        if rel.parts[0] in (".git", ".claude", "en", "node_modules") or rel.parts[:2] == ("snippets", "en"):
            continue
        out.append(rel.as_posix())
    return out


def english_files(root):
    return sorted([p.relative_to(root).as_posix() for p in (root / "en").rglob("*.mdx")]
                  + [p.relative_to(root).as_posix() for p in (root / "snippets" / "en").rglob("*.mdx")])


def posix(rel):
    """A repo-relative path as forward-slash PurePosixPath, also for Windows paths."""
    return pathlib.PurePosixPath(rel.as_posix() if isinstance(rel, pathlib.PurePath) else str(rel).replace("\\", "/"))


def en_path(rel):
    rel = posix(rel)
    if rel.parts[0] == "snippets":
        return pathlib.PurePosixPath("snippets/en", *rel.parts[1:])
    return pathlib.PurePosixPath("en", *rel.parts)


def es_path(rel):
    rel = posix(rel)
    if rel.parts[:2] == ("snippets", "en"):
        return pathlib.PurePosixPath("snippets", *rel.parts[2:])
    return pathlib.PurePosixPath(*rel.parts[1:])


def relink(text):
    """Point internal links and snippet imports of an English page to the English versions."""
    text = re.sub(r'(?<=["(\s])/(api-reference|guides)/', r"/en/\1/", text)
    text = re.sub(r'(?<=["(])/index(?=["#)])', "/en/index", text)
    return text.replace('from "/snippets/', 'from "/snippets/en/').replace("/snippets/en/en/", "/snippets/en/")


def split_blocks(text):
    """Replace the bodies of long JSON code blocks with @@BLOCK n@@ and return (skeleton, bodies)."""
    bodies = []

    def sub(m):
        if m.group(2).count("\n") > MIN_BLOCK_LINES and m.group(1).strip().lstrip("> ").startswith("```json"):
            bodies.append(m.group(2))
            return m.group(1) + f"@@BLOCK {len(bodies) - 1}@@\n" + m.group(3)
        return m.group(0)

    return FENCE.sub(sub, text), bodies


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
