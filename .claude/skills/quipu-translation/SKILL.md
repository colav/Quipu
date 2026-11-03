---
name: quipu-translation
description: Keep the English version of the ImpactU API documentation (the colav/Quipu Mintlify repository, published at help.impactu.colav.co) in step with the Spanish one - find Spanish pages that are new, changed or deleted since their English copy was last committed, translate them into en/ (pages) and snippets/en/ (snippets), regenerate the English indicator pages, sync the "en" navigation of docs.json, copy response examples, check for leftover Spanish and broken links, and open a PR. Use whenever the user says the Spanish Quipu/ImpactU docs changed, asks to update, sync, refresh or check the English translation, to translate a new Quipu page, or whether the English docs are up to date - also after a PR that edited Spanish pages, or after generate_plot_pages.py / generate_examples.py changed them.
---

# Updating Quipu's English translation

Quipu (https://github.com/colav/Quipu) is the Mintlify source of https://help.impactu.colav.co. Spanish is the default language at the root (`index.mdx`, `guides/`, `api-reference/`, `snippets/`). English mirrors it with the same paths under `en/` (pages) and `snippets/en/` (snippets), and `docs.json` has `navigation.languages` with `es` first and `en` second. The English version was added in colav/Quipu#13 (November 2026).

**Sync rule.** An English page is in sync when its last commit is newer than every change to its Spanish page. Always commit an English page together with, or after, the Spanish change it reflects; never commit an English page you haven't updated, or the change it missed will be hidden.

## Requirements

- `git` and Python 3.8 or newer. The scripts use only the standard library; on Windows call them with `python` or `py` instead of `python3`.
- Optional: `gh` (the GitHub CLI) to fork and open the pull request, and Node.js 18 or newer for Mintlify's checks (`npx mint ...`). Without `gh`, push with `git` and open the pull request on github.com. Without Node, skip the Mintlify checks and say so in the pull request.

## Paths used below

- **`S`:** the `scripts/` folder next to this SKILL.md. The skill lives in the Quipu repository at `.claude/skills/quipu-translation/`, so from a clone `S` is `REPO/.claude/skills/quipu-translation/scripts`.
- **`REPO`:** the Quipu clone. Every script takes it as its first argument. Run from inside the clone you can pass `.`; the scripts also find the repository they are installed in.
- **`W`:** a temporary work folder outside the repository: the session's scratchpad if there is one, otherwise `mktemp -d` (on Windows, a folder under `%TEMP%`).
- **Dictionaries** in `references/`: `plot_phrases.json` (indicator pages), `nav_names.json` (tab and group names) and `example_titles.json` (example titles).
- **Glossary and style:** `references/glossary.md`. Read it before translating.

## Workflow

1. **Get an up-to-date clone and a branch.**
   - If the user is already in a Quipu clone (it has `docs.json` and `api-reference/`), use it. Check `git status` first: don't mix the user's uncommitted work into the translation.
   - If there is no clone, ask where to put one, then clone it:
     - with push rights to colav/Quipu: `gh repo clone colav/Quipu` or `git clone https://github.com/colav/Quipu.git`;
     - without them: fork it with `gh repo fork colav/Quipu --clone`, or fork on github.com and clone the fork.

     Check access with `gh repo view colav/Quipu --json viewerPermission`: `WRITE`, `MAINTAIN` or `ADMIN` can push branches.
   - Then update `main` and branch from it. `upstream` is colav/Quipu in a fork, `origin` otherwise:

     ```bash
     git checkout main && git pull upstream main
     git checkout -b docs/en-sync-YYYY-MM-DD
     ```

   If a translation branch is still open, ask whether to continue it.

2. **See what is out of date:** `python3 S/status.py REPO --diff`. It lists:
   - **NEW:** Spanish pages or snippets without an English copy.
   - **OUTDATED:** Spanish files changed since their English copy's last commit, each with the Spanish diff.
   - **EDITED:** outdated, but the English copy already has uncommitted changes.
   - **ORPHAN:** English copies whose Spanish page was deleted or moved.
   - **UNCOMMITTED:** English copies never committed.

   Then run `python3 S/nav.py REPO` to compare the English navigation with the Spanish one.

   It needs the full git history. In a shallow clone (`--depth`), run `git fetch --unshallow` first.

3. **Outdated pages: apply the Spanish diff to the English page.** Read the diff and make the matching edit in `en/...`. Translate only what changed; don't retranslate the page. Handle the special cases this way:
   - **Response examples only** (new JSON, a renamed example): `python3 S/examples.py REPO PAGE...` copies the Spanish `<ResponseExample>` block and translates its titles. Add unknown titles to `example_titles.json`.
   - **Indicator pages** (`api-reference/*/plots/*.mdx`, including the three `overview.mdx` catalogues): run `python3 S/plots.py REPO [PAGE...]` instead of editing by hand. For every line it reports as still Spanish, add the phrase to `plot_phrases.json` and rerun. The `generate_*plot_pages.py` scripts write only the Spanish pages, so run this after every indicator regeneration.
   - **A heavily rewritten page:** treat it as new.

4. **New pages and snippets: translate the whole file.** `PAGE` is the Spanish path, such as `api-reference/work/get-work.mdx` or `snippets/view-param.mdx`.
   - `python3 S/translate.py skel REPO W PAGE...` writes `W/skel/PAGE`. Long JSON example bodies are replaced by `@@BLOCK n@@` lines, so you don't retype them.
   - Write the English text to `W/en/PAGE` and keep each `@@BLOCK n@@` line in place.
   - `python3 S/translate.py build REPO W PAGE...` restores the JSON, points links to `/en/...` and snippet imports to `/snippets/en/...`, and writes `en/PAGE` (or `snippets/en/...`).

   Translate frontmatter `title`, `description` and `sidebarTitle`; prose; component titles (`<Expandable title="properties">`, `<Accordion title=...>`); table text; example titles; comments and printed strings in code samples. Keep API output and catalogue values as they are (see the glossary).

5. **Orphans.** If the Spanish page was renamed (check `git log --follow`), `git mv` the English one to match. If it was deleted, delete the English copy too.

6. **Navigation:** `python3 S/nav.py REPO --write` rebuilds the `en` entry of `docs.json` from `es`: same tree, `en/` prefixes, translated names. Add any reported missing tab or group name to `nav_names.json` and rerun. It never touches the `es` entry.

7. **Check:**
   - `python3 S/check.py REPO` lists Spanish left outside code blocks, and links or imports that point to Spanish pages. Expected leftovers are proper names and values in backticks; fix the rest.
   - `python3 -X utf8 REPO/scripts/validate_docs.py` must print `[OK] N páginas validadas sin errores.`, where N is twice the Spanish page count. It warns about Spanish pages without an English copy.
   - From REPO, if Node is available: `npx --yes mint@latest broken-links` (no broken links) and `npx --yes mint@latest validate` (build and validation passed). Ignore the CLI's sign-up and login suggestions.
   - `python3 S/status.py REPO` should show only EDITED or UNCOMMITTED entries for what you just changed.

8. **Commit and open a pull request.**
   - Stage the English pages, `docs.json` and any dictionary changes. Commit with a message such as `docs(en): sync English pages with <what changed>`, listing the pages.
   - Ask before pushing if the user didn't ask for a pull request. Then push the branch: `git push -u origin HEAD`, which pushes to the fork in a fork.
   - Open the pull request against `colav/Quipu`'s `main`: `gh pr create --repo colav/Quipu --base main` (from a fork, gh fills in `--head <user>:<branch>`). Without `gh`, open it from the link that `git push` prints.
   - In the pull request body, list the pages translated, updated, moved or deleted, and the checks run (or skipped).

   Once the pull request is merged, `status.py` reports everything in sync.

## Notes

- **Spanish typos.** The Spanish source sometimes has small errors, such as "las departamentos" in indicator titles. Translate the meaning; fix the Spanish only if asked, and in its own commit.
- **The validator and the example generator know about `en/`.** `generate_examples.py` already updates the English pages, translating the example titles with its own `VARIANTS_EN`. If you add a title to `example_titles.json` that the generator also produces, add it to `VARIANTS_EN` in `scripts/generate_examples.py` too.
- **Snippets are shared by many pages.** A changed Spanish snippet affects every page that imports it; its English copy is all you need to update.
- **Large batches of new pages:** translate them file by file with `translate.py` to keep each translation reviewable.
- **The skill itself.** The skill is versioned in the repository. When you improve a script or a dictionary, commit it with the translation, so the next user gets the change.
