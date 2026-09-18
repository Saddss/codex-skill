---
name: review
description: >-
  Two-axis branch review — Standards (CONTRIBUTING.md, CONTEXT, ADRs) and Spec
  (issue/PRD/plan). Use when the user requests a branch or change review,
  including review before a PR.
license: MIT
metadata:
  author: Matt Pocock
  upstream: https://github.com/mattpocock/skills/tree/main/skills/in-progress/review
  adapted_for: Codex global skills (parallel subagent review; inference triggers)
---

> **Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) under MIT.** Upstream status: in-progress.

# Review

Review diff between `HEAD` and a user-supplied fixed point on **two independent axes**:

- **Standards** — matches documented coding standards?
- **Spec** — matches originating issue / PRD / plan?

Use parallel subagents when available and authorized, or check the two dimensions sequentially. A review-only request does not authorize code edits.

## Process

### 1. Pin the fixed point

Use the user-specified base and include the requested committed or uncommitted changes. Otherwise inspect the current branch and PR metadata to identify a clear base. Ask only when different plausible bases would materially change the review scope.

```bash
git diff <fixed-point>...HEAD
git log <fixed-point>..HEAD --oneline
```

These commands inspect committed changes. For requested working-tree review, also inspect `git diff` and `git diff --cached`, including relevant untracked files. Do not omit requested uncommitted changes or change the working tree to obtain a diff.

### 2. Identify spec source

1. Issue refs in commits (`#123`, `Closes #45`) — fetch via `docs/agents/issue-tracker.md` or `gh issue view`
2. User-provided path (e.g. `docs/plans/*.md`, `.codex/plans/*.md`)
3. `docs/specs/`, `docs/plans/`, `.scratch/` matching branch/feature name
4. If none: use the user's stated requirements. If those are also absent, continue the standards review and report that spec compliance could not be assessed; ask only when a missing requirement blocks a material judgment.

### 3. Identify standards sources

Collect paths — e.g. `CONTRIBUTING.md`, `AGENTS.md`, `CONTEXT.md`, `docs/adr/`, linter configs. Note machine-enforced rules; don't re-check what CI already enforces.

### 4. Parallel sub-agents

When delegating, give each available subagent the corresponding review inputs; otherwise perform these checks directly:

**Standards prompt:** diff command, commit list, standards file list. "Read standards, read diff. Report violations with file+rule citation. Hard vs judgement. Skip tooling-enforced. Under 400 words."

**Spec prompt:** diff command, commit list, spec contents/path. "Read spec, read diff. Report: (a) missing/partial requirements, (b) scope creep, (c) likely wrong implementations. Quote spec lines. Under 400 words."

Skip Spec sub-agent if no spec.

### 5. Aggregate

List actionable findings by severity and file/line, identifying whether each concerns standards or requirements. Attach necessary background to its finding. Report missing evidence and required checks not run; omit introductory and closing summaries.

## Why two axes

- Standards pass, Spec fail → correct style, wrong feature
- Spec pass, Standards fail → right feature, wrong conventions

## Integration

| When | Pair with |
|------|-----------|
| After implementation | Before PR |
| With `simplify-code` | review = correctness; simplify = clarity |
| After `to-issues` | Spec axis uses issue acceptance criteria |
