# Copilot code review instructions

Follow `AGENTS.md` at the repository root for project facts and conventions. Review checklist:

- Keep the code dependency-free (standard library only); flag unjustified third-party imports.
- Flag changes to the parser regex capture groups or the output keys (`time`, `threadName`, `level`, `messages`, `raws`) unless `README.md` and consumers are updated.
- Flag committed logs, `output.json` or `data.json`; they can contain personal data.
- Do not flag the lack of tests or a dependency manifest on unrelated PRs.

Language: all deliverables (commits, PR text, review comments, code comments, docs) are in English; runtime messages are English.
