"""Safe human-readable filenames for confirmed private receipt storage."""

import re
import unicodedata
from datetime import date


def future_receipt_filename(receipt_date: date | None, store_name: str | None) -> str:
    """Use date/store when known; never invent missing source metadata."""
    ascii_name = unicodedata.normalize("NFKD", store_name or "").encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "store"
    date_part = receipt_date.isoformat() if receipt_date else "undated"
    return f"{date_part}_{slug[:80].rstrip('-')}.pdf"
