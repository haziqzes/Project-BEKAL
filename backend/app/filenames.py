"""Filename convention reserved for future confirmed receipt storage."""

import re
import unicodedata
from datetime import date


def future_receipt_filename(receipt_date: date, store_name: str) -> str:
    """Build YYYY-MM-DD_store.pdf without trusting store text as a path."""
    ascii_name = unicodedata.normalize("NFKD", store_name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "store"
    return f"{receipt_date.isoformat()}_{slug[:80].rstrip('-')}.pdf"
