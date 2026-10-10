"""Confirmed receipt persistence with private PDF storage and rollback cleanup."""

import hashlib
import os
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, create_engine, func, or_, select
from sqlalchemy.engine import Connection

from app.candidates import CandidateStore
from app.filenames import future_receipt_filename
from app.review import CATEGORIES
from app.schema import categories, product_aliases, products, receipt_items, receipts

CONFIRM_LOCK = Lock()  # One local API process; database keys provide a second idempotency guard.


class ReceiptInput(BaseModel):
    store_name: str | None = Field(default=None, max_length=255)
    receipt_date: date | None = None
    receipt_number: str | None = Field(default=None, max_length=120)
    payment_method: str | None = Field(default=None, max_length=120)
    subtotal: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    discount_total: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    tax_total: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    final_total: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: Literal["MYR"] = "MYR"

    @field_validator("store_name", "receipt_number", "payment_method")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class ItemInput(BaseModel):
    raw_name: str | None = Field(default=None, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    quantity: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    unit: str | None = Field(default=None, max_length=30)
    unit_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    line_total: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    category: str
    review_flag: bool = False

    @field_validator("display_name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Product name is required")
        return value

    @field_validator("category")
    @classmethod
    def known_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("Choose a predefined category")
        return value


class ConfirmInput(BaseModel):
    receipt: ReceiptInput
    items: list[ItemInput] = Field(min_length=1)
    allow_duplicate: bool = False


def _key(value: str) -> str:
    return " ".join(value.casefold().split())


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _saved_result(connection: Connection, receipt_id: str) -> dict | None:
    row = connection.execute(select(receipts).where(receipts.c.id == receipt_id)).mappings().first()
    if row is None:
        return None
    count = connection.execute(select(func.count()).select_from(receipt_items).where(receipt_items.c.receipt_id == receipt_id)).scalar_one()
    return {"status": "stored", "id": receipt_id, "store_name": row["store_name"],
            "receipt_date": row["receipt_date"].isoformat() if row["receipt_date"] else None,
            "item_count": count, "final_total": float(row["final_total"]) if row["final_total"] is not None else None}


def _duplicate(connection: Connection, receipt: ReceiptInput, file_hash: str) -> dict | None:
    exact = connection.execute(select(receipts.c.id).where(receipts.c.file_sha256 == file_hash).limit(1)).scalar_one_or_none()
    if exact:
        return {"code": "possible_duplicate", "match_id": exact, "match_kind": "exact_file"}
    conditions = []
    if receipt.store_name and receipt.receipt_number:
        conditions.append(and_(func.lower(receipts.c.store_name) == receipt.store_name.casefold(),
                               receipts.c.receipt_number == receipt.receipt_number))
    if receipt.store_name and receipt.receipt_date and receipt.final_total is not None:
        conditions.append(and_(func.lower(receipts.c.store_name) == receipt.store_name.casefold(),
                               receipts.c.receipt_date == receipt.receipt_date,
                               receipts.c.final_total == receipt.final_total))
    if not conditions:
        return None
    row = connection.execute(select(receipts.c.id).where(or_(*conditions)).limit(1)).first()
    if row is None:
        return None
    return {"code": "possible_duplicate", "match_id": row.id, "match_kind": "possible_receipt"}


def _category_ids(connection: Connection) -> dict[str, int]:
    return dict(connection.execute(select(categories.c.name, categories.c.id)).all())


def _product_for_item(connection: Connection, item: ItemInput, category_id: int) -> tuple[str, str]:
    source = " ".join((item.raw_name or "").split())
    source_key = _key(source) if source else ""
    display_key = _key(item.display_name)
    alias = None
    if source_key:
        alias = connection.execute(select(product_aliases.c.product_id).where(product_aliases.c.alias_key == source_key)).scalar_one_or_none()
    if alias:
        product = connection.execute(select(products.c.canonical_name, products.c.name_key).where(products.c.id == alias)).one()
        if display_key not in (source_key, product.name_key):
            raise HTTPException(status_code=409, detail={"code": "alias_conflict", "source_name": source})
        return alias, product.canonical_name

    product = connection.execute(select(products.c.id, products.c.canonical_name).where(products.c.name_key == display_key)).first()
    if product is None:
        product_id = str(uuid4())
        connection.execute(products.insert().values(id=product_id, canonical_name=item.display_name,
                                                    name_key=display_key, default_category_id=category_id))
        canonical_name = item.display_name
    else:
        product_id, canonical_name = product.id, product.canonical_name
    if source_key and source_key != display_key:
        connection.execute(product_aliases.insert().values(id=str(uuid4()), source_alias=source,
                                                           alias_key=source_key, product_id=product_id))
    return product_id, canonical_name


def _destination(root: Path, candidate_id: UUID, receipt: ReceiptInput) -> tuple[Path, Path]:
    directory = (Path(str(receipt.receipt_date.year)) / f"{receipt.receipt_date.month:02d}") if receipt.receipt_date else Path("undated")
    base = future_receipt_filename(receipt.receipt_date, receipt.store_name)
    folder = root / directory
    target = folder / base
    if target.exists():
        stem = base[:-4]
        target = folder / f"{stem}_{candidate_id.hex[:6]}.pdf"
        index = 2
        while target.exists():
            target = folder / f"{stem}_{candidate_id.hex[:6]}_{index}.pdf"
            index += 1
    return target, target.relative_to(root)


def _copy_private(source: Path, target: Path, candidate_id: UUID) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    pending = target.parent / f".{candidate_id}.pending"
    linked = False
    try:
        descriptor = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as original:
            shutil.copyfileobj(original, output)
            output.flush()
            os.fsync(output.fileno())
        os.link(pending, target)  # Fails instead of replacing an existing private receipt.
        linked = True
    except Exception:
        if linked:
            target.unlink(missing_ok=True)
        raise
    finally:
        try:
            pending.unlink(missing_ok=True)
        except OSError:
            if linked:
                target.unlink(missing_ok=True)
            raise


def confirm_candidate(candidate_id: UUID, payload: ConfirmInput, store: CandidateStore,
                      database_url: str, storage_root: Path) -> dict:
    """Commit structured data and a private PDF, retaining the candidate on failure."""
    with CONFIRM_LOCK:
        engine = create_engine(database_url, pool_pre_ping=True)
        target: Path | None = None
        copied = False
        committed = False
        try:
            with engine.begin() as connection:
                existing = _saved_result(connection, str(candidate_id))
                if existing:
                    try:
                        store.delete(candidate_id)
                    except OSError:
                        pass
                    return existing
                candidate = store.get(candidate_id)
                if candidate is None:
                    raise HTTPException(status_code=404, detail="Candidate not found or expired")
                digest = _file_hash(candidate.path)
                duplicate = _duplicate(connection, payload.receipt, digest)
                if duplicate and not payload.allow_duplicate:
                    raise HTTPException(status_code=409, detail=duplicate)
                ids = _category_ids(connection)
                if any(item.category not in ids for item in payload.items):
                    raise HTTPException(status_code=409, detail="Predefined categories are unavailable; run migrations")
                target, relative = _destination(storage_root, candidate_id, payload.receipt)
                receipt_values = payload.receipt.model_dump()
                connection.execute(receipts.insert().values(id=str(candidate_id), **receipt_values,
                    original_file_path=relative.as_posix(), file_sha256=digest))
                for item in payload.items:
                    category_id = ids[item.category]
                    product_id, canonical_name = _product_for_item(connection, item, category_id)
                    connection.execute(receipt_items.insert().values(
                        id=str(uuid4()), receipt_id=str(candidate_id), product_id=product_id,
                        category_id=category_id, source_name=item.raw_name or None,
                        display_name=canonical_name, quantity=item.quantity, unit=item.unit,
                        unit_price=item.unit_price, line_total=item.line_total,
                        review_flag=item.review_flag))
                _copy_private(candidate.path, target, candidate_id)
                copied = True
            committed = True
            try:
                store.delete(candidate_id)
            except OSError:
                # The receipt is committed; the candidate will expire or be cleared on restart.
                pass
            return {"status": "stored", "id": str(candidate_id),
                    "store_name": payload.receipt.store_name,
                    "receipt_date": payload.receipt.receipt_date.isoformat() if payload.receipt.receipt_date else None,
                    "item_count": len(payload.items),
                    "final_total": float(payload.receipt.final_total) if payload.receipt.final_total is not None else None}
        except HTTPException:
            if copied and not committed and target:
                target.unlink(missing_ok=True)
            raise
        except Exception as exc:
            if copied and not committed and target:
                target.unlink(missing_ok=True)
            raise HTTPException(status_code=503, detail="Could not save the receipt. The temporary candidate is still available.") from exc
        finally:
            engine.dispose()
