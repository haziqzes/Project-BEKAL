from io import BytesIO
from pathlib import Path
from shutil import which

import pypdfium2 as pdfium
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app import extraction
from app.main import app


def text_pdf(*pages: list[str]) -> bytes:
    output = BytesIO()
    document = canvas.Canvas(output, pagesize=(550, 750))
    document.setFont("Helvetica", 18)
    for lines in pages:
        y = 680
        for line in lines:
            document.drawString(45, y, line)
            y -= 36
        document.showPage()
    document.save()
    return output.getvalue()


def scanned_pdf(source: bytes) -> bytes:
    document = pdfium.PdfDocument(source)
    page = document[0]
    bitmap = page.render(scale=2)
    image = bitmap.to_pil().convert("RGB")
    output = BytesIO()
    image.save(output, format="PDF", resolution=144)
    image.close()
    bitmap.close()
    page.close()
    document.close()
    return output.getvalue()


def upload_and_extract(pdf: bytes, tmp_path: Path, monkeypatch) -> dict:
    monkeypatch.setenv("CANDIDATE_STORAGE_DIR", str(tmp_path / "candidates"))
    with TestClient(app) as client:
        upload = client.post("/api/candidates", files={"file": ("synthetic.pdf", pdf, "application/pdf")})
        assert upload.status_code == 201
        candidate_id = upload.json()["id"]
        response = client.post(f"/api/candidates/{candidate_id}/extract")
        assert response.status_code == 200, response.text
        assert response.json()["candidate_id"] == candidate_id
        return response.json()


def test_embedded_text_is_preferred_and_multi_page_is_parsed(tmp_path: Path, monkeypatch) -> None:
    def fail_if_ocr_called(_path: Path) -> str:
        raise AssertionError("OCR must not run when embedded receipt text is usable")

    monkeypatch.setattr(extraction, "ocr_text", fail_if_ocr_called)
    pdf = text_pdf(
        ["FRESH MART", "Date: 10/10/2026", "Receipt No: INV-101", "Payment: Card", "MILK 2 pcs 4.50 9.00"],
        ["BREAD 1 pcs 3.50 3.50", "Subtotal RM 12.50", "Total RM 12.50"],
    )
    result = upload_and_extract(pdf, tmp_path, monkeypatch)
    assert result["extraction_method"] == "embedded_text"
    assert result["extraction_status"] == "extracted"
    assert result["receipt"] == {
        "store_name": "FRESH MART",
        "receipt_date": "2026-10-10",
        "receipt_number": "INV-101",
        "payment_method": "Card",
        "subtotal": 12.5,
        "discount_total": None,
        "tax_total": None,
        "final_total": 12.5,
        "currency": "MYR",
    }
    assert result["items"] == [
        {"display_name": "MILK", "quantity": 2.0, "unit": "pcs", "unit_price": 4.5, "line_total": 9.0},
        {"display_name": "BREAD", "quantity": 1.0, "unit": "pcs", "unit_price": 3.5, "line_total": 3.5},
    ]


@pytest.mark.skipif(which("tesseract") is None, reason="Tesseract is installed in the Docker backend")
def test_scanned_pdf_uses_local_ocr(tmp_path: Path, monkeypatch) -> None:
    pdf = scanned_pdf(text_pdf(["FRESH MART", "Date: 10/10/2026", "MILK 2 pcs 4.50 9.00", "Total RM 9.00"]))
    assert extraction.embedded_text(Path(_write_pdf(tmp_path, pdf))).strip() == ""
    result = upload_and_extract(pdf, tmp_path, monkeypatch)
    assert result["extraction_method"] == "ocr"
    assert result["extraction_status"] == "extracted"
    assert result["receipt"]["final_total"] == 9.0
    assert result["items"][0]["display_name"] == "MILK"


def _write_pdf(tmp_path: Path, pdf: bytes) -> Path:
    path = tmp_path / "scan.pdf"
    path.write_bytes(pdf)
    return path


def test_missing_metadata_and_unparseable_content(tmp_path: Path, monkeypatch) -> None:
    pdf = text_pdf(["SMALL SHOP", "ITEM ONE RM 3.20", "ITEM TWO RM 4.10", "TOTAL RM 7.30"])
    result = upload_and_extract(pdf, tmp_path, monkeypatch)
    assert result["receipt"]["receipt_date"] is None
    assert result["receipt"]["payment_method"] is None
    assert result["items"][0]["line_total"] == 3.2

    blank = text_pdf([""])
    monkeypatch.setattr(extraction, "ocr_text", lambda _path: "unrecognizable content")
    result = upload_and_extract(blank, tmp_path, monkeypatch)
    assert result["extraction_method"] == "ocr"
    assert result["extraction_status"] == "no_data"
    assert result["items"] == []


def test_optional_discount_and_tax_are_parsed_without_inference() -> None:
    receipt, items = extraction.parse_receipt_text(
        "CORNER SHOP\nDate: 10/10/2026\nRICE RM 10.00\nSubtotal RM 10.00\n"
        "Discount RM 1.00\nTax RM 0.54\nGrand Total RM 9.54"
    )
    assert receipt.subtotal == 10.0
    assert receipt.discount_total == 1.0
    assert receipt.tax_total == 0.54
    assert receipt.final_total == 9.54
    assert items[0].display_name == "RICE"
