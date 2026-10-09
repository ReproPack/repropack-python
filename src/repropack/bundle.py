from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import os
import stat
import zipfile
import zlib
from typing import Mapping

from .model import Manifest, ReadLimits, ReproPackError, default_limits, sha256

MANIFEST_PATH = "manifest.json"
EVIDENCE_PREFIX = "evidence/"


@dataclass
class Bundle:
    manifest: Manifest
    evidence: dict[str, bytes]


def _canonical(value: object) -> object:
    if isinstance(value, list): return [_canonical(item) for item in value]
    if isinstance(value, dict): return {key: _canonical(value[key]) for key in sorted(value)}
    return value


def _manifest_bytes(manifest: Manifest) -> bytes:
    Manifest.from_dict(manifest.to_dict())
    return json.dumps(_canonical(manifest.to_dict()), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _safe_path(name: str, limits: ReadLimits) -> bool:
    return len(name.encode("utf-8")) <= limits.max_path_bytes and (name == MANIFEST_PATH or name.startswith(EVIDENCE_PREFIX)) and "\\" not in name and all(part and part not in {".", ".."} and all(character.isascii() and (character.isalnum() or character in "._-~") for character in part) for part in name.split("/"))


def create_bundle(manifest: Manifest, evidence: Mapping[str, bytes]) -> bytes:
    Manifest.from_dict(manifest.to_dict())
    expected = {entry.path for entry in manifest.evidence}
    if set(evidence) != expected:
        missing = expected - set(evidence); raise ReproPackError("missing-entry" if missing else "unexpected-entry", sorted(missing or (set(evidence) - expected))[0])
    from io import BytesIO
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(MANIFEST_PATH, _manifest_bytes(manifest))
        for path in sorted(evidence):
            if not _safe_path(path, default_limits()): raise ReproPackError("unsafe-path", path)
            archive.writestr(path, evidence[path])
    return stream.getvalue()


def read_bundle(data: bytes, limits: ReadLimits | None = None) -> Bundle:
    limits = limits or default_limits()
    from io import BytesIO
    try: archive = zipfile.ZipFile(BytesIO(data))
    except zipfile.BadZipFile as error: raise ReproPackError("malformed-archive", "invalid ZIP archive") from error
    with archive:
        infos = archive.infolist()
        if len(infos) > limits.max_entries: raise ReproPackError("limit-exceeded", "entry count")
        names: set[str] = set(); evidence: dict[str, bytes] = {}; manifest_bytes: bytes | None = None; total = 0
        for info in infos:
            name = info.filename
            if not _safe_path(name, limits): raise ReproPackError("unsafe-path", name)
            if name in names: raise ReproPackError("duplicate-entry", name)
            names.add(name)
            if info.flag_bits & 1: raise ReproPackError("encrypted-entry", name)
            if info.is_dir() or stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF) or stat.S_ISCHR((info.external_attr >> 16) & 0xFFFF) or stat.S_ISBLK((info.external_attr >> 16) & 0xFFFF) or stat.S_ISFIFO((info.external_attr >> 16) & 0xFFFF): raise ReproPackError("unsupported-entry-type", name)
            if info.file_size > limits.max_entry_bytes: raise ReproPackError("limit-exceeded", name)
            total += info.file_size
            if total > limits.max_total_bytes: raise ReproPackError("limit-exceeded", "total bytes")
            try: content = archive.read(info)
            except (zipfile.BadZipFile, RuntimeError, ValueError, zlib.error, EOFError) as error: raise ReproPackError("malformed-archive", name) from error
            if name == MANIFEST_PATH:
                if len(content) > limits.max_manifest_bytes: raise ReproPackError("limit-exceeded", "manifest bytes")
                manifest_bytes = content
            else: evidence[name] = content
    if manifest_bytes is None: raise ReproPackError("missing-entry", MANIFEST_PATH)
    try: manifest = Manifest.from_dict(json.loads(manifest_bytes.decode("utf-8")), limits)
    except (UnicodeDecodeError, json.JSONDecodeError) as error: raise ReproPackError("invalid-manifest", "manifest JSON") from error
    expected = {entry.path for entry in manifest.evidence}
    if expected - set(evidence): raise ReproPackError("missing-entry", sorted(expected - set(evidence))[0])
    if set(evidence) - expected: raise ReproPackError("unexpected-entry", sorted(set(evidence) - expected)[0])
    return Bundle(manifest, evidence)


def verify_bundle(bundle: Bundle) -> None:
    for entry in bundle.manifest.evidence:
        content = bundle.evidence.get(entry.path)
        if content is None: raise ReproPackError("missing-entry", entry.path)
        if len(content) != entry.size: raise ReproPackError("size-mismatch", entry.path)
        if sha256(content) != entry.sha256: raise ReproPackError("hash-mismatch", entry.path)


def _reject(path: Path) -> None:
    if path.is_symlink() or path.exists() and not path.is_file() and not path.is_dir(): raise ReproPackError("extraction-failed", str(path))


def extract_bundle(bundle: Bundle, destination: str | Path) -> None:
    verify_bundle(bundle); root = Path(destination).resolve(); root.mkdir(parents=True, exist_ok=True); _reject(root)
    for archive_path, content in bundle.evidence.items():
        output = (root / archive_path[len(EVIDENCE_PREFIX):]).resolve()
        try: output.relative_to(root)
        except ValueError as error: raise ReproPackError("unsafe-path", archive_path) from error
        output.parent.mkdir(parents=True, exist_ok=True); current = root
        for component in output.relative_to(root).parts[:-1]: current /= component; _reject(current)
        _reject(output); output.write_bytes(content)
