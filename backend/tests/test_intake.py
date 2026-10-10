from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.candidates import CandidateStore
from app.filenames import future_receipt_filename
from app.intake import MAX_PDF_BYTES
from app.main import app


def sample_pdf() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)
    return output.getvalue()


def test_valid_pdf_is_temporary_and_previewable(tmp_path: Path, monkeypatch) -> None:
    candidate_dir = tmp_path / "candidates"
    monkeypatch.setenv("CANDIDATE_STORAGE_DIR", str(candidate_dir))
    pdf = sample_pdf()

    with TestClient(app) as client:
        response = client.post("/api/candidates", files={"file": ("receipt.pdf", pdf, "application/pdf")})
        assert response.status_code == 201
        candidate_id = UUID(response.json()["id"])
        assert response.json()["preview_url"] == f"/api/candidates/{candidate_id}/pdf"
        assert list(candidate_dir.iterdir()) == [candidate_dir / f"{candidate_id}.pdf"]

        preview = client.get(response.json()["preview_url"])
        assert preview.status_code == 200
        assert preview.content == pdf
        assert preview.headers["content-type"] == "application/pdf"
        assert preview.headers["cache-control"] == "no-store"

        assert client.delete(f"/api/candidates/{candidate_id}").status_code == 204
        assert client.get(response.json()["preview_url"]).status_code == 404
        assert not list(candidate_dir.iterdir())


def test_rejects_non_pdf_and_oversized_files(tmp_path: Path, monkeypatch) -> None:
    candidate_dir = tmp_path / "candidates"
    monkeypatch.setenv("CANDIDATE_STORAGE_DIR", str(candidate_dir))
    with TestClient(app) as client:
        cases = [
            ("receipt.txt", sample_pdf(), "application/pdf", 415),
            ("receipt.pdf", b"not a PDF", "application/pdf", 422),
            ("receipt.pdf", b"%PDF-fake", "application/pdf", 422),
            ("receipt.pdf", sample_pdf(), "text/plain", 415),
            ("receipt.pdf", b"x" * (MAX_PDF_BYTES + 1), "application/pdf", 413),
        ]
        for name, content, content_type, expected in cases:
            response = client.post("/api/candidates", files={"file": (name, content, content_type)})
            assert response.status_code == expected
        assert not list(candidate_dir.iterdir())


def test_candidates_expire_and_restart_discards_files(tmp_path: Path) -> None:
    store = CandidateStore(tmp_path, ttl=timedelta(seconds=-1))
    store.prepare()
    candidate = store.create(sample_pdf())
    assert store.get(candidate.id) is None
    assert not candidate.path.exists()

    store = CandidateStore(tmp_path)
    store.prepare()
    candidate = store.create(sample_pdf())
    assert candidate.path.exists()
    CandidateStore(tmp_path).prepare()
    assert not candidate.path.exists()


def test_future_filename_uses_safe_date_and_store() -> None:
    assert future_receipt_filename(date(2026, 10, 10), "Lotus's / KL") == "2026-10-10_lotus-s-kl.pdf"
    assert future_receipt_filename(date(2026, 10, 10), "../") == "2026-10-10_store.pdf"
