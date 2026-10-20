# Project state

- Current phase: v0.1.1 GitHub Release and PyPI publication complete
- Phase status: technically validated; publication decisions remain owner-controlled
- Specification implemented: native 0.1 model and standard-library bundle operations; canonical version is 0.1 approved for implementation
- Implementation status: native package, validation, ZIP I/O, redaction, verification, safe extraction, unittest suite, and published distribution verified
- Conformance status: all 12 core fixtures pass in the local suite; hosted interoperability passed on the corrected synchronized commits
- Hosted CI correction: run `37918784908` exposed missing src-layout package installation; the editable-install correction was verified by run [37919750244](https://github.com/ReproPack/repropack-python/actions/runs/37919750244)
- Known environment issue: system Python aliases are disabled; isolated workspace Python 3.12 runtime is used for validation
- Release baseline: synchronized `main` is `3aa2f0ccfc134dfa0c1e0a7986bcd80c387fe893`; remote `v0.1.1` tag and GitHub Release exist; local annotated `v0.1.0` still targets `bd48963ac6a77a8ed72adf48e036251fe5084712`
- Registry decision: wheel/sdist build, isolated installation, and public PyPI publication pass for `repropack==0.1.1`
- Owner decisions: preserve the old local tag and release `0.1.1`, or explicitly confirm no external consumption and recreate `v0.1.0`
- Full organization audit: branch `audit/full-repropack-2026-10-09` contains security, schema-validation, CRLF-redaction, and CI revision-selection corrections. The corrected v0.1.1 snapshot is released on GitHub and PyPI.
