# Release checklist

Do not publish before the canonical specification is frozen, native tests and conformance pass, security cases are evidenced, package validation succeeds, and the core `FINAL_AUDIT.md` is complete.

Target release: `0.1.1`. Local compileall, security tests, wheel/sdist build, isolated installation, and hosted CI pass. The v0.1.1 GitHub Release and PyPI package are published with checksum-verified wheel and sdist assets.

Post-CI correction: hosted run `37918784908` exposed that CI ran tests without installing the src-layout project. The workflow now performs a no-dependency editable install before tests, verified by run `37919750244`.

## Coordinated publication prerequisites

- [x] Owner chose the coordinated 0.1.1 strategy while preserving historical v0.1.0.
- [x] Approved `v0.1.1` tag exists on the exact corrected commit.
- [x] Wheel and sdist checksums are attached to the GitHub Release.
- [x] Clean-environment installation and metadata review are recorded for the approved artifacts.
- [x] PyPI publisher and project-name ownership are confirmed by successful publication of `repropack==0.1.1`.
