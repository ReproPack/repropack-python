# Contributor backlog

These items are scoped implementation work that can be completed from public repository context.

## Clean wheel-install integration test

Build a wheel, install it into a fresh virtual environment, run the public API smoke test, and run `pip check` in CI.

**Acceptance:** the test does not depend on the source checkout after installation and records the exact distribution version.

**Difficulty:** Small.

## Pytest failure-capture example

Provide an optional example that selects a test report and bounded metadata, creates a bundle, and verifies it before upload.

**Acceptance:** synthetic evidence passes; credentials and unrelated workspace files are excluded; invalid and redacted cases are documented.

**Difficulty:** Small.

## Streaming or chunked verification

Add large-bundle verification without changing the v0.1 wire format or weakening existing limits.

**Acceptance:** hash, size, and path behavior remain compatible; memory behavior is measured or bounded; the security documentation is updated.

**Difficulty:** Large.

## Shared-fixture contribution check

Add a contributor-facing check that reports fixture paths, hashes, expected error categories, and unsafe-path cases clearly.

**Acceptance:** a synthetic fixture fails with an actionable message when its manifest or expected result is inconsistent.

**Difficulty:** Medium.

## Scope boundary

Replay, environment reconstruction, implicit execution, credential capture, and hosted debugging remain outside this implementation backlog.
