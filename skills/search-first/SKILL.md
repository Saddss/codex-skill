---
name: search-first
description: >-
  Find existing implementations, extension points or maintained dependencies
  when a requested feature needs a reuse-versus-build decision.
license: MIT
metadata:
  author: Affaan Mustafa (Everything Claude Code)
  upstream: https://github.com/affaan-m/everything-claude-code/tree/main/skills/search-first
  adapted_for: Codex global skills (Codex paths + inference-framework triggers)
---

> **Vendored from [everything-claude-code](https://github.com/affaan-m/everything-claude-code) under MIT.** Paths adapted for Codex; inference-framework triggers added.

# Search First — Research Before You Code

Systematizes "search for existing solutions before implementing."

## Trigger

Use when:
- Adding a feature to a **mature framework** (find similar implementations first)
- Starting functionality that likely already exists in-repo or upstream
- A new utility, helper, registry entry or abstraction requires a reuse decision

## Workflow

Identify the unresolved reuse decision, inspect relevant local implementations and tests, and expand to authoritative external sources only when needed. Stop once the available evidence supports the decision and its relevant compatibility checks. Implement only if the task includes implementation.

## Decision Matrix

| Signal | Action |
|--------|--------|
| Exact match in repo or upstream, well-maintained | **Adopt** — use directly |
| Partial match or existing hook/plugin point | **Extend** — thin wrapper at seam |
| Multiple weak matches | **Compose** — combine 2–3 small pieces |
| Nothing suitable | **Build** — custom, but informed by research |

## Step 0: Tool Availability Preflight

Check availability only for channels needed by the current investigation. Report limitations that affect the conclusion; unused channels need no preflight.

| Channel | Check | If missing |
|---------|-------|------------|
| Repository search | `rg` through modules, tests, configs | State only visible files were inspected |
| Framework patterns | Similar features, registries, plugins, custom op hooks | Read adjacent files + tests |
| Package registry | `pip`, `npm`, project lockfile | Web/docs search only |
| GitHub CLI | `gh auth status` | Public web or local git history |
| MCP / docs tools | Available MCP tool list | Official docs / web search |
| Skills | `~/.codex/skills/` | Say no local skill catalog was checked |

## Quick Mode (default for small changes)

Use `rg` to find relevant implementations, call sites and tests. If these establish the supported extension point and expected behavior, proceed. Consult framework documentation when API behavior remains uncertain, or package registries when a dependency choice is genuinely needed. Do not require a package-market or skill-directory search for every small change.

## Full Mode (non-trivial features)

Use parallel exploration for independent questions when delegation is available and authorized; otherwise inspect the relevant areas sequentially:

```
Subagent(prompt="
  Find how [FRAMEWORK] implements [FEATURE] or closest equivalent.
  Return: file paths, extension points, test patterns, recommendation Adopt/Extend/Build.
")
```

Combine with `parallel-exploring` when the codebase is large.

## Mature Framework Checklist

For the requested extension, inspect the relevant items:

- [ ] Checked for an **in-repo reference implementation** of similar scope, when one exists
- [ ] Identified the **public seam** (registry, plugin, model class, runner hook)
- [ ] Checked tests for how the feature is exercised
- [ ] Confirmed change follows **existing file layout and naming**
- [ ] Recorded the reuse decision when its rationale matters to the implementation

## Anti-Patterns

- **Jumping to code** without searching the repo
- **Reinventing framework mechanisms** (custom registry when one exists)
- **Silent skipping** — claiming "nothing found" when search was incomplete
- **Over-customizing** a library until it loses its benefits
- **Dependency bloat** — massive package for one small helper

## Integration

| Phase | Pair with |
|-------|-----------|
| Cross-cutting codebase exploration | `parallel-exploring` |
| Test-first implementation | `tdd` |
| Requested code cleanup | `simplify-code` |
