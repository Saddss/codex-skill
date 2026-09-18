---
name: diagnose
description: >-
  Disciplined diagnosis loop for hard bugs and performance regressions.
  Reproduce → minimise → hypothesise → instrument → fix → regression-test.
  Use when user says "diagnose this" / "debug this", reports a bug, says
  something is broken/throwing/failing, describes a performance regression,
  or debugs vLLM / SGLang / TRT-LLM / lmdeploy failures, benchmark regressions,
  or flaky inference runs.
license: MIT
metadata:
  author: Matt Pocock
  upstream: https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnose
  adapted_for: Codex global skills (evidence-driven diagnosis; real dependencies)
---

> **Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) under MIT.** Uses evidence-driven diagnosis and real dependencies. See `LICENSE-MIT-Matt-Pocock.txt`.

# Diagnose

A discipline for hard bugs. Select the phases needed by the available evidence. Diagnosis-only requests authorize investigation and explanation; apply fixes only when requested or included in the task.

When exploring the codebase, use the project's domain glossary to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Phase 1 — Build a feedback loop

Prefer a fast, repeatable check that distinguishes the observed failure from correct behavior. Use existing logs, traces and call sites to choose a relevant check. If reproduction is unavailable, continue safe evidence-based analysis and label conclusions that still need runtime validation.

### Ways to construct one — try them in roughly this order

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Focused harness.** Exercise the actual code path with real required dependencies and isolated resources. Do not use mocks or fabricated dependency responses.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Version comparison.** Compare already available artifacts, logs or isolated installations from known versions. Preserve the current working tree and user changes; do not restore code using Git.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

Record what the check establishes and what remains uncertain.

### Iterate on the loop itself

Treat the loop as a product. Once you have _a_ loop, ask:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps. A 50%-flake bug is debuggable; 1% is not — keep raising the rate until it's debuggable.

### When you genuinely cannot build a loop

State the reproduction limitation and continue with relevant logs, traces, code and configuration. Separate observed facts from hypotheses. Ask for a missing artifact or environment access only when it blocks further meaningful progress. Production instrumentation requires explicit authorization.

## Phase 2 — Reproduce

Run the loop. Watch the bug appear.

Confirm:

- [ ] The loop produces the failure mode the **user** described — not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or, for non-deterministic bugs, reproducible at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

If reproduction is unavailable, retain that limitation when reporting later findings.

## Phase 3 — Hypothesise

Form hypotheses supported by the evidence and test the most discriminating prediction first. Add alternatives when the evidence supports them; no fixed number is required.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe — discard or sharpen it.

Share relevant hypotheses and supporting evidence when useful. Continue authorized checks without requiring approval for each hypothesis.

## Phase 4 — Instrument

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

Use the project's existing logging conventions for authorized instrumentation. Track each temporary edit so it can be removed without changing unrelated user code.

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5 — Fix + regression test

Write the regression test **before the fix** — but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Flag this for the next phase.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

## Phase 6 — Cleanup + post-mortem

For an authorized fix, verify and report:

- [ ] Original repro no longer reproduces when available; otherwise state that this runtime check remains unverified
- [ ] Regression test passes (or absence of seam is documented)
- [ ] Task-added temporary instrumentation removed and the diff checked
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message — so the next debugger learns

Report remaining risks supported by the investigation. Broader architecture work requires a separate request or an explicit part of the current scope.
