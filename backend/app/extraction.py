"""Temporary receipt extraction: embedded text first, local OCR when needed."""

import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal

import pypdfium2 as pdfium
import pytesseract
from pydantic import BaseModel
from pypdf import PdfReader


class ReceiptData(BaseModel):
    store_name: str | None = None
    receipt_date: str | None = None
    receipt_number: str | None = None
    payment_method: str | None = None
    subtotal: float | None = None
    discount_total: float | None = None
    tax_total: float | None = None
    final_total: float | None = None
    currency: Literal["MYR"] = "MYR"


class ItemData(BaseModel):
    display_name: str
    quantity: float | None = None
    unit: str | None = None
    unit_price: float | None = None
    line_total: float | None = None


class ExtractionData(BaseModel):
    extraction_method: Literal["embedded_text", "ocr"]
    extraction_status: Literal["extracted", "no_data"]
    receipt: ReceiptData
    items: list[ItemData]


AMOUNT = r"-?\d[\d,]*\.\d{2}"
AMOUNT_AT_END = re.compile(rf"(?:RM\s*)?({AMOUNT})\s*$", re.IGNORECASE)
QUANTITY_ITEM = re.compile(
    rf"^(?P<name>.+?)\s+(?P<quantity>\d+(?:\.\d+)?)\s*"
    rf"(?P<unit>kg|g|ml|l|pcs|pc|pack|packs|unit|units)?\s*"
    rf"(?:x|@)?\s*(?:RM\s*)?(?P<unit_price>{AMOUNT})\s+"
    rf"(?:RM\s*)?(?P<line_total>{AMOUNT})$",
    re.IGNORECASE,
)
DATE = re.compile(r"\b(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
RECEIPT_NUMBER = re.compile(
    r"\b(?:receipt|invoice|inv)\s*(?:no\.?|number|#)?\s*[:#-]?\s*([A-Z0-9][A-Z0-9/-]+)",
    re.IGNORECASE,
)
PAYMENT = re.compile(
    r"\b(?:payment(?: method)?|paid(?: by)?)\s*[:\-]?\s*"
    r"(cash|card|visa|mastercard|debit|credit|e-?wallet)\b",
    re.IGNORECASE,
)
NON_ITEM = re.compile(
    r"^(?:sub\s*total|grand\s*total|total|amount\s+due|discount|tax|sst|gst|"
    r"receipt|invoice|inv\b|date\b|payment|paid\b|cash\b|change\b|balance\b)",
    re.IGNORECASE,
)


def embedded_text(path: Path) -> str:
    """Read selectable text from every page of the candidate PDF."""
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def usable_embedded_text(text: str) -> bool:
    """Require receipt-like text before skipping OCR."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    alphanumeric = sum(character.isalnum() for character in text)
    return len(lines) >= 3 and alphanumeric >= 25 and any(AMOUNT_AT_END.search(line) for line in lines)


def ocr_text(path: Path) -> str:
    """Render each PDF page locally and OCR it with the installed Tesseract binary."""
    document = pdfium.PdfDocument(str(path))
    try:
        pages: list[str] = []
        for page in document:
            try:
                bitmap = page.render(scale=2)
                try:
                    image = bitmap.to_pil()
                    try:
                        pages.append(pytesseract.image_to_string(image, config="--psm 6"))
                    finally:
                        image.close()
                finally:
                    bitmap.close()
            finally:
                page.close()
        return "\n".join(pages)
    finally:
        document.close()


def _amount(line: str) -> float | None:
    match = AMOUNT_AT_END.search(line)
    return float(Decimal(match.group(1).replace(",", ""))) if match else None


def _date(line: str) -> str | None:
    match = DATE.search(line)
    if not match:
        return None
    value = match.group(1)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_receipt_text(text: str) -> tuple[ReceiptData, list[ItemData]]:
    """Extract conservative receipt fields without normalization or persistence."""
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    receipt = ReceiptData()
    items: list[ItemData] = []

    for line in lines:
        if receipt.store_name is None and re.search(r"[A-Za-z]", line) and not NON_ITEM.match(line):
            receipt.store_name = line
        if receipt.receipt_date is None:
            receipt.receipt_date = _date(line)
        if receipt.receipt_number is None:
            match = RECEIPT_NUMBER.search(line)
            if match:
                receipt.receipt_number = match.group(1)
        if receipt.payment_method is None:
            match = PAYMENT.search(line)
            if match:
                receipt.payment_method = match.group(1).title()

        label = line.lower()
        if re.match(r"^sub\s*total\b", label):
            receipt.subtotal = _amount(line)
        elif re.match(r"^discount\b", label):
            receipt.discount_total = _amount(line)
        elif re.match(r"^(?:tax|sst|gst)\b", label):
            receipt.tax_total = _amount(line)
        elif re.match(r"^(?:grand\s+total|total|amount\s+due)\b", label):
            receipt.final_total = _amount(line)

        if NON_ITEM.match(line):
            continue
        match = QUANTITY_ITEM.match(line)
        if match:
            items.append(ItemData(
                display_name=match.group("name").strip(),
                quantity=float(match.group("quantity")),
                unit=match.group("unit"),
                unit_price=float(Decimal(match.group("unit_price").replace(",", ""))),
                line_total=float(Decimal(match.group("line_total").replace(",", ""))),
            ))
            continue
        amount_match = AMOUNT_AT_END.search(line)
        if amount_match:
            name = line[:amount_match.start()].strip()
            if name and re.search(r"[A-Za-z]", name):
                items.append(ItemData(display_name=name, line_total=_amount(line)))

    return receipt, items


def extract_candidate(path: Path) -> ExtractionData:
    text = embedded_text(path)
    method: Literal["embedded_text", "ocr"] = "embedded_text"
    if not usable_embedded_text(text):
        text = ocr_text(path)
        method = "ocr"
    receipt, items = parse_receipt_text(text)
    status: Literal["extracted", "no_data"] = (
        "extracted" if items or receipt.final_total is not None or (receipt.store_name and receipt.receipt_date) else "no_data"
    )
    return ExtractionData(extraction_method=method, extraction_status=status, receipt=receipt, items=items)
