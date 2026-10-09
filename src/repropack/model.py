from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from typing import Any, Literal

FORMAT = "repropack"
SPEC_VERSION = "0.1"
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$")
_PATH = re.compile(r"^evidence/[A-Za-z0-9._~-]+(?:/[A-Za-z0-9._~-]+)*$")
_MEDIA = re.compile(r"^[a-z0-9!#$%&'*+.^_`|~-]+/[a-z0-9!#$%&'*+.^_`|~-]+$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_KINDS = {"log", "text", "structured", "source", "environment", "test-output", "file"}
_SELECTIONS = {"explicit", "generated", "derived"}
_REASONS = {"secret", "personal-data", "user-requested", "policy"}
RedactionReason = Literal["secret", "personal-data", "user-requested", "policy"]


class ReproPackError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class ReadLimits:
    max_manifest_bytes: int = 1024 * 1024
    max_entries: int = 10_000
    max_entry_bytes: int = 256 * 1024 * 1024
    max_total_bytes: int = 1024 * 1024 * 1024
    max_path_bytes: int = 4096


def default_limits() -> ReadLimits:
    return ReadLimits()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReproPackError("invalid-manifest", f"{label} must be an object")
    return value


def _exact(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ReproPackError("invalid-manifest", f"{label} has unknown field {sorted(unknown)[0]}")


def _required(value: dict[str, Any], keys: tuple[str, ...], label: str) -> None:
    for key in keys:
        if key not in value:
            raise ReproPackError("invalid-manifest", f"{label} missing {key}")


@dataclass
class EvidenceEntry:
    path: str
    kind: str
    media_type: str
    size: int
    sha256: str
    selection: str
    redaction: dict[str, str]

    @classmethod
    def from_dict(cls, value: Any, index: int) -> EvidenceEntry:
        item = _object(value, f"evidence[{index}]")
        _exact(item, {"path", "kind", "media_type", "size", "sha256", "selection", "redaction"}, f"evidence[{index}]")
        _required(item, ("path", "kind", "media_type", "size", "sha256", "selection", "redaction"), f"evidence[{index}]")
        redaction = _object(item["redaction"], f"evidence[{index}].redaction")
        _exact(redaction, {"status", "reason"}, f"evidence[{index}].redaction")
        return cls(item["path"], item["kind"], item["media_type"], item["size"], item["sha256"], item["selection"], redaction)

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "kind": self.kind, "media_type": self.media_type, "size": self.size, "sha256": self.sha256, "selection": self.selection, "redaction": self.redaction}


@dataclass
class Manifest:
    format: str
    spec_version: str
    bundle_id: str
    created_at: str
    capture: dict[str, Any]
    evidence: list[EvidenceEntry]
    incident: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, value: Any, limits: ReadLimits | None = None) -> Manifest:
        limits = limits or default_limits()
        root = _object(value, "manifest")
        _exact(root, {"format", "spec_version", "bundle_id", "created_at", "capture", "incident", "evidence", "extensions"}, "manifest")
        _required(root, ("format", "spec_version", "bundle_id", "created_at", "capture", "evidence"), "manifest")
        if root["format"] != FORMAT: raise ReproPackError("invalid-manifest", "invalid format")
        if root["spec_version"] != SPEC_VERSION: raise ReproPackError("unsupported-version", str(root["spec_version"]))
        if not isinstance(root["bundle_id"], str) or not _UUID.fullmatch(root["bundle_id"]): raise ReproPackError("invalid-manifest", "invalid bundle_id")
        if not isinstance(root["created_at"], str) or not _TIMESTAMP.fullmatch(root["created_at"]): raise ReproPackError("invalid-manifest", "invalid created_at")
        try: datetime.fromisoformat(root["created_at"].replace("Z", "+00:00"))
        except ValueError as error: raise ReproPackError("invalid-manifest", "invalid created_at") from error
        capture = _object(root["capture"], "capture")
        _exact(capture, {"mode", "tool", "actor", "source"}, "capture")
        _required(capture, ("mode", "tool"), "capture")
        if capture["mode"] not in {"explicit", "generated"}: raise ReproPackError("invalid-manifest", "invalid capture mode")
        tool = _object(capture["tool"], "capture.tool")
        _exact(tool, {"name", "version"}, "capture.tool")
        if not isinstance(tool.get("name"), str) or not tool["name"] or not isinstance(tool.get("version"), str) or not tool["version"]: raise ReproPackError("invalid-manifest", "invalid capture tool")
        extensions = root.get("extensions")
        if extensions is not None:
            extensions = _object(extensions, "extensions")
            if any(":" not in key or any(character.isspace() for character in key) for key in extensions): raise ReproPackError("invalid-manifest", "invalid extension")
        if not isinstance(root["evidence"], list) or not root["evidence"]: raise ReproPackError("invalid-manifest", "evidence must not be empty")
        entries = [EvidenceEntry.from_dict(raw, index) for index, raw in enumerate(root["evidence"])]
        paths: set[str] = set(); previous = ""
        for index, entry in enumerate(entries):
            if not isinstance(entry.path, str) or not _PATH.fullmatch(entry.path) or ".." in entry.path.split("/") or entry.path in paths or entry.path <= previous: raise ReproPackError("unsafe-path" if ".." in entry.path.split("/") else "invalid-manifest", f"invalid evidence path at {index}")
            paths.add(entry.path); previous = entry.path
            if entry.kind not in _KINDS or not isinstance(entry.media_type, str) or not _MEDIA.fullmatch(entry.media_type): raise ReproPackError("invalid-manifest", f"invalid evidence metadata at {index}")
            if not isinstance(entry.size, int) or isinstance(entry.size, bool) or entry.size < 0 or entry.size > limits.max_entry_bytes: raise ReproPackError("limit-exceeded", f"evidence size at {index}")
            if not isinstance(entry.sha256, str) or not _DIGEST.fullmatch(entry.sha256): raise ReproPackError("invalid-manifest", f"invalid digest at {index}")
            if entry.selection not in _SELECTIONS: raise ReproPackError("invalid-manifest", f"invalid selection at {index}")
            if entry.redaction.get("status") == "none" and "reason" in entry.redaction or entry.redaction.get("status") == "redacted" and entry.redaction.get("reason") not in _REASONS or entry.redaction.get("status") not in {"none", "redacted"}: raise ReproPackError("invalid-manifest", f"invalid redaction at {index}")
        return cls(root["format"], root["spec_version"], root["bundle_id"], root["created_at"], capture, entries, root.get("incident"), extensions)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"format": self.format, "spec_version": self.spec_version, "bundle_id": self.bundle_id, "created_at": self.created_at, "capture": self.capture, "evidence": [entry.to_dict() for entry in self.evidence]}
        if self.incident is not None: result["incident"] = self.incident
        if self.extensions: result["extensions"] = self.extensions
        return result
