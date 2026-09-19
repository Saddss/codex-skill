# Codex Skill

Personal Codex skills and global agent instructions.

## Contents

- `AGENTS.md`: the global instructions maintained at `~/.codex/AGENTS.md`.
- `skills/`: 31 personal skills, including their references, scripts, templates, and configuration examples.
- `scripts/install.sh`: links the two above into a Codex home.

`scripts/install.sh` links the repository into `$CODEX_HOME`, so the installed entries are these files and `git pull` keeps them current.

## Skill invocation

Personal skills require an explicit request or approval for the current task. Each skill includes `agents/openai.yaml` with `policy.allow_implicit_invocation: false`; explicit `$skill-name` invocation remains available. For a particularly suitable skill, explain its concrete benefit and obtain approval before following its workflow. References to other skills do not grant permission to invoke them.

This policy does not disable application-managed system skills or plugin requirements. It also does not grant permission for repository initialization, destructive operations, or external changes.

## Installation

Review `AGENTS.md` and the skills you intend to use before installing them, then link this repository into the Codex home:

```bash
bash scripts/install.sh --dry-run     # report what would change
bash scripts/install.sh               # create the links
```

The script links `AGENTS.md` and each skill directory into `$CODEX_HOME` (default `~/.codex`). Skills are linked one by one, so system-managed skills such as `$CODEX_HOME/skills/.system`, and any other skill you keep there, stay untouched.

Linking is a one-time step. The installed entries are these repository files, so `git pull` in the checkout is the synchronization from then on.

- `--codex-home DIR` chooses another destination.
- An existing copy that matches the repository is replaced by a link; a copy that differs is moved aside to `<name>.bak.<timestamp>` first.
- Links that point into this repository but no longer resolve are removed.

Review machine-specific paths in the instructions when installing on another machine, and keep each skill's supporting files together with its `SKILL.md`. Dependencies and runtime requirements are documented in the individual skills.

## Scope and provenance

System-managed skills, plugin caches, credentials, session history, and runtime artifacts are excluded. Existing upstream attribution and license declarations remain with the individual components.

## Validation

With Python 3 and PyYAML installed, run `python -B tests/test_skill_safety.py -v`.
These checks cover invocation metadata, source syntax, service selectors, report
labels, and actual CLI failure paths. They do not launch GPU services or validate
container lifecycle behavior against a live Docker daemon.
