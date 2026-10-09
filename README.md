# ReproPack Python

Native Python implementation of the language-neutral ReproPack specification. Local Phase 2 is complete: native manifest validation, standard-library ZIP operations, verification, redaction, safe extraction, and canonical fixture tests pass. See [docs/PHASE_2_REVIEW.md](docs/PHASE_2_REVIEW.md).

See the canonical project documentation in [repropack-core](https://github.com/ReproPack/repropack-core), especially its [draft specification](https://github.com/ReproPack/repropack-core/blob/main/docs/SPECIFICATION.md), [architecture](docs/ARCHITECTURE.md), and [roadmap](ROADMAP.md).

For the first end-to-end workflow, see the core [tutorial](https://github.com/ReproPack/repropack-core/blob/main/docs/TUTORIAL.md). The SDK entry points are exported from `repropack`; run `python -m unittest discover -s tests -v` and `python -m build` before integrating.
