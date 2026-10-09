# Contributing

Read `PROJECT_CONTEXT.md`, the applicable phase in `ROADMAP.md`, and the canonical core specification before changing behavior. The implementation must remain native Python and must not invoke Rust. Changes need tests, security consideration, and truthful state updates.

For cross-repository changes, follow the core [contributor guide](https://github.com/ReproPack/repropack-core/blob/main/CONTRIBUTING.md), [compatibility policy](https://github.com/ReproPack/repropack-core/blob/main/docs/COMPATIBILITY.md), and [fixture contribution guide](https://github.com/ReproPack/repropack-core/blob/main/docs/FIXTURE_CONTRIBUTION.md). Run the Python test and compile commands from the CI workflow for implementation changes.
