from __future__ import annotations

from dataclasses import dataclass
from .model import Manifest, RedactionReason, ReproPackError, sha256


@dataclass
class RedactionWarning:
    kind: str
    message: str


@dataclass
class RedactionResult:
    data: bytes
    redacted: bool
    warnings: list[RedactionWarning]


def redact_text(value: str) -> RedactionResult:
    output: list[str] = []; warnings: list[RedactionWarning] = []; private_key = False; redacted = False
    for line in value.splitlines(keepends=True):
        if line.endswith("\r\n"):
            content, newline = line[:-2], "\r\n"
        elif line.endswith("\n"):
            content, newline = line[:-1], "\n"
        elif line.endswith("\r"):
            content, newline = line[:-1], "\r"
        else:
            content, newline = line, ""
        if private_key:
            redacted = True
            if "-----END " in content and content.endswith("PRIVATE KEY-----"): private_key = False
            output.append(f"[REDACTED]{newline}"); continue
        if content.startswith("-----BEGIN ") and content.endswith("PRIVATE KEY-----"):
            private_key = True; redacted = True; warnings.append(RedactionWarning("private-key-block", "a private-key block was replaced")); output.append(f"[REDACTED]{newline}"); continue
        lower = content.lower(); bearer = lower.find("bearer ")
        if bearer >= 0:
            redacted = True; warnings.append(RedactionWarning("bearer-token", "a bearer-token value was replaced")); output.append(f"{content[:bearer + 7]}[REDACTED]{newline}"); continue
        separator = next((index for index, character in enumerate(content) if character in ":="), None)
        if separator is not None:
            key = content[:separator].strip().lstrip("-# \t").lower().replace("-", "_")
            if key in {"api_key", "apikey", "access_token", "auth_token", "password", "secret", "private_key", "client_secret", "authorization"}:
                redacted = True; warnings.append(RedactionWarning("secret-assignment", "a secret-like assignment value was replaced")); output.append(f"{content[:separator + 1]}[REDACTED]{newline}"); continue
        output.append(line)
    return RedactionResult("".join(output).encode("utf-8"), redacted, warnings)


def redact_bytes(value: bytes) -> RedactionResult:
    try: text = value.decode("utf-8")
    except UnicodeDecodeError: return RedactionResult(value, False, [RedactionWarning("binary-input-not-scanned", "input is not valid UTF-8; no redaction was attempted")])
    return redact_text(text)


def redact_manifest_entry(manifest: Manifest, path: str, value: bytes, reason: RedactionReason) -> RedactionResult:
    entry = next((candidate for candidate in manifest.evidence if candidate.path == path), None)
    if entry is None: raise ReproPackError("missing-entry", path)
    result = redact_bytes(value)
    if result.redacted:
        entry.size = len(result.data); entry.sha256 = sha256(result.data); entry.redaction = {"status": "redacted", "reason": reason}
    return result
