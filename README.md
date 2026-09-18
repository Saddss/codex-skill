# Codex Skill

Personal Codex skills and global agent instructions.

## Contents

- `AGENTS.md`: the global instructions maintained at `~/.codex/AGENTS.md`.
- `skills/`: 31 personal skills, including their references, scripts, templates, and configuration examples.

The repository contains a snapshot of the local files. Repository edits and installed files are independent; synchronization is explicit.

## Skill invocation

Personal skills require an explicit request or approval for the current task. Each skill includes `agents/openai.yaml` with `policy.allow_implicit_invocation: false`; explicit `$skill-name` invocation remains available. For a particularly suitable skill, explain its concrete benefit and obtain approval before following its workflow. References to other skills do not grant permission to invoke them.

This policy does not disable application-managed system skills or plugin requirements. It also does not grant permission for repository initialization, destructive operations, or external changes.

## Installation

Review `AGENTS.md` and each selected skill before installation. Back up existing local files and reconcile differences before replacing them.

Place the global instructions at `$CODEX_HOME/AGENTS.md` and selected skill directories under `$CODEX_HOME/skills/`. The default Codex home is `~/.codex`. Review machine-specific paths in the instructions when installing on another machine.

Keep each selected skill's supporting files together with its `SKILL.md`. Dependencies and runtime requirements are documented in the individual skills.

## Scope and provenance

System-managed skills, plugin caches, credentials, session history, and runtime artifacts are excluded. Existing upstream attribution and license declarations remain with the individual components.

## Validation

With Python 3 and PyYAML installed, run `python -B tests/test_skill_safety.py -v`.
These checks cover invocation metadata, source syntax, service selectors, report
labels, and actual CLI failure paths. They do not launch GPU services or validate
container lifecycle behavior against a live Docker daemon.
