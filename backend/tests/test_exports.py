"""Synthetic CSV export tests; downloaded data is never written to the repository."""

import csv
from io import StringIO

from test_persistence import payload, saved, setup, synthetic_pdf

from app.exports import ITEM_COLUMNS, RECEIPT_COLUMNS


def records(response) -> list[dict[str, str]]:
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    return list(csv.DictReader(StringIO(response.content.decode("utf-8-sig"))))


def test_empty_exports_have_utf8_headers_and_private_download_headers(setup) -> None:
    client, _, _ = setup
    for filename, columns in (("receipts.csv", RECEIPT_COLUMNS), ("items.csv", ITEM_COLUMNS)):
        response = client.get(f"/api/exports/{filename}")
        assert records(response) == []
        assert response.content.decode("utf-8-sig").splitlines()[0] == ",".join(columns)
        assert response.headers["content-disposition"] == f'attachment; filename="{filename}"'
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "text/csv" in response.headers["content-type"]


def test_export_preserves_nulls_money_quantity_and_spreadsheet_safety(setup) -> None:
    client, _, _ = setup
    data = payload("+UNSAFE SOURCE", "Safe Product")
    data["receipt"].update(store_name='=HYPERLINK("https://invalid.example")',
                           receipt_number="@INJECT", subtotal=None, discount_total=None,
                           tax_total=None)
    receipt_id = saved(client, data)
    receipt = records(client.get("/api/exports/receipts.csv"))[0]
    item = records(client.get("/api/exports/items.csv"))[0]
    assert receipt["receipt_id"] == receipt_id
    assert receipt["receipt_date"] == "2026-10-10"
    assert receipt["store_name"].startswith("'=")
    assert receipt["receipt_number"] == "'@INJECT"
    assert receipt["subtotal_myr"] == ""
    assert receipt["final_total_myr"] == "9.00"
    assert receipt["currency"] == "MYR"
    assert item["receipt_id"] == receipt_id
    assert item["source_name"] == "'+UNSAFE SOURCE"
    assert item["product_name"] == "Safe Product"
    assert item["quantity"] == "2.000"
    assert item["unit_price_myr"] == "4.50"
    assert item["line_total_myr"] == "9.00"
    assert item["review_recommended"] == "false"
    assert "original_file_path" not in receipt and "file_sha256" not in receipt


def test_exports_reflect_saved_edits_and_deletion(setup) -> None:
    client, _, _ = setup
    first = saved(client, pdf=synthetic_pdf("FIRST"))
    second_data = payload("BREAD", "Bread")
    second_data["receipt"].update(store_name="Other Synthetic", receipt_date=None,
                                  final_total=None, subtotal=None)
    second_data["items"][0].update(quantity=None, unit=None, unit_price=None, line_total=None,
                                   category="Bread & Bakery")
    second = saved(client, second_data, synthetic_pdf("SECOND"))
    initial = records(client.get("/api/exports/receipts.csv"))
    assert [row["receipt_id"] for row in initial] == [first, second]
    detail = client.get(f"/api/receipts/{first}").json()
    detail["receipt"]["store_name"] = "Edited Synthetic"
    detail["receipt"]["final_total"] = 12
    detail["items"][0]["line_total"] = 12
    assert client.put(f"/api/receipts/{first}", json={"receipt": detail["receipt"], "items": detail["items"]}).status_code == 200
    assert client.delete(f"/api/receipts/{second}").status_code == 200
    receipts_csv = records(client.get("/api/exports/receipts.csv"))
    items_csv = records(client.get("/api/exports/items.csv"))
    assert len(receipts_csv) == 1 and receipts_csv[0]["receipt_id"] == first
    assert receipts_csv[0]["store_name"] == "Edited Synthetic"
    assert receipts_csv[0]["final_total_myr"] == "12.00"
    assert len(items_csv) == 1 and items_csv[0]["receipt_id"] == first
    assert items_csv[0]["line_total_myr"] == "12.00"
