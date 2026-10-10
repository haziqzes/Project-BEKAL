"""Short-lived receipt candidates; no database or permanent PDF storage."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Candidate:
    id: UUID
    path: Path
    expires_at: datetime


class CandidateStore:
    def __init__(self, directory: Path, ttl: timedelta = timedelta(hours=1)) -> None:
        self.directory = directory
        self.ttl = ttl
        self._candidates: dict[UUID, Candidate] = {}

    def prepare(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Candidates are intentionally discarded after any backend restart.
        for path in self.directory.iterdir():
            if path.is_file() or path.is_symlink():
                path.unlink()
        self._candidates.clear()

    def create(self, pdf: bytes) -> Candidate:
        candidate_id = uuid4()
        path = self.directory / f"{candidate_id}.pdf"
        with path.open("xb") as output:
            output.write(pdf)
        candidate = Candidate(
            id=candidate_id,
            path=path,
            expires_at=datetime.now(timezone.utc) + self.ttl,
        )
        self._candidates[candidate_id] = candidate
        return candidate

    def get(self, candidate_id: UUID) -> Candidate | None:
        candidate = self._candidates.get(candidate_id)
        if candidate is not None and candidate.expires_at <= datetime.now(timezone.utc):
            self.delete(candidate_id)
            return None
        return candidate

    def delete(self, candidate_id: UUID) -> bool:
        candidate = self._candidates.pop(candidate_id, None)
        if candidate is None:
            return False
        candidate.path.unlink(missing_ok=True)
        return True

    def cleanup_expired(self) -> None:
        for candidate_id in list(self._candidates):
            self.get(candidate_id)

    def clear(self) -> None:
        for candidate_id in list(self._candidates):
            self.delete(candidate_id)
