"""Synthetic persistence and failure-path tests; no real receipt data."""

from io import BytesIO
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine, func, select

from app import persistence
from app import history
from app.filenames import future_receipt_filename
from app.main import app
from app.schema import categories, product_aliases, products, receipt_items, receipts


def synthetic_pdf(label: str = "SYNTHETIC SHOP", item_line: str = "MILK 2 pcs 4.50 9.00") -> bytes:
    output = BytesIO()
    document = canvas.Canvas(output)
    document.drawString(50, 750, label)
    document.drawString(50, 720, item_line)
    document.drawString(50, 690, "Total RM 9.00")
    document.save()
    return output.getvalue()


def payload(raw: str = "MILK", name: str = "Milk") -> dict:
    return {"receipt": {"store_name": "Synthetic Shop", "receipt_date": "2026-10-10",
                        "receipt_number": "SYN-101", "payment_method": "Card", "subtotal": 9,
                        "discount_total": None, "tax_total": None, "final_total": 9, "currency": "MYR"},
            "items": [{"raw_name": raw, "display_name": name, "quantity": 2, "unit": "pcs",
                       "unit_price": 4.5, "line_total": 9, "category": "Dairy"}]}


@pytest.fixture
def setup(tmp_path: Path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("CANDIDATE_STORAGE_DIR", str(tmp_path / "candidates"))
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path / "receipts"))
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    command.upgrade(config, "head")
    with TestClient(app) as client:
        yield client, create_engine(url), tmp_path


def upload(client: TestClient, pdf: bytes | None = None) -> str:
    response = client.post("/api/candidates", files={"file": ("synthetic.pdf", pdf or synthetic_pdf(), "application/pdf")})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def count(engine, table) -> int:
    with engine.connect() as connection:
        return connection.execute(select(func.count()).select_from(table)).scalar_one()


def saved(client: TestClient, data: dict | None = None, pdf: bytes | None = None) -> str:
    candidate_id = upload(client, pdf)
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json=data or payload())
    assert response.status_code == 200, response.text
    return candidate_id


def test_confirm_persists_structured_data_and_private_pdf(setup) -> None:
    client, engine, root = setup
    pdf = synthetic_pdf()
    candidate_id = upload(client, pdf)
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json=payload())
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "stored", "id": candidate_id, "store_name": "Synthetic Shop",
                               "receipt_date": "2026-10-10", "item_count": 1, "final_total": 9.0}
    assert client.get(f"/api/candidates/{candidate_id}/pdf").status_code == 404
    assert count(engine, receipts) == 1
    assert count(engine, receipt_items) == 1
    assert count(engine, products) == 1
    assert count(engine, categories) == 16
    with engine.connect() as connection:
        receipt = connection.execute(select(receipts)).mappings().one()
        item = connection.execute(select(receipt_items)).mappings().one()
        category = connection.execute(select(categories.c.name).where(categories.c.id == item["category_id"])).scalar_one()
        assert receipt["store_name"] == "Synthetic Shop"
        assert receipt["receipt_date"].isoformat() == "2026-10-10"
        assert receipt["final_total"] == 9
        assert category == "Dairy"
        assert receipt["original_file_path"] == "2026/10/2026-10-10_synthetic-shop.pdf"
        saved = root / "receipts" / receipt["original_file_path"]
        assert saved.read_bytes() == pdf
        assert not (root / "candidates" / f"{candidate_id}.pdf").exists()
    # A repeated request is idempotent even after candidate cleanup.
    assert client.post(f"/api/candidates/{candidate_id}/confirm", json=payload()).json()["id"] == candidate_id
    assert count(engine, receipts) == 1


def test_alias_creation_reuse_and_conflict(setup) -> None:
    client, engine, _ = setup
    first = upload(client, synthetic_pdf(item_line="AYM BRST FZN 2 pcs 4.50 9.00"))
    first_payload = payload("AYM BRST FZN", "Frozen Chicken Breast")
    first_payload["items"][0]["category"] = "Meat & Poultry"
    assert client.post(f"/api/candidates/{first}/confirm", json=first_payload).status_code == 200
    assert count(engine, product_aliases) == 1
    second = upload(client, synthetic_pdf("SECOND SYNTHETIC SHOP", "AYM BRST FZN 2 pcs 4.50 9.00"))
    second_payload = payload("AYM BRST FZN", "AYM BRST FZN")
    second_payload["receipt"]["receipt_number"] = "SYN-102"
    second_payload["receipt"]["store_name"] = "Second Synthetic Shop"
    second_payload["items"][0]["category"] = "Meat & Poultry"
    assert client.post(f"/api/candidates/{second}/confirm", json=second_payload).status_code == 200
    assert count(engine, products) == 1
    with engine.connect() as connection:
        names = connection.execute(select(receipt_items.c.display_name).order_by(receipt_items.c.id)).scalars().all()
        assert names == ["Frozen Chicken Breast", "Frozen Chicken Breast"]
    third = upload(client, synthetic_pdf("THIRD SYNTHETIC SHOP", "AYM BRST FZN 2 pcs 4.50 9.00"))
    conflict = payload("AYM BRST FZN", "Other Product")
    conflict["receipt"]["receipt_number"] = "SYN-103"
    conflict["receipt"]["store_name"] = "Third Synthetic Shop"
    conflict["items"][0]["category"] = "Meat & Poultry"
    response = client.post(f"/api/candidates/{third}/confirm", json=conflict)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "alias_conflict"
    assert client.get(f"/api/candidates/{third}/pdf").status_code == 200
    assert count(engine, receipts) == 2


def test_history_list_order_count_details_and_pdf(setup) -> None:
    client, _, _ = setup
    first_pdf = synthetic_pdf("FIRST SYNTHETIC")
    first = saved(client, pdf=first_pdf)
    second_data = payload("BREAD", "Bread")
    second_data["receipt"]["store_name"] = "Later Synthetic Shop"
    second_data["receipt"]["receipt_date"] = "2026-10-11"
    second_data["items"].append({"raw_name": "MILK", "display_name": "Milk", "quantity": 1,
                                  "unit": "pcs", "unit_price": 2, "line_total": 2, "category": "Dairy"})
    second = saved(client, second_data, synthetic_pdf("SECOND SYNTHETIC"))
    listing = client.get("/api/receipts")
    assert listing.status_code == 200
    assert [row["id"] for row in listing.json()] == [second, first]
    assert listing.json()[0]["item_count"] == 2
    assert listing.json()[1]["currency"] == "MYR"
    detail = client.get(f"/api/receipts/{first}")
    assert detail.status_code == 200
    assert detail.json()["receipt"]["store_name"] == "Synthetic Shop"
    assert detail.json()["items"][0]["display_name"] == "Milk"
    pdf = client.get(f"/api/receipts/{first}/pdf")
    assert pdf.status_code == 200 and pdf.content == first_pdf
    assert pdf.headers["x-content-type-options"] == "nosniff"
    assert client.get("/api/receipts/not-a-uuid").status_code == 422
    assert client.get(f"/api/receipts/{uuid4()}").status_code == 404
    assert client.get(f"/api/receipts/{uuid4()}/pdf").status_code == 404


def test_missing_pdf_and_path_containment(setup) -> None:
    client, engine, root = setup
    receipt_id = saved(client)
    with engine.begin() as connection:
        relative = connection.execute(select(receipts.c.original_file_path)).scalar_one()
    (root / "receipts" / relative).unlink()
    missing = client.get(f"/api/receipts/{receipt_id}/pdf")
    assert missing.status_code == 404 and "missing" in missing.json()["detail"]
    assert client.get(f"/api/receipts/{receipt_id}").status_code == 200
    with engine.begin() as connection:
        connection.execute(receipts.update().values(original_file_path="../outside.pdf"))
    assert client.get(f"/api/receipts/{receipt_id}/pdf").status_code == 409
    assert client.delete(f"/api/receipts/{receipt_id}").status_code == 409


def test_update_metadata_items_product_reuse_and_shared_product(setup) -> None:
    client, engine, _ = setup
    first = saved(client)
    other_data = payload("MILK", "Milk")
    other_data["receipt"]["store_name"] = "Other Synthetic Shop"
    second = saved(client, other_data, synthetic_pdf("OTHER SYNTHETIC"))
    detail = client.get(f"/api/receipts/{first}").json()
    update_data = {"receipt": {**detail["receipt"], "store_name": "Edited Synthetic Shop", "final_total": 12},
                   "items": [{**detail["items"][0], "raw_name": None, "display_name": "Bread", "category": "Bread & Bakery", "line_total": 10},
                             {"display_name": "Milk", "category": "Dairy", "quantity": 1, "unit": "pcs", "unit_price": 2, "line_total": 2}]}
    response = client.put(f"/api/receipts/{first}", json=update_data)
    assert response.status_code == 200, response.text
    assert response.json()["receipt"]["store_name"] == "Edited Synthetic Shop"
    assert {item["display_name"] for item in response.json()["items"]} == {"Bread", "Milk"}
    assert len(response.json()["items"]) == 2
    assert client.get(f"/api/receipts/{second}").json()["items"][0]["display_name"] == "Milk"
    assert count(engine, products) == 2
    with engine.connect() as connection:
        first_product = connection.execute(select(receipt_items.c.product_id).where(receipt_items.c.receipt_id == first,
            receipt_items.c.display_name == "Milk")).scalar_one()
        second_product = connection.execute(select(receipt_items.c.product_id).where(receipt_items.c.receipt_id == second)).scalar_one()
        assert first_product == second_product
    update_data["items"] = [update_data["items"][0]]
    assert client.put(f"/api/receipts/{first}", json=update_data).status_code == 200
    assert len(client.get(f"/api/receipts/{first}").json()["items"]) == 1
    assert client.get("/api/receipts").json()[0]["item_count"] == 1


def test_update_validation_alias_and_rollback(setup, monkeypatch) -> None:
    client, engine, _ = setup
    receipt_id = saved(client)
    original = client.get(f"/api/receipts/{receipt_id}").json()
    changed = {"receipt": dict(original["receipt"]), "items": [dict(original["items"][0])]}
    changed["items"][0]["category"] = "Invalid category"
    assert client.put(f"/api/receipts/{receipt_id}", json=changed).status_code == 422
    changed["items"][0]["category"] = "Dairy"
    changed["items"][0]["line_total"] = -1
    assert client.put(f"/api/receipts/{receipt_id}", json=changed).status_code == 422
    changed["items"][0]["line_total"] = 9
    changed["receipt"]["currency"] = "USD"
    assert client.put(f"/api/receipts/{receipt_id}", json=changed).status_code == 422
    changed["receipt"]["currency"] = "MYR"
    changed["items"][0]["display_name"] = "Fresh Milk"
    assert client.put(f"/api/receipts/{receipt_id}", json=changed).status_code == 200
    assert count(engine, product_aliases) == 1
    assert count(engine, products) == 2
    changed["items"][0]["display_name"] = "Different Milk"
    conflict = client.put(f"/api/receipts/{receipt_id}", json=changed)
    assert conflict.status_code == 409 and conflict.json()["detail"]["code"] == "alias_conflict"
    assert client.get(f"/api/receipts/{receipt_id}").json()["items"][0]["display_name"] == "Fresh Milk"
    def fail(*args):
        raise RuntimeError("synthetic failure")
    monkeypatch.setattr(history, "_product_for_item", fail)
    changed["receipt"]["store_name"] = "Should Roll Back"
    assert client.put(f"/api/receipts/{receipt_id}", json=changed).status_code == 503
    assert client.get(f"/api/receipts/{receipt_id}").json()["receipt"]["store_name"] == "Synthetic Shop"
    assert client.get(f"/api/receipts/{receipt_id}/pdf").status_code == 200


def test_delete_removes_receipt_items_and_pdf_but_not_shared_data(setup) -> None:
    client, engine, root = setup
    first = saved(client, payload("SHORT MILK", "Milk"))
    second_data = payload("MILK", "Milk")
    second_data["receipt"]["store_name"] = "Second Synthetic Shop"
    second = saved(client, second_data, synthetic_pdf("SECOND SYNTHETIC"))
    with engine.connect() as connection:
        relative = connection.execute(select(receipts.c.original_file_path).where(receipts.c.id == first)).scalar_one()
    pdf = root / "receipts" / relative
    assert pdf.exists()
    result = client.delete(f"/api/receipts/{first}")
    assert result.status_code == 200 and not result.json()["pdf_missing"]
    assert not pdf.exists()
    assert client.get(f"/api/receipts/{first}").status_code == 404
    assert [row["id"] for row in client.get("/api/receipts").json()] == [second]
    assert count(engine, receipts) == 1 and count(engine, receipt_items) == 1
    assert count(engine, products) == 1 and count(engine, product_aliases) == 1
    assert count(engine, categories) == 16
    assert client.get(f"/api/receipts/{second}/pdf").status_code == 200
    assert client.delete(f"/api/receipts/{first}").status_code == 404


def test_delete_with_already_missing_pdf(setup) -> None:
    client, engine, root = setup
    receipt_id = saved(client)
    with engine.connect() as connection:
        relative = connection.execute(select(receipts.c.original_file_path)).scalar_one()
    (root / "receipts" / relative).unlink()
    result = client.delete(f"/api/receipts/{receipt_id}")
    assert result.status_code == 200 and result.json()["pdf_missing"]
    assert count(engine, receipts) == 0 and count(engine, receipt_items) == 0


def test_delete_failure_restores_pdf_and_database_record(setup, monkeypatch) -> None:
    client, engine, root = setup
    receipt_id = saved(client)
    with engine.connect() as connection:
        relative = connection.execute(select(receipts.c.original_file_path)).scalar_one()
    pdf = root / "receipts" / relative
    def fail(*args):
        raise RuntimeError("synthetic database failure")
    monkeypatch.setattr(history, "delete", fail)
    assert client.delete(f"/api/receipts/{receipt_id}").status_code == 503
    assert pdf.is_file()
    assert count(engine, receipts) == 1 and count(engine, receipt_items) == 1
    assert client.get(f"/api/receipts/{receipt_id}/pdf").status_code == 200


def test_update_rejects_foreign_or_repeated_item_ids(setup) -> None:
    client, _, _ = setup
    first = saved(client)
    other_data = payload()
    other_data["receipt"]["store_name"] = "Other Synthetic Shop"
    second = saved(client, other_data, synthetic_pdf("SECOND SYNTHETIC"))
    first_detail = client.get(f"/api/receipts/{first}").json()
    foreign_item = client.get(f"/api/receipts/{second}").json()["items"][0]
    submission = {"receipt": first_detail["receipt"], "items": [foreign_item]}
    assert client.put(f"/api/receipts/{first}", json=submission).status_code == 422
    submission["items"] = [first_detail["items"][0], first_detail["items"][0]]
    assert client.put(f"/api/receipts/{first}", json=submission).status_code == 422
    assert len(client.get(f"/api/receipts/{first}").json()["items"]) == 1


def test_duplicate_warning_allows_explicit_continue_and_filename_collision(setup) -> None:
    client, engine, root = setup
    pdf = synthetic_pdf()
    first = upload(client, pdf)
    assert client.post(f"/api/candidates/{first}/confirm", json=payload()).status_code == 200
    second = upload(client, pdf)
    response = client.post(f"/api/candidates/{second}/confirm", json=payload())
    assert response.status_code == 409
    assert response.json()["detail"]["match_kind"] == "exact_file"
    assert count(engine, receipts) == 1
    assert client.get(f"/api/candidates/{second}/pdf").status_code == 200
    duplicate_payload = payload()
    duplicate_payload["allow_duplicate"] = True
    assert client.post(f"/api/candidates/{second}/confirm", json=duplicate_payload).status_code == 200
    assert count(engine, receipts) == 2
    files = list((root / "receipts" / "2026" / "10").glob("*.pdf"))
    assert len(files) == 2
    assert any(second.replace("-", "")[:6] in file.name for file in files)


def test_database_or_file_failure_keeps_candidate_and_rolls_back(setup, monkeypatch) -> None:
    client, engine, root = setup
    candidate_id = upload(client)
    original = persistence._copy_private
    monkeypatch.setattr(persistence, "_copy_private", lambda *_args: (_ for _ in ()).throw(OSError("synthetic failure")))
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json=payload())
    assert response.status_code == 503
    assert client.get(f"/api/candidates/{candidate_id}/pdf").status_code == 200
    assert count(engine, receipts) == 0
    assert not list((root / "receipts").rglob("*.pdf"))
    monkeypatch.setattr(persistence, "_copy_private", original)

    monkeypatch.setattr(persistence, "_product_for_item", lambda *_args: (_ for _ in ()).throw(RuntimeError("synthetic DB failure")))
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json=payload())
    assert response.status_code == 503
    assert client.get(f"/api/candidates/{candidate_id}/pdf").status_code == 200
    assert count(engine, receipts) == 0
    assert count(engine, products) == 0


def test_commit_failure_removes_new_pdf_and_keeps_candidate(setup, monkeypatch) -> None:
    client, engine, root = setup
    candidate_id = upload(client)

    class FailingEngine:
        @contextmanager
        def begin(self):
            with engine.begin() as connection:
                yield connection
                raise RuntimeError("synthetic failure after private PDF copy")

        def dispose(self):
            pass

    monkeypatch.setattr(persistence, "create_engine", lambda *_args, **_kwargs: FailingEngine())
    response = client.post(f"/api/candidates/{candidate_id}/confirm", json=payload())
    assert response.status_code == 503
    assert client.get(f"/api/candidates/{candidate_id}/pdf").status_code == 200
    assert count(engine, receipts) == 0
    assert not list((root / "receipts").rglob("*.pdf"))


def test_metadata_duplicate_is_warning_without_exact_file_match(setup) -> None:
    client, engine, _ = setup
    first = upload(client, synthetic_pdf("FIRST SYNTHETIC SHOP"))
    assert client.post(f"/api/candidates/{first}/confirm", json=payload()).status_code == 200
    second = upload(client, synthetic_pdf("DIFFERENT PDF CONTENT"))
    response = client.post(f"/api/candidates/{second}/confirm", json=payload())
    assert response.status_code == 409
    assert response.json()["detail"]["match_kind"] == "possible_receipt"
    assert count(engine, receipts) == 1


def test_missing_source_values_and_safe_filenames(setup) -> None:
    client, engine, root = setup
    candidate_id = upload(client)
    data = payload()
    data["receipt"].update(store_name=None, receipt_date=None, receipt_number=None, final_total=None, subtotal=None)
    data["items"][0].update(quantity=None, unit=None, unit_price=None, line_total=None)
    assert client.post(f"/api/candidates/{candidate_id}/confirm", json=data).status_code == 200
    with engine.connect() as connection:
        row = connection.execute(select(receipts)).mappings().one()
        assert row["receipt_date"] is None and row["final_total"] is None
        assert row["original_file_path"] == "undated/undated_store.pdf"
        assert (root / "receipts" / row["original_file_path"]).is_file()
    assert future_receipt_filename(None, "../Private\\Store * 🛒") == "undated_private-store.pdf"


def test_migration_from_foundation_and_fresh_database(tmp_path: Path, monkeypatch) -> None:
    for starting_revision in ("0001_foundation", "head"):
        database = tmp_path / f"{starting_revision}.db"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
        command.upgrade(config, starting_revision)
        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{database.as_posix()}")
        assert count(engine, categories) == 16
        assert count(engine, receipts) == 0
        engine.dispose()
