# Release checklist

Do not publish before the canonical specification is frozen, native tests and conformance pass, security cases are evidenced, package validation succeeds, and the core `FINAL_AUDIT.md` is complete.

Current readiness evidence: local compileall, six unittest tests, wheel/sdist build, and `pip check` pass with the isolated Python 3.12 runtime. Clean-environment installation, PyPI publisher/name verification, GitHub synchronization, and hosted CI for the corrected core release snapshot remain pending.

Post-CI correction: hosted run `37918784908` exposed that CI ran tests without installing the src-layout project. The workflow now performs a no-dependency editable install before tests; the hosted rerun remains an open release gate.
