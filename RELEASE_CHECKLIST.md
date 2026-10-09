# Release checklist

Do not publish before the canonical specification is frozen, native tests and conformance pass, security cases are evidenced, package validation succeeds, and the core `FINAL_AUDIT.md` is complete.

Target release: `0.1.1`. Pre-audit readiness evidence: local compileall, six baseline unittest tests, wheel/sdist build, and `pip check` pass with the isolated Python 3.12 runtime. The audit branch adds two focused security/schema regressions; its local eight-test suite passes. Hosted run [37925450600](https://github.com/ReproPack/repropack-python/actions/runs/37925450600) passed before the full audit branch. PyPI publisher/name verification and publication approval remain open; hosted CI for `audit/full-repropack-2026-10-09` remains pending.

Post-CI correction: hosted run `37918784908` exposed that CI ran tests without installing the src-layout project. The workflow now performs a no-dependency editable install before tests, verified by run `37919750244`.

## Coordinated publication prerequisites

- [ ] Owner chooses the coordinated version/tag strategy.
- [ ] Approved release tag exists on the exact corrected commit.
- [ ] Wheel and sdist checksums are recorded in the release dossier.
- [ ] Clean-environment installation and metadata review are recorded for the approved artifacts.
- [ ] PyPI publisher, project-name ownership, and publication approval are confirmed.
