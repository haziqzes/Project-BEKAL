"""Reconcile private PDFs after a process crash without discarding uncertain data."""

import re
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, inspect, select

from app.schema import receipts

DELETING = re.compile(r"^\.(.+\.pdf)\.([0-9a-fA-F-]{36})\.deleting$")


def _receipt_folders(root: Path):
    for year in root.iterdir():
        if not year.is_dir() or year.is_symlink():
            continue
        if year.name == "undated":
            yield year
        elif re.fullmatch(r"\d{4}", year.name):
            for month in year.iterdir():
                if month.is_dir() and not month.is_symlink() and re.fullmatch(r"0[1-9]|1[0-2]", month.name):
                    yield month


def recover_private_storage(database_url: str | None, root: Path) -> None:
    """Restore incomplete deletions; quarantine orphaned saves for private review."""
    if not database_url or not root.is_dir():
        return
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            if not inspect(connection).has_table("receipts"):
                return  # Initial startup can precede the documented migration step.
            saved = {row.id: row.original_file_path for row in connection.execute(
                select(receipts.c.id, receipts.c.original_file_path)).all()}
    finally:
        engine.dispose()

    referenced = set(saved.values())
    for folder in _receipt_folders(root):
        for file in folder.iterdir():
            if not file.is_file() or file.is_symlink():
                continue
            match = DELETING.fullmatch(file.name)
            if match:
                original = file.with_name(match.group(1))
                relative = original.relative_to(root).as_posix()
                if saved.get(match.group(2)) == relative:
                    if not original.exists():
                        file.rename(original)
                    else:
                        _quarantine(root, file)
                elif match.group(2) not in saved:
                    file.unlink()  # The database deletion committed; finish its requested file removal.
                else:
                    _quarantine(root, file)
                continue
            if file.suffix.lower() == ".pdf" and file.relative_to(root).as_posix() not in referenced:
                _quarantine(root, file)


def _quarantine(root: Path, file: Path) -> None:
    recovery = root / ".recovery"
    if recovery.is_symlink():
        raise OSError("Private recovery directory cannot be a symlink")
    recovery.mkdir(mode=0o700, exist_ok=True)
    file.rename(recovery / f"{uuid4()}.pdf")
