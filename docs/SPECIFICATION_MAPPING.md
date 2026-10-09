# Python mapping for ReproPack 0.1

This is an implementation design artifact for Phase 1. It does not claim that the SDK exists.

| Specification concept | Python mapping | Required behavior |
|---|---|---|
| Manifest | `ReproPackManifest` dataclass or validated mapping | Reject unknown ordinary fields; preserve URI-keyed extensions |
| Evidence | `EvidenceEntry` dataclass | Validate integer sizes and configured limits before reading |
| SHA-256 | lowercase `str` validated at the boundary | Recompute bytes; never trust the manifest digest alone |
| Timestamp | UTC RFC 3339 `str` or explicit datetime wrapper | Require `Z` suffix; do not normalize silently |
| Redaction | tagged mapping/dataclass with `status` and optional `reason` | Hash replacement bytes and never retain removed bytes |
| Error categories | custom `ReproPackError` subclasses with stable `code` | Details must be safe to log and must not echo evidence secrets |
| Limits | `ReadLimits` dataclass with explicit byte/count fields | Enforce before extraction and during streaming reads |
| Unknown version | `UnsupportedVersionError` / `unsupported-version` code | Reject before using evidence |
| Safe extraction | destination-root checked `pathlib` operation | Reject links and special files; never execute entries |

The implementation must use native Python and the standard library where practical; it must not invoke or link to Rust. The mapping is ready for Phase 2 after independent review of the canonical specification.
