# Release checklist

Do not publish before the canonical specification is frozen, native tests and conformance pass, security cases are evidenced, package validation succeeds, and the core `FINAL_AUDIT.md` is complete.

Current readiness evidence: local compileall, six unittest tests, wheel/sdist build, and `pip check` pass with the isolated Python 3.12 runtime. Hosted run [37919750244](https://github.com/ReproPack/repropack-python/actions/runs/37919750244) also passed package installation and checks. PyPI publisher/name verification and publication approval remain open.

Post-CI correction: hosted run `37918784908` exposed that CI ran tests without installing the src-layout project. The workflow now performs a no-dependency editable install before tests, verified by run `37919750244`.

## Coordinated publication prerequisites

- [ ] Owner chooses the coordinated version/tag strategy.
- [ ] Approved release tag exists on the exact corrected commit.
- [ ] Wheel and sdist checksums are recorded in the release dossier.
- [ ] Clean-environment installation and metadata review are recorded for the approved artifacts.
- [ ] PyPI publisher, project-name ownership, and publication approval are confirmed.
