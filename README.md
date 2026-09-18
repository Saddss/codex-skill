# Codex Skill

Personal Codex skills and global agent instructions.

## Contents

- `AGENTS.md`: the global instructions maintained at `~/.codex/AGENTS.md`.
- `skills/`: 31 personal skills, including their references, scripts, templates, and configuration examples.

The repository contains a snapshot of the local files. Repository edits and installed files are independent; synchronization is explicit.

## Installation

Review `AGENTS.md` and each selected skill before installation. Back up existing local files and reconcile differences before replacing them.

Place the global instructions at `$CODEX_HOME/AGENTS.md` and selected skill directories under `$CODEX_HOME/skills/`. The default Codex home is `~/.codex`. Review machine-specific paths in the instructions when installing on another machine.

Keep each selected skill's supporting files together with its `SKILL.md`. Dependencies and runtime requirements are documented in the individual skills.

## Scope and provenance

System-managed skills, plugin caches, credentials, session history, and runtime artifacts are excluded. Existing upstream attribution and license declarations remain with the individual components.
