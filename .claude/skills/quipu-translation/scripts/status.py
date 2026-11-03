"""Which English pages of Quipu are missing or out of date with respect to the Spanish ones.

Usage:
    python status.py [REPO] [--diff] [--json]

A Spanish file is OUTDATED when it changed (in a later commit or in the working tree) after the
last commit that touched its English copy. Commits that change both together, such as the
response examples written by generate_examples.py, therefore count as in sync. NEW = no English
copy; ORPHAN = English copy whose Spanish page is gone; UNCOMMITTED = English copy never
committed. EDITED = outdated, but its English copy has uncommitted changes: check them
and commit both pages together to mark the pair as in sync.
--diff prints, for every OUTDATED file, the Spanish diff since that commit: apply the same
changes to the English page.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find common.py when run from anywhere
from common import en_path, english_files, es_path, git, repo, spanish_files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?")
    ap.add_argument("--diff", action="store_true", help="print the Spanish diff of every outdated file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = repo(args.repo)

    status = {"new": [], "outdated": [], "edited": [], "orphan": [], "uncommitted": []}
    since = {}
    for rel in spanish_files(root):
        en = en_path(rel)
        if not (root / en).exists():
            status["new"].append(str(rel))
            continue
        last = git(root, "log", "-1", "--format=%H", "--", str(en)).stdout.strip()
        if not last:
            status["uncommitted"].append(str(rel))
            continue
        # exit code 1 = the Spanish file differs between that commit and the working tree
        if git(root, "diff", "--quiet", last, "--", str(rel), check=False).returncode:
            en_edited = git(root, "status", "--porcelain", "--", str(en)).stdout.strip()
            status["edited" if en_edited else "outdated"].append(str(rel))
            since[str(rel)] = last
    for en in english_files(root):
        if not (root / es_path(en)).exists():
            status["orphan"].append(str(en))

    if args.json:
        print(json.dumps({**status, "since": since}, indent=1))
    else:
        for k, v in status.items():
            print(f"{k.upper()}: {len(v)}")
            for p in v:
                print(f"   {p}" + (f"  (since {since[p][:8]})" if p in since else ""))
    if args.diff:
        for p, c in since.items():
            print(f"\n===== {p}  ->  {en_path(p)}  (Spanish changes since {c[:8]})")
            sys.stdout.write(git(root, "diff", c, "--", p).stdout)


if __name__ == "__main__":
    main()
