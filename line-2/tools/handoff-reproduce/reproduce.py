#!/usr/bin/env python3
"""Check byte-for-byte reproducibility under the original HANDOFF v1 writer."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile


def load(name, relative):
    path = Path.cwd() / relative
    # Dependencies are fixed workspace paths; refuse symlinks in every component.
    current = Path.cwd()
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink():
            raise ValueError("dependency symlinks are not allowed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INSPECT = load("handoff_reproduce_inspector", "line-2/tools/handoff-inspect/inspect_handoff.py")
WRITER = load("handoff_reproduce_writer", "line-2/tools/handoff/handoff.py")


def check_bytes(data, expected=None, limits=None):
    """Validate a bounded immutable snapshot, then rebuild its payload in memory."""
    receipt = INSPECT.inspect_stream(io.BytesIO(data), limits, expected)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = {item["path"]: archive.read(item["path"]) for item in receipt["files"]}
    rebuilt = WRITER.build(files)
    # Also check the writer output against the inspector, independently of equality.
    rebuilt_receipt = INSPECT.inspect_stream(io.BytesIO(rebuilt), limits)
    equal = data == rebuilt
    first = None
    if not equal:
        first = next((i for i, (a, b) in enumerate(zip(data, rebuilt)) if a != b),
                     min(len(data), len(rebuilt)))
    return {"format": "handoff-reproduction-v1", "profile": "original-handoff-v1-writer",
            "verified": True, "byte_reproducible": equal,
            "archive_sha256": receipt["archive_sha256"], "archive_bytes": len(data),
            "rebuilt_sha256": rebuilt_receipt["archive_sha256"], "rebuilt_bytes": len(rebuilt),
            "file_count": receipt["file_count"], "payload_bytes": receipt["payload_bytes"],
            "first_difference_offset": first,
            "trusted_digest_matched": receipt["trusted_digest_matched"]}


def check_path(raw, expected=None):
    # One bounded snapshot avoids reopening a path between verification and rebuild.
    data = WRITER.regular_bytes(WRITER.workspace_path(raw), INSPECT.Limits.archive_bytes)
    return check_bytes(data, expected)


def demo():
    result = check_path("line-2/handoff.zip")
    if not result["byte_reproducible"]:
        raise ValueError("inherited archive no longer reproduces")
    result["demo"] = "actual inherited handoff; no extraction or payload execution"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo")
    check = commands.add_parser("check")
    check.add_argument("archive", help="relative workspace ZIP path")
    check.add_argument("--sha256", help="independently obtained archive SHA-256")
    args = parser.parse_args()
    try:
        result = demo() if args.command == "demo" else check_path(args.archive, args.sha256)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["byte_reproducible"] else 2
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError,
            zipfile.BadZipFile, EOFError, NotImplementedError) as error:
        print("handoff-reproduce: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
