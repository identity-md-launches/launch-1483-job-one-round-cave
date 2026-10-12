#!/usr/bin/env python3
"""Public in-memory fixtures; CLI fixture writes are confined to test/scratch."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import reproduce as R


def variant(data, change=None, reverse=False, comment=b""):
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(out, "w") as dest:
        infos = source.infolist()
        for info in reversed(infos) if reverse else infos:
            payload = source.read(info.filename)
            if change:
                payload = change(info, payload)
            dest.writestr(info, payload)
        dest.comment = comment
    return out.getvalue()


class ReproductionTests(unittest.TestCase):
    def setUp(self):
        self.data = R.WRITER.build({"empty": b"", "sub/界.py": b"print('public fixture')\n"})

    def test_actual_inherited_archive(self):
        self.assertTrue(R.demo()["byte_reproducible"])

    def test_canonical_unicode_empty_and_nested(self):
        r = R.check_bytes(self.data)
        self.assertTrue(r["byte_reproducible"])
        self.assertIsNone(r["first_difference_offset"])
        self.assertEqual(r["archive_sha256"], r["rebuilt_sha256"])

    def assert_noncanonical(self, data):
        r = R.check_bytes(data)
        self.assertTrue(r["verified"])
        self.assertFalse(r["byte_reproducible"])
        self.assertEqual(r["rebuilt_sha256"], R.WRITER.digest(self.data))
        self.assertIsInstance(r["first_difference_offset"], int)
        return r

    def test_entry_order(self):
        self.assert_noncanonical(variant(self.data, reverse=True))

    def test_archive_comment(self):
        self.assert_noncanonical(variant(self.data, comment=b"public metadata"))

    def test_timestamp(self):
        def change(info, payload):
            info.date_time = (2026, 1, 1, 0, 0, 0)
            return payload
        self.assert_noncanonical(variant(self.data, change))

    def test_mode(self):
        def change(info, payload):
            info.external_attr = (0o100755 << 16)
            return payload
        self.assert_noncanonical(variant(self.data, change))

    def test_manifest_serialization(self):
        def change(info, payload):
            if info.filename == "HANDOFF.json":
                obj = json.loads(payload)
                obj["files"].reverse()
                return json.dumps(obj, indent=2, ensure_ascii=False).encode()
            return payload
        self.assert_noncanonical(variant(self.data, change))

    def test_integrity_failure_refused(self):
        def change(info, payload):
            return b"altered" if info.filename == "empty" else payload
        with self.assertRaisesRegex(ValueError, "byte count differs"):
            R.check_bytes(variant(self.data, change))

    def test_digest_and_limits(self):
        self.assertTrue(R.check_bytes(self.data, R.WRITER.digest(self.data))["trusted_digest_matched"])
        with self.assertRaisesRegex(ValueError, "trusted digest"):
            R.check_bytes(self.data, "f" * 64)
        with self.assertRaisesRegex(ValueError, "exactly 64"):
            R.check_bytes(self.data, "bad")
        with self.assertRaisesRegex(ValueError, "archive exceeds"):
            R.check_bytes(self.data, limits=R.INSPECT.Limits(archive_bytes=1))
        with self.assertRaisesRegex(ValueError, "payload exceeds"):
            R.check_bytes(self.data, limits=R.INSPECT.Limits(payload_bytes=1))

    def test_truncated_and_trailing(self):
        for data in (b"not a zip", self.data[:-1], self.data + b"extra"):
            with self.assertRaises(ValueError):
                R.check_bytes(data)

    def test_cli_exits_and_workspace_paths(self):
        root = Path("test/scratch")
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as folder:
            path = Path(folder).resolve().relative_to(Path.cwd()) / "public.zip"
            command = [sys.executable, "-B", "line-2/tools/handoff-reproduce/reproduce.py", "check"]
            for data, status in ((self.data, 0), (variant(self.data, comment=b"x"), 2), (b"bad", 1)):
                path.write_bytes(data)
                result = subprocess.run(command + [str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, status, result.stderr)
                if status == 1:
                    self.assertEqual(result.stdout, "")
                else:
                    self.assertEqual(json.loads(result.stdout)["byte_reproducible"], status == 0)
            path.write_bytes(self.data)
            link = path.with_name("link.zip")
            link.symlink_to(path.name)
            for raw in (str(link), str(path.absolute()), "../outside.zip"):
                result = subprocess.run(command + [raw], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
