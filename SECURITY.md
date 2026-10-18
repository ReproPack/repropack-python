# Security

Treat bundles as hostile input. The current reader rejects traversal, duplicate paths, encrypted entries, unsafe entry types, oversized inputs, malformed metadata, compression-bomb-sized entries, and hash mismatches without executing contents. It reads entries in bounded chunks but still returns bounded buffers; broader archive fuzzing and an external security review remain future work. Do not publish secrets in public reports. See the canonical [security model](https://github.com/ReproPack/repropack-core/blob/main/docs/SECURITY.md).
