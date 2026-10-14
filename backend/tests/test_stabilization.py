"""Synthetic end-to-end and private-file recovery checks."""

import csv
from io import StringIO

from sqlalchemy import select

from test_extraction import text_pdf
from test_persistence import saved, setup, synthetic_pdf, upload

from app.schema import receipt_items, receipts
from app.storage_recovery import recover_private_storage


def test_upload_extract_correct_save_view_and_export(setup) -> None:
    client, engine, root = setup
    original = text_pdf([
        "FRESH MART", "Date: 10/10/2026", "Receipt No: INV-101", "Payment: Card",
        "MILK 2 pcs 4.50 9.00", "Total RM 9.00",
    ])
    candidate_id = upload(client, original)
    extraction = client.post(f"/api/candidates/{candidate_id}/extract")
    assert extraction.status_code == 200
    candidate = extraction.json()
    assert candidate["extraction_method"] == "embedded_text"
    assert candidate["review"]["items"][0]["raw_name"] == "MILK"
    assert client.get(f"/api/candidates/{candidate_id}/pdf").content == original

    corrected = candidate["review"]["items"][0]
    corrected["display_name"] = "Fresh Milk"
    corrected["category"] = "Dairy"
    receipt = candidate["review"]["receipt"]
    receipt["store_name"] = "Fresh Mart"
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json={
        "receipt": receipt, "items": [corrected],
    })
    assert response.status_code == 200, response.text
    detail = client.get(f"/api/receipts/{candidate_id}")
    assert detail.status_code == 200
    assert detail.json()["receipt"]["store_name"] == "Fresh Mart"
    assert detail.json()["items"][0]["display_name"] == "Fresh Milk"
    assert client.get(f"/api/receipts/{candidate_id}/pdf").content == original
    rows = list(csv.DictReader(StringIO(client.get("/api/exports/items.csv").content.decode("utf-8-sig"))))
    assert rows[0]["receipt_id"] == candidate_id
    assert rows[0]["product_name"] == "Fresh Milk"
    assert rows[0]["line_total_myr"] == "9.00"
    assert not (root / "candidates" / f"{candidate_id}.pdf").exists()
    with engine.connect() as connection:
        assert connection.execute(select(receipts.c.id)).scalars().all() == [candidate_id]


def test_recovery_restores_precommit_delete_and_finishes_committed_delete(setup) -> None:
    client, engine, root = setup
    receipt_id = saved(client)
    with engine.connect() as connection:
        relative = connection.execute(select(receipts.c.original_file_path)).scalar_one()
    pdf = root / "receipts" / relative
    staged = pdf.with_name(f".{pdf.name}.{receipt_id}.deleting")
    pdf.rename(staged)
    recover_private_storage(str(engine.url), root / "receipts")
    assert pdf.is_file() and not staged.exists()
    assert client.get(f"/api/receipts/{receipt_id}/pdf").status_code == 200

    pdf.rename(staged)
    with engine.begin() as connection:
        connection.execute(receipt_items.delete().where(receipt_items.c.receipt_id == receipt_id))
        connection.execute(receipts.delete().where(receipts.c.id == receipt_id))
    recover_private_storage(str(engine.url), root / "receipts")
    assert not pdf.exists() and not staged.exists()


def test_recovery_quarantines_unreferenced_pdf_without_losing_bytes(setup) -> None:
    client, engine, root = setup
    receipt_id = saved(client)
    with engine.connect() as connection:
        relative = connection.execute(select(receipts.c.original_file_path)).scalar_one()
    stored = root / "receipts" / relative
    orphan = stored.with_name("orphan-synthetic.pdf")
    private_bytes = synthetic_pdf("ORPHAN SYNTHETIC")
    orphan.write_bytes(private_bytes)
    recover_private_storage(str(engine.url), root / "receipts")
    assert not orphan.exists()
    quarantined = list((root / "receipts" / ".recovery").glob("*.pdf"))
    assert len(quarantined) == 1 and quarantined[0].read_bytes() == private_bytes
    assert stored.is_file()
    assert client.get(f"/api/receipts/{receipt_id}/pdf").status_code == 200
