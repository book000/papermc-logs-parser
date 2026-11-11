# AGENTS.md

Guidance for AI coding agents and contributors. `CLAUDE.md` imports this file, and `.github/copilot-instructions.md` adds the review checklist.

## Language

- All deliverables are written in **English**: commit messages, PR/Issue titles and bodies, review comments, code comments and docstrings, and documentation (`README.md`, `AGENTS.md`, etc.).
- Exceptions (keep as is): quotations, technical identifiers, generated files, and external source text.
- Runtime messages (logs, errors) are English.
- Do not rewrite Git history to change the language of past commits.

## Overview

`papermc-logs-parser` parses PaperMC (also Spigot/Bukkit) server log files into structured records with `time`, `threadName`, `level`, `messages` and `raws`. Continuation lines (stack traces, multi-line messages) are merged into the preceding entry.

## Commands

```bash
python -m src      # run from the repository root; needs ./config.json
ruff check         # lint (CI)
ruff format --check
pytest             # CI runs it, but no tests exist yet
```

Pure Python 3, standard library only; there is no dependency manifest. Do not introduce a dependency without a clear need.

`config.json` holds `{"path": "..."}`, the log file to parse (default `logs/latest.log`). Outputs go to the working directory: `output.json` (all entries) and `data.json` (cursor `count` / `firstTime` used to print only new entries on the next run).

## Structure

- `src/__init__.py`: `parser(filepath)`, the core parser. Regex `^\[(HH:MM:SS)] \[(thread)/(level)]: ?(message)$`; a non-matching line is appended to the current entry. It exits with an error if the file is missing.
- `src/__main__.py`: `main()`, the CLI entry point. Reads `config.json`, writes `output.json`, maintains `data.json`.
- `.github/workflows/python-ci.yml`: reusable Python CI from `book000/templates` (ruff, pytest).
- `renovate.json`: dependency automation via a shared `book000/templates` preset.

## Conventions

- Keep the regex capture groups and the output keys (`time`, `threadName`, `level`, `messages`, `raws`) stable; downstream JSON consumers rely on them. Update `README.md` when they, the run command, the `config.json` schema or the output files change.
- Verify behavior changes by running `python -m src` against a sample log and inspecting `output.json`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/); branches follow [Conventional Branch](https://conventional-branch.github.io) short form (`feat/...`, `fix/...`).
- Never commit real server logs or `output.json` / `data.json` from private servers; they may contain player names or IP addresses. Never commit secrets. Do not commit to Renovate PRs.
