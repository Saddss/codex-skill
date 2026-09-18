---
name: prototype
description: >-
  Build throwaway prototypes to validate a design before production code.
  Terminal state-machine for routing/cache/overload logic, or UI variants on one
  route. Use when prototyping, sanity-checking a state model, exploring routing
  policies, or saying "prototype this" / "let me play with it".
license: MIT
metadata:
  author: Matt Pocock
  upstream: https://github.com/mattpocock/skills/tree/main/skills/engineering/prototype
  adapted_for: Codex global skills (inference/routing triggers added)
---

> **Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) under MIT.**

# Prototype

**Throwaway code that answers one question.** The question decides the shape.

## Pick a branch

- **Logic / state / routing policy?** → [LOGIC.md](LOGIC.md) — interactive terminal TUI over a pure reducer/state machine
- **Layout / UI?** → [UI.md](UI.md) — multiple variants on one route via `?variant=`

If ambiguous: backend/routing module → LOGIC; page/component → UI. State the assumption at the top.

## Rules (both branches)

1. **Clearly marked throwaway** — name/path says prototype; live near the real module
2. **One command to run** — `python …`, `pnpm …`, Makefile target
3. **No persistence by default** — in-memory unless persistence is the question
4. **Question-scoped verification** — run the prototype and check the behaviors and boundary cases needed to answer the design question; use real dependencies when they are part of that question
5. **Surface state** — print/render full state after every action
6. **Preserve the result** — record the answer and verification evidence; delete or integrate artifacts only within the user's authorized scope

## When done

Deliver the answer, runnable artifact and observed checks. Integration into production code or deletion of the prototype requires authorization for that operation.

## Integration

| Before | After |
|--------|-------|
| Design question or `grill-with-docs` | Validated design |
| Prototype verdict | Implementation plan, or `to-issues` when issue creation is requested |
| Authorized production implementation | Implement and verify; use `tdd` for test-first work |
