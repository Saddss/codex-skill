# Real Dependency Verification

Exercise the actual implementation through its public interfaces. Use real local services, isolated test databases and task-owned files when integration behavior depends on them. Captured production inputs may be replayed through real code only when access and data handling are authorized; state what the replay can verify.

Do not substitute mocks, stubs, fabricated responses or fixed-success outputs for a required dependency. Deterministic input cases and seeded workloads test the real implementation; their expected results must follow the contract and their provenance must be clear.

If a required dependency is unavailable, run the independent checks that remain meaningful and report the unverified integration behavior. Request access only when it is necessary to finish. Never contact production services, send external messages or incur charges merely to satisfy a test.

Keep dependency ownership and cleanup scoped to the current test run. Verify outputs and failure behavior without weakening assertions or changing production behavior to make a test pass.
