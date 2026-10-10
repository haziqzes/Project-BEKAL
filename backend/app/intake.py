"""PDF-only temporary intake endpoints for Phase 1."""

from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfReader

from app.candidates import CandidateStore

router = APIRouter(prefix="/api/candidates", tags=["receipt intake"])
MAX_PDF_BYTES = 10 * 1024 * 1024
ACCEPTED_CONTENT_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream"}


def candidate_store(request: Request) -> CandidateStore:
    return request.app.state.candidate_store


@router.post("", status_code=201)
async def upload_candidate(request: Request, file: UploadFile = File(...)) -> dict[str, str]:
    try:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=415, detail="Choose a .pdf file")
        if file.content_type not in ACCEPTED_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="File must have a PDF content type")

        pdf = await file.read(MAX_PDF_BYTES + 1)
        if len(pdf) > MAX_PDF_BYTES:
            raise HTTPException(status_code=413, detail="PDF exceeds the 10 MiB limit")
        if not pdf.startswith(b"%PDF-"):
            raise HTTPException(status_code=422, detail="File is not a valid PDF")
        try:
            reader = PdfReader(BytesIO(pdf))
            if reader.is_encrypted or len(reader.pages) == 0:
                raise ValueError("Encrypted or empty PDF")
        except Exception as exc:
            raise HTTPException(status_code=422, detail="PDF cannot be previewed") from exc

        candidate = candidate_store(request).create(pdf)
        return {
            "id": str(candidate.id),
            "expires_at": candidate.expires_at.isoformat(),
            "preview_url": f"/api/candidates/{candidate.id}/pdf",
        }
    finally:
        await file.close()


@router.get("/{candidate_id}/pdf")
def preview_candidate(candidate_id: UUID, request: Request) -> FileResponse:
    candidate = candidate_store(request).get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found or expired")
    return FileResponse(
        candidate.path,
        media_type="application/pdf",
        filename=f"{candidate.id}.pdf",
        content_disposition_type="inline",
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"},
    )


@router.delete("/{candidate_id}", status_code=204)
def discard_candidate(candidate_id: UUID, request: Request) -> None:
    if not candidate_store(request).delete(candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found or expired")
