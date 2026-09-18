# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [LANGUAGE.md](LANGUAGE.md) — **module**, **interface**, **seam**, **adapter**.

## Dependency categories

When assessing a candidate for deepening, classify its dependencies. The category determines how the deepened module is tested across its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. Always deepenable — merge the modules and test through the new interface directly. No adapter needed.

### 2. Local runtime

Dependencies that can run locally, such as a database or filesystem. Test against the actual supported implementation in an isolated environment. Preserve relevant production behavior and report requirements that cannot be exercised locally.

### 3. Remote but owned (Ports & Adapters)

Your own services across a network boundary (microservices, internal APIs). Define a **port** (interface) when the boundary warrants one. Test the transport adapter against an actual isolated service instance. Pure domain logic can be tested directly without substituting the service's responses.

Keep the domain logic and transport boundary explicit, and validate both domain behavior and the real service contract.

### 4. Third-party service

Use the provider's supported test environment with the necessary authorization. If it is unavailable, report the integration check as unrun and identify the missing access. Do not invent responses or claim integration coverage from a substitute implementation.

## Seam discipline

- **Justify boundaries by real constraints.** Ownership, external protocols, and independent deployment can justify a port with one adapter. Do not create a test-only adapter to justify an abstraction.
- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation, used by its own tests) as well as the external seam at its interface. Don't expose internal seams through the interface just because tests use them.

## Testing strategy: replace, don't layer

- Retain existing regression coverage until equivalent behavior and edge cases are verified through the new interface. Remove a test only when its assertions are demonstrably redundant or its contract is intentionally changed.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation. If a test has to change when the implementation changes, it's testing past the interface.
