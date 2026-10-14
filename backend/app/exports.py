"""On-demand, private CSV views of confirmed receipts; no export files are stored."""

import csv
import io
import os
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from sqlalchemy import create_engine, select

from app.schema import categories, receipt_items, receipts

router = APIRouter(prefix="/api/exports", tags=["CSV export"])

RECEIPT_COLUMNS = (
    "receipt_id", "receipt_date", "store_name", "receipt_number", "payment_method",
    "subtotal_myr", "discount_total_myr", "tax_total_myr", "final_total_myr",
    "currency", "created_at", "updated_at",
)
ITEM_COLUMNS = (
    "item_id", "receipt_id", "receipt_date", "store_name", "source_name", "product_name",
    "category", "quantity", "unit", "unit_price_myr", "line_total_myr", "review_recommended",
)


def _cell(value, places: int | None = None) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return f"{value:.{places or 2}f}"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    result = str(value)
    # Spreadsheet applications may evaluate text cells beginning with a formula trigger.
    if result.lstrip().startswith(("=", "+", "-", "@")) or result.startswith(("\t", "\r", "\n")):
        return "'" + result
    return result


def _csv(columns: tuple[str, ...], rows: list[tuple]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(columns)
    writer.writerows(rows)
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def _response(filename: str, content: bytes) -> Response:
    return Response(content=content, media_type="text/csv; charset=utf-8", headers={
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
    })


def _database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if not value:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return value


@router.get("/receipts.csv")
def export_receipts() -> Response:
    engine = create_engine(_database_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            saved = connection.execute(
                select(receipts.c.id, receipts.c.receipt_date, receipts.c.store_name,
                       receipts.c.receipt_number, receipts.c.payment_method, receipts.c.subtotal,
                       receipts.c.discount_total, receipts.c.tax_total, receipts.c.final_total,
                       receipts.c.currency, receipts.c.created_at, receipts.c.updated_at)
                .where(receipts.c.currency == "MYR")
                .order_by(receipts.c.receipt_date.desc().nulls_last(), receipts.c.created_at.desc(), receipts.c.id.desc())
            ).all()
    finally:
        engine.dispose()
    rows = [tuple(_cell(value) for value in row) for row in saved]
    return _response("receipts.csv", _csv(RECEIPT_COLUMNS, rows))


@router.get("/items.csv")
def export_items() -> Response:
    engine = create_engine(_database_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            items = connection.execute(
                select(receipt_items.c.id, receipt_items.c.receipt_id, receipts.c.receipt_date,
                       receipts.c.store_name, receipt_items.c.source_name, receipt_items.c.display_name,
                       categories.c.name, receipt_items.c.quantity, receipt_items.c.unit,
                       receipt_items.c.unit_price, receipt_items.c.line_total, receipt_items.c.review_flag)
                .join(receipts, receipt_items.c.receipt_id == receipts.c.id)
                .join(categories, receipt_items.c.category_id == categories.c.id)
                .where(receipts.c.currency == "MYR")
                .order_by(receipts.c.receipt_date.desc().nulls_last(), receipts.c.created_at.desc(),
                          receipts.c.id.desc(), receipt_items.c.created_at, receipt_items.c.id)
            ).all()
    finally:
        engine.dispose()
    rows = [tuple(_cell(value, 3 if index == 7 else None) for index, value in enumerate(row)) for row in items]
    return _response("items.csv", _csv(ITEM_COLUMNS, rows))
