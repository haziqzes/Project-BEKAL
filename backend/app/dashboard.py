"""Read-only monthly overview of confirmed receipt data."""

import os
from collections import defaultdict
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import create_engine, select

from app.schema import categories, products, receipt_items, receipts

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _month_bounds(month: str) -> tuple[date, date]:
    year, number = map(int, month.split("-"))
    if not 1 <= year <= 9998:
        raise HTTPException(status_code=422, detail="Choose a valid calendar month")
    start = date(year, number, 1)
    end = date(year + 1, 1, 1) if number == 12 else date(year, number + 1, 1)
    return start, end


def monthly_overview(database_url: str, month: str) -> dict:
    """Aggregate only dated, permanently saved MYR receipts in one calendar month."""
    start, end = _month_bounds(month)
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            saved = connection.execute(
                select(receipts.c.id, receipts.c.receipt_date, receipts.c.store_name,
                       receipts.c.final_total, receipts.c.created_at)
                .where(receipts.c.receipt_date >= start, receipts.c.receipt_date < end,
                       receipts.c.currency == "MYR")
                .order_by(receipts.c.receipt_date.desc(), receipts.c.created_at.desc(), receipts.c.id.desc())
            ).mappings().all()
            items = connection.execute(
                select(receipt_items.c.receipt_id, receipt_items.c.product_id,
                       receipt_items.c.quantity, receipt_items.c.unit, receipt_items.c.unit_price,
                       receipt_items.c.line_total, receipt_items.c.review_flag,
                       categories.c.name.label("category"), products.c.canonical_name.label("product_name"),
                       receipts.c.receipt_date, receipts.c.store_name)
                .join(receipts, receipt_items.c.receipt_id == receipts.c.id)
                .join(categories, receipt_items.c.category_id == categories.c.id)
                .join(products, receipt_items.c.product_id == products.c.id)
                .where(receipts.c.receipt_date >= start, receipts.c.receipt_date < end,
                       receipts.c.currency == "MYR")
                .order_by(receipts.c.receipt_date.desc(), receipts.c.created_at.desc(),
                          receipts.c.id.desc(), receipt_items.c.id.desc())
            ).mappings().all()
    finally:
        engine.dispose()

    known_totals = [row["final_total"] for row in saved if row["final_total"] is not None]
    missing_total_count = len(saved) - len(known_totals)
    spending = float(sum(known_totals, Decimal("0"))) if known_totals or not saved else None

    category_totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    product_counts: dict[tuple[str, str], int] = defaultdict(int)
    price_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in items:
        product_key = (item["product_id"], item["product_name"])
        product_counts[product_key] += 1  # Purchase occurrences, not inferred quantities.
        if item["line_total"] is not None:
            category_totals[item["category"]] += item["line_total"]
        unit = (item["unit"] or "").strip().casefold()
        if (item["unit_price"] is not None and item["quantity"] is not None
                and item["quantity"] > 0 and unit and not item["review_flag"]):
            price_groups[(item["product_id"], unit)].append({
                "product_name": item["product_name"], "unit": unit,
                "unit_price": float(item["unit_price"]), "receipt_date": item["receipt_date"].isoformat(),
                "store_name": item["store_name"], "receipt_id": item["receipt_id"],
            })

    comparable = []
    for points in price_groups.values():
        per_receipt: dict[str, list[dict]] = defaultdict(list)
        for point in points:
            per_receipt[point["receipt_id"]].append(point)
        # Multiple prices for the same product and unit on one receipt are ambiguous.
        unambiguous = [point for receipt_points in per_receipt.values()
                       if len(receipt_points) == 1 for point in receipt_points]
        if len(unambiguous) >= 2:
            comparable.append(unambiguous)
    comparable.sort(key=lambda points: (points[0]["receipt_date"], points[0]["receipt_id"],
                                         points[0]["product_name"]), reverse=True)
    return {
        "month": month, "currency": "MYR", "receipt_count": len(saved),
        "total_spending": spending, "missing_total_count": missing_total_count,
        "top_categories": [{"category": name, "known_item_spending": float(total)}
                           for name, total in sorted(category_totals.items(), key=lambda pair: (-pair[1], pair[0]))[:5]],
        "most_purchased": [{"product_name": name, "purchase_count": count}
                           for (_, name), count in sorted(product_counts.items(), key=lambda pair: (-pair[1], pair[0][1]))[:5]],
        "recent_price_history": [{"product_name": points[0]["product_name"], "unit": points[0]["unit"],
                                  "points": points[:5]} for points in comparable[:5]],
        "recent_receipts": [{"id": row["id"], "receipt_date": row["receipt_date"].isoformat(),
                             "store_name": row["store_name"],
                             "final_total": float(row["final_total"]) if row["final_total"] is not None else None}
                            for row in saved[:5]],
    }


@router.get("")
def get_monthly_dashboard(month: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")) -> dict:
    chosen = month or date.today().strftime("%Y-%m")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return monthly_overview(database_url, chosen)
