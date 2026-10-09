from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from io import BytesIO
import zipfile

from repropack import Manifest, ReproPackError, create_bundle, default_limits, extract_bundle, read_bundle, redact_bytes, redact_manifest_entry, sha256, verify_bundle

CORE = Path(os.environ.get("REPROPACK_CORE", Path(__file__).parents[2] / "repropack-core"))
FIXTURES = CORE / "conformance" / "fixtures"


def fixture(case: str) -> tuple[Manifest, dict[str, bytes]]:
    root = FIXTURES / case
    manifest = Manifest.from_dict(json.loads((root / "manifest.json").read_text(encoding="utf-8")))
    evidence = {entry.path: (root / Path(entry.path)).read_bytes() for entry in manifest.evidence}
    return manifest, evidence


class ReproPackTests(unittest.TestCase):
    def test_valid_fixtures_round_trip_and_verify(self) -> None:
        catalog = json.loads((CORE / "conformance/catalog.json").read_text(encoding="utf-8"))
        for case in catalog["cases"]:
            if case["valid"]:
                manifest, evidence = fixture(case["id"])
                bundle = read_bundle(create_bundle(manifest, evidence))
                verify_bundle(bundle)

    def test_invalid_fixture_categories(self) -> None:
        expected = {"missing-required-field": "invalid-manifest", "invalid-metadata": "invalid-manifest", "corrupted-content": "hash-mismatch", "incorrect-hash": "hash-mismatch", "unsupported-future-version": "unsupported-version", "unsafe-path": "unsafe-path", "oversized-input": "limit-exceeded"}
        for case, category in expected.items():
            with self.subTest(case=case):
                with self.assertRaises(ReproPackError) as raised:
                    if case in {"corrupted-content", "incorrect-hash"}:
                        manifest, evidence = fixture(case); verify_bundle(read_bundle(create_bundle(manifest, evidence)))
                    else:
                        Manifest.from_dict(json.loads((FIXTURES / case / "manifest.json").read_text(encoding="utf-8")))
                actual = "hash-mismatch" if raised.exception.code == "size-mismatch" else raised.exception.code
                self.assertEqual(actual, category)

    def test_redaction_and_metadata(self) -> None:
        result = redact_bytes(b"password=super-secret\n")
        self.assertTrue(result.redacted); self.assertEqual(result.data, b"password=[REDACTED]\n"); self.assertNotIn(b"super-secret", result.data)
        manifest, _ = fixture("minimal-valid")
        result = redact_manifest_entry(manifest, "evidence/message.txt", b"api_key=secret-value\n", "secret")
        self.assertEqual(manifest.evidence[0].size, len(result.data)); self.assertEqual(manifest.evidence[0].sha256, sha256(result.data)); Manifest.from_dict(manifest.to_dict())

    def test_binary_warning(self) -> None:
        result = redact_bytes(b"\x00\xffsecret")
        self.assertEqual(result.data, b"\x00\xffsecret"); self.assertEqual(result.warnings[0].kind, "binary-input-not-scanned")

    def test_changed_content_and_safe_extraction(self) -> None:
        manifest, evidence = fixture("minimal-valid"); bundle = read_bundle(create_bundle(manifest, evidence)); bundle.evidence["evidence/message.txt"] = b"changed content"
        with self.assertRaises(ReproPackError): verify_bundle(bundle)
        bundle = read_bundle(create_bundle(*fixture("minimal-valid")))
        with tempfile.TemporaryDirectory() as directory:
            extract_bundle(bundle, directory)
            self.assertEqual((Path(directory) / "message.txt").read_bytes(), b"ReproPack minimal evidence.\n")
        self.assertEqual(default_limits().max_entry_bytes, 256 * 1024 * 1024)

    def test_malformed_archive_and_limits(self) -> None:
        with self.assertRaises(ReproPackError) as raised:
            read_bundle(b"not a zip")
        self.assertEqual(raised.exception.code, "malformed-archive")
        manifest, evidence = fixture("minimal-valid")
        with self.assertRaises(ReproPackError) as raised:
            read_bundle(create_bundle(manifest, evidence), type(default_limits())(max_manifest_bytes=1))
        self.assertEqual(raised.exception.code, "limit-exceeded")
        stream = BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("evidence/../escape.txt", b"x")
        with self.assertRaises(ReproPackError) as raised:
            read_bundle(stream.getvalue())
        self.assertEqual(raised.exception.code, "unsafe-path")


if __name__ == "__main__": unittest.main()
