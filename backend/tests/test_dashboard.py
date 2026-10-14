"""Synthetic monthly dashboard aggregation tests."""

from datetime import date

from test_persistence import payload, saved, setup, synthetic_pdf


def receipt_data(store: str, day: str, name: str = "Milk", price: float | None = 4.5,
                 total: float | None = 9, unit: str | None = "pcs", flagged: bool = False) -> dict:
    data = payload(name.upper(), name)
    data["receipt"].update(store_name=store, receipt_date=day, final_total=total, subtotal=total)
    data["items"][0].update(unit_price=price, line_total=total, unit=unit, review_flag=flagged)
    return data


def test_empty_month_and_invalid_month(setup) -> None:
    client, _, _ = setup
    result = client.get("/api/dashboard?month=2026-10")
    assert result.status_code == 200
    assert result.json() == {"month": "2026-10", "currency": "MYR", "receipt_count": 0,
                             "total_spending": 0.0, "missing_total_count": 0,
                             "top_categories": [], "most_purchased": [],
                             "recent_price_history": [], "recent_receipts": []}
    assert client.get("/api/dashboard?month=2026-13").status_code == 422
    assert client.get("/api/dashboard?month=0000-01").status_code == 422
    assert client.get("/api/dashboard?month=9999-12").status_code == 422
    assert client.get("/api/dashboard").json()["month"] == date.today().strftime("%Y-%m")


def test_monthly_totals_categories_products_and_comparable_prices(setup) -> None:
    client, _, _ = setup
    older = saved(client, receipt_data("Synthetic A", "2026-10-01"), synthetic_pdf("A"))
    newer = saved(client, receipt_data("Synthetic B", "2026-10-14", price=5, total=10), synthetic_pdf("B"))
    partial = saved(client, receipt_data("Synthetic Partial", "2026-10-15", name="Bread", price=None,
                                         total=None, unit=None, flagged=True), synthetic_pdf("PARTIAL"))
    saved(client, receipt_data("November Shop", "2026-11-01", price=20, total=40), synthetic_pdf("NOVEMBER"))
    result = client.get("/api/dashboard?month=2026-10").json()
    assert result["receipt_count"] == 3
    assert result["total_spending"] == 19
    assert result["missing_total_count"] == 1
    assert result["top_categories"] == [{"category": "Dairy", "known_item_spending": 19}]
    assert result["most_purchased"] == [{"product_name": "Milk", "purchase_count": 2},
                                         {"product_name": "Bread", "purchase_count": 1}]
    assert [row["id"] for row in result["recent_receipts"]] == [partial, newer, older]
    assert result["recent_price_history"] == [{"product_name": "Milk", "unit": "pcs", "points": [
        {"product_name": "Milk", "unit": "pcs", "unit_price": 5, "receipt_date": "2026-10-14",
         "store_name": "Synthetic B", "receipt_id": newer},
        {"product_name": "Milk", "unit": "pcs", "unit_price": 4.5, "receipt_date": "2026-10-01",
         "store_name": "Synthetic A", "receipt_id": older}]}]
    november = client.get("/api/dashboard?month=2026-11").json()
    assert november["receipt_count"] == 1 and november["total_spending"] == 40
    assert november["recent_price_history"] == []


def test_reviewed_comparable_price_requires_same_unit_and_distinct_receipts(setup) -> None:
    client, _, _ = setup
    first = receipt_data("A", "2026-10-01")
    first["items"].append({**first["items"][0], "unit_price": 8})
    saved(client, first, synthetic_pdf("A"))
    saved(client, receipt_data("B", "2026-10-02", unit="kg"), synthetic_pdf("B"))
    saved(client, receipt_data("C", "2026-10-03", flagged=True), synthetic_pdf("C"))
    assert client.get("/api/dashboard?month=2026-10").json()["recent_price_history"] == []


def test_edits_and_deletion_change_dashboard_without_new_persistence(setup) -> None:
    client, engine, root = setup
    first = saved(client, receipt_data("First", "2026-10-01"), synthetic_pdf("FIRST"))
    second = saved(client, receipt_data("Second", "2026-10-02", price=5, total=10), synthetic_pdf("SECOND"))
    detail = client.get(f"/api/receipts/{first}").json()
    detail["receipt"].update(receipt_date="2026-11-01", final_total=12, subtotal=12)
    detail["items"][0]["line_total"] = 12
    assert client.put(f"/api/receipts/{first}", json={"receipt": detail["receipt"], "items": detail["items"]}).status_code == 200
    october = client.get("/api/dashboard?month=2026-10").json()
    assert october["receipt_count"] == 1 and october["total_spending"] == 10
    assert [row["id"] for row in october["recent_receipts"]] == [second]
    assert client.get("/api/dashboard?month=2026-11").json()["total_spending"] == 12
    assert client.delete(f"/api/receipts/{second}").status_code == 200
    assert client.get("/api/dashboard?month=2026-10").json()["receipt_count"] == 0
    assert client.get(f"/api/receipts/{first}").status_code == 200
