"""Saved receipt history and explicit local CRUD operations."""

import os
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, delete, func, select, update

from app.persistence import ItemInput, ReceiptInput, _category_ids, _product_for_item
from app.schema import categories, receipt_items, receipts

router = APIRouter(prefix="/api/receipts", tags=["saved receipts"])


class SavedItemInput(ItemInput):
    id: UUID | None = None


class UpdateInput(BaseModel):
    receipt: ReceiptInput
    items: list[SavedItemInput] = Field(min_length=1)


def _settings() -> tuple[str, Path]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return database_url, Path(os.getenv("RECEIPT_STORAGE_DIR", "../runtime-data/receipts"))


def _private_pdf(root: Path, relative: str) -> Path:
    reference = Path(relative)
    if reference.is_absolute() or not relative or ".." in reference.parts:
        raise HTTPException(status_code=409, detail="Stored PDF reference is invalid")
    private_root = root.resolve()
    current = private_root
    for part in reference.parts:
        current = current / part
        if current.is_symlink():
            raise HTTPException(status_code=409, detail="Stored PDF reference is invalid")
    target = (private_root / reference).resolve()
    if not target.is_relative_to(private_root):
        raise HTTPException(status_code=409, detail="Stored PDF reference is invalid")
    return target


def _receipt_json(row) -> dict:
    return {key: row[key].isoformat() if key == "receipt_date" and row[key] else
            float(row[key]) if key in {"subtotal", "discount_total", "tax_total", "final_total"} and row[key] is not None else
            row[key] for key in ("store_name", "receipt_date", "receipt_number", "payment_method",
                                  "subtotal", "discount_total", "tax_total", "final_total", "currency")}


def _details(connection, receipt_id: str) -> dict:
    row = connection.execute(select(receipts).where(receipts.c.id == receipt_id)).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    items = connection.execute(
        select(receipt_items, categories.c.name.label("category"))
        .join(categories, receipt_items.c.category_id == categories.c.id)
        .where(receipt_items.c.receipt_id == receipt_id)
        .order_by(receipt_items.c.created_at, receipt_items.c.id)
    ).mappings().all()
    return {"id": receipt_id, "receipt": _receipt_json(row),
            "created_at": row["created_at"].isoformat(), "updated_at": row["updated_at"].isoformat(),
            "pdf_url": f"/api/receipts/{receipt_id}/pdf",
            "items": [{"id": item["id"], "raw_name": item["source_name"] or "",
                       "display_name": item["display_name"], "quantity": float(item["quantity"]) if item["quantity"] is not None else None,
                       "unit": item["unit"], "unit_price": float(item["unit_price"]) if item["unit_price"] is not None else None,
                       "line_total": float(item["line_total"]) if item["line_total"] is not None else None,
                       "category": item["category"], "review_flag": item["review_flag"]} for item in items]}


@router.get("")
def list_receipts() -> list[dict]:
    database_url, _ = _settings()
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            counts = select(receipt_items.c.receipt_id, func.count().label("item_count")).group_by(receipt_items.c.receipt_id).subquery()
            rows = connection.execute(
                select(receipts.c.id, receipts.c.receipt_date, receipts.c.store_name, receipts.c.final_total,
                       receipts.c.currency, receipts.c.created_at, func.coalesce(counts.c.item_count, 0).label("item_count"))
                .outerjoin(counts, counts.c.receipt_id == receipts.c.id)
                .order_by(receipts.c.receipt_date.desc().nulls_last(), receipts.c.created_at.desc(), receipts.c.id.desc())
            ).mappings().all()
            return [{"id": row["id"], "receipt_date": row["receipt_date"].isoformat() if row["receipt_date"] else None,
                     "store_name": row["store_name"], "item_count": row["item_count"],
                     "final_total": float(row["final_total"]) if row["final_total"] is not None else None,
                     "currency": row["currency"], "created_at": row["created_at"].isoformat()} for row in rows]
    finally:
        engine.dispose()


@router.get("/{receipt_id}")
def get_receipt(receipt_id: UUID) -> dict:
    database_url, _ = _settings()
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return _details(connection, str(receipt_id))
    finally:
        engine.dispose()


@router.get("/{receipt_id}/pdf")
def get_receipt_pdf(receipt_id: UUID) -> FileResponse:
    database_url, root = _settings()
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            relative = connection.execute(select(receipts.c.original_file_path).where(receipts.c.id == str(receipt_id))).scalar_one_or_none()
    finally:
        engine.dispose()
    if relative is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    pdf = _private_pdf(root, relative)
    if not pdf.is_file():
        raise HTTPException(status_code=404, detail="The original PDF is missing. Receipt details are still available.")
    return FileResponse(pdf, media_type="application/pdf", filename=f"{receipt_id}.pdf",
                        content_disposition_type="inline",
                        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"})


@router.put("/{receipt_id}")
def update_receipt(receipt_id: UUID, payload: UpdateInput) -> dict:
    database_url, _ = _settings()
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            existing = connection.execute(select(receipts.c.id).where(receipts.c.id == str(receipt_id)).with_for_update()).scalar_one_or_none()
            if existing is None:
                raise HTTPException(status_code=404, detail="Receipt not found")
            old_ids = set(connection.execute(select(receipt_items.c.id).where(receipt_items.c.receipt_id == str(receipt_id))).scalars())
            submitted_ids = [str(item.id) for item in payload.items if item.id]
            if len(submitted_ids) != len(set(submitted_ids)) or not set(submitted_ids).issubset(old_ids):
                raise HTTPException(status_code=422, detail="Item IDs must belong to this receipt and be unique")
            ids = _category_ids(connection)
            if any(item.category not in ids for item in payload.items):
                raise HTTPException(status_code=409, detail="Predefined categories are unavailable; run migrations")
            connection.execute(update(receipts).where(receipts.c.id == str(receipt_id)).values(
                **payload.receipt.model_dump(), updated_at=func.now()))
            for item in payload.items:
                category_id = ids[item.category]
                product_id, canonical_name = _product_for_item(connection, item, category_id)
                values = dict(product_id=product_id, category_id=category_id, source_name=item.raw_name or None,
                              display_name=canonical_name, quantity=item.quantity, unit=item.unit,
                              unit_price=item.unit_price, line_total=item.line_total, review_flag=item.review_flag)
                if item.id:
                    connection.execute(update(receipt_items).where(receipt_items.c.id == str(item.id)).values(
                        **values, updated_at=func.now()))
                else:
                    connection.execute(receipt_items.insert().values(
                        id=str(uuid4()), receipt_id=str(receipt_id), **values))
            removed_ids = old_ids - set(submitted_ids)
            if removed_ids:
                connection.execute(delete(receipt_items).where(receipt_items.c.id.in_(removed_ids)))
            return _details(connection, str(receipt_id))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not update the receipt. Saved data is unchanged.") from exc
    finally:
        engine.dispose()


@router.delete("/{receipt_id}")
def delete_receipt(receipt_id: UUID) -> dict:
    database_url, root = _settings()
    engine = create_engine(database_url, pool_pre_ping=True)
    pdf = staged = None
    committed = False
    missing = False
    try:
        with engine.begin() as connection:
            relative = connection.execute(select(receipts.c.original_file_path).where(receipts.c.id == str(receipt_id)).with_for_update()).scalar_one_or_none()
            if relative is None:
                raise HTTPException(status_code=404, detail="Receipt not found")
            pdf = _private_pdf(root, relative)
            if pdf.is_file():
                staged = pdf.with_name(f".{uuid4()}.deleting")
                pdf.rename(staged)
            else:
                missing = True
            connection.execute(delete(receipt_items).where(receipt_items.c.receipt_id == str(receipt_id)))
            connection.execute(delete(receipts).where(receipts.c.id == str(receipt_id)))
        committed = True
        cleanup_pending = False
        if staged:
            try:
                staged.unlink()
            except OSError:
                cleanup_pending = True
        return {"status": "deleted", "id": str(receipt_id), "pdf_missing": missing,
                "file_cleanup_pending": cleanup_pending}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not delete the receipt. Try again.") from exc
    finally:
        if staged and not committed and staged.exists() and pdf is not None:
            staged.rename(pdf)
        engine.dispose()
