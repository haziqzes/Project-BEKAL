"""Fail closed on private tracked paths and recognizable credential formats."""

import argparse
import re
import subprocess
import sys


PRIVATE_PARTS = {
    "runtime-data", "data", "private", "uploads", "receipts", "receipt_images",
    "ocr_output", "ocr_cache", "exports", "backups", "snapshots", "user_data",
    "secrets", "credentials", "keys", "logs",
}
PRIVATE_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".sql", ".dump", ".backup",
                    ".log", ".pem", ".key", ".p12", ".pfx"}
TOKEN_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,})"),
    "OpenAI token": re.compile(rb"\bsk-[A-Za-z0-9_-]{32,}"),
    "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def unsafe_path(path: str) -> bool:
    name = path.replace("\\", "/").lower()
    parts = name.split("/")
    filename = parts[-1]
    if any(part in PRIVATE_PARTS for part in parts[:-1]):
        return True
    if filename.startswith(".env") and filename != ".env.example":
        return True
    if any(filename.endswith(suffix) for suffix in PRIVATE_SUFFIXES):
        return True
    if filename.endswith((".pdf", ".csv")) and not name.startswith("examples/synthetic/"):
        return True
    return False


def inspect_blob(path: str, contents: bytes, problems: list[str]) -> None:
    if unsafe_path(path):
        problems.append(f"Private file path: {path}")
    for label, pattern in TOKEN_PATTERNS.items():
        if pattern.search(contents):
            problems.append(f"Possible {label}: {path}")


def scan_staged(problems: list[str]) -> None:
    for raw in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0"):
        if raw:
            path = raw.decode("utf-8", "surrogateescape")
            inspect_blob(path, git("show", f":{path}"), problems)


def scan_history(problems: list[str]) -> None:
    seen: set[tuple[str, str]] = set()
    for raw in git("rev-list", "--objects", "--all").splitlines():
        if b" " not in raw:
            continue
        object_id, raw_path = raw.split(b" ", 1)
        path = raw_path.decode("utf-8", "surrogateescape")
        oid = object_id.decode("ascii")
        if (oid, path) in seen or git("cat-file", "-t", oid).strip() != b"blob":
            continue
        seen.add((oid, path))
        inspect_blob(path, git("cat-file", "-p", oid), problems)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Check files currently staged for commit")
    parser.add_argument("--history", action="store_true", help="Check all committed Git blobs and paths")
    args = parser.parse_args()
    if args.staged == args.history:
        parser.error("Choose exactly one of --staged or --history")
    problems: list[str] = []
    try:
        (scan_staged if args.staged else scan_history)(problems)
    except subprocess.CalledProcessError as exc:
        print(f"Git safety check failed: {exc.cmd}", file=sys.stderr)
        return 2
    if problems:
        for problem in sorted(set(problems)):
            print(problem, file=sys.stderr)
        return 1
    print("Git safety check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
