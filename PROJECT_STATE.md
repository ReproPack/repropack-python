# Project state

- Current phase: v0.1.1 release preparation
- Phase status: technically validated; publication decisions remain owner-controlled
- Specification implemented: native 0.1 model and standard-library bundle operations; canonical version is 0.1 approved for implementation
- Implementation status: native package, validation, ZIP I/O, redaction, verification, safe extraction, and unittest suite implemented; no package released
- Conformance status: all 12 core fixtures pass in the local suite; hosted interoperability passed on the corrected synchronized commits
- Hosted CI correction: run `37918784908` exposed missing src-layout package installation; the editable-install correction was verified by run [37919750244](https://github.com/ReproPack/repropack-python/actions/runs/37919750244)
- Known environment issue: system Python aliases are disabled; isolated workspace Python 3.12 runtime is used for validation
- Release baseline: synchronized `main` is `075322861dca89ee2497f009778a420373ee47cf`; target is local `v0.1.1`; local annotated `v0.1.0` still targets `bd48963ac6a77a8ed72adf48e036251fe5084712`; no remote tag or GitHub Release exists
- Registry decision: local wheel/sdist exist, but clean-environment installation and publisher/name verification remain required before PyPI publication
- Owner decisions: preserve the old local tag and release `0.1.1`, or explicitly confirm no external consumption and recreate `v0.1.0`; PyPI publication requires owner approval and project-name/publisher confirmation
- Full organization audit: branch `audit/full-repropack-2026-10-09` contains security, schema-validation, CRLF-redaction, and cross-branch CI corrections. Hosted CI passed in [run 37932699454](https://github.com/ReproPack/repropack-python/actions/runs/37932699454); review remains open in [PR #1](https://github.com/ReproPack/repropack-python/pull/1). The canonical report is [AUDIT_REPORT.md](https://github.com/ReproPack/repropack-core/blob/audit/full-repropack-2026-10-09/AUDIT_REPORT.md); publication remains pending.
