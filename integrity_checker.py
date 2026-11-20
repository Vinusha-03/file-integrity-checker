#!/usr/bin/env python3
"""
File Integrity Checker
Create and verify a SHA-256 baseline for files in a directory.
"""

import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

MANIFEST_NAME = ".integrity_baseline.json"
CHUNK_SIZE = 1024 * 1024  # Read files in 1 MB chunks


def sha256_file(file_path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes(directory: Path) -> dict[str, str]:
    """Hash regular files recursively, excluding the baseline manifest."""
    hashes = {}
    manifest = (directory / MANIFEST_NAME).resolve()

    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if path.resolve() == manifest:
            continue

        relative_path = path.relative_to(directory).as_posix()
        hashes[relative_path] = sha256_file(path)

    return hashes


def create_baseline(directory: Path) -> None:
    """Save current file hashes as the trusted baseline."""
    hashes = collect_hashes(directory)
    manifest_data = {
        "algorithm": "SHA-256",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": hashes,
    }

    manifest_path = directory / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest_data, indent=2),
        encoding="utf-8",
    )
    print(f"[+] Baseline created: {manifest_path}")
    print(f"[+] Files recorded: {len(hashes)}")


def verify_directory(directory: Path) -> None:
    """Compare current file hashes with the saved baseline."""
    manifest_path = directory / MANIFEST_NAME

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No baseline found. Run 'init' first: {manifest_path}"
        )

    try:
        baseline_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        baseline = baseline_data["files"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ValueError("The baseline file is invalid or corrupted.") from error

    current = collect_hashes(directory)

    added = sorted(current.keys() - baseline.keys())
    deleted = sorted(baseline.keys() - current.keys())
    modified = sorted(
        name for name in current.keys() & baseline.keys()
        if current[name] != baseline[name]
    )

    if not (added or deleted or modified):
        print("[OK] No changes detected. Files match the baseline.")
        return

    print("[!] Changes detected:")
    for name in modified:
        print(f"  [MODIFIED] {name}")
    for name in added:
        print(f"  [ADDED]    {name}")
    for name in deleted:
        print(f"  [DELETED]  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect added, modified, and deleted files using SHA-256."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Create a baseline for a directory."
    )
    init_parser.add_argument("directory", type=Path)

    check_parser = subparsers.add_parser(
        "check", help="Check a directory against its saved baseline."
    )
    check_parser.add_argument("directory", type=Path)

    args = parser.parse_args()
    directory = args.directory.expanduser().resolve()

    if not directory.exists() or not directory.is_dir():
        parser.error(f"Not a valid directory: {directory}")

    try:
        if args.command == "init":
            create_baseline(directory)
        elif args.command == "check":
            verify_directory(directory)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
