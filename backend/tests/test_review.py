from app.extraction import ExtractionData, ItemData, ReceiptData
from app.review import CATEGORIES, prepare_item, prepare_review


def extracted(items: list[ItemData], **receipt_fields) -> ExtractionData:
    return ExtractionData(extraction_method="embedded_text", extraction_status="extracted",
                          receipt=ReceiptData(**receipt_fields), items=items)


def test_conservative_name_category_and_quantity_inference() -> None:
    item = prepare_item(ItemData(display_name="  MILK 2L  ", unit_price=4.25, line_total=8.5))
    assert item.raw_name == "  MILK 2L  "
    assert item.display_name == "Milk 2L"
    assert item.category == "Dairy"
    assert item.quantity == 2
    assert item.unit == "l"
    assert item.unit_price == 4.25
    assert "Line total is unknown" not in item.warnings

    package_size = prepare_item(ItemData(display_name="MILK 2L", line_total=8.5))
    assert package_size.quantity is None
    assert package_size.unit is None

    uncertain = prepare_item(ItemData(display_name="ABC 123", line_total=3.0))
    assert uncertain.display_name == "ABC 123"
    assert uncertain.category == "Other"
    assert uncertain.quantity is None
    assert "Category needs review" in uncertain.warnings
    assert "Quantity or unit is unknown" in uncertain.warnings
    assert len(CATEGORIES) == 16


def test_totals_and_missing_fields_are_flagged() -> None:
    items = [ItemData(display_name="MILK", quantity=2, unit="pcs", unit_price=4.5, line_total=9),
             ItemData(display_name="BREAD", quantity=1, unit="pcs", unit_price=3.5, line_total=3.5)]
    result = prepare_review(extracted(items, store_name="SHOP", receipt_date="2026-10-10", subtotal=12.5, final_total=12.5))
    assert result.calculated_items_total == 12.5
    assert result.reconciliation == "Items match subtotal"
    assert not result.warnings

    mismatch = prepare_review(extracted(items, subtotal=13))
    assert mismatch.reconciliation == "Items do not match subtotal"
    assert "Store or date needs review" in mismatch.warnings

    adjusted = prepare_review(extracted(items, subtotal=12.5, discount_total=1, tax_total=0.5, final_total=12))
    assert adjusted.reconciliation == "Items and receipt total reconcile"
    incomplete_adjustment = prepare_review(extracted(items, subtotal=12.5, final_total=12))
    assert "needs review" in incomplete_adjustment.reconciliation

    incomplete = prepare_review(extracted([ItemData(display_name="MILK")], final_total=9))
    assert incomplete.calculated_items_total is None
    assert "Cannot compare" in incomplete.reconciliation


def test_manual_fallback_starts_without_fabricated_data() -> None:
    result = prepare_review(ExtractionData(extraction_method="ocr", extraction_status="no_data",
                                           receipt=ReceiptData(), items=[]))
    assert result.items == []
    assert result.receipt.store_name is None
    assert result.calculated_items_total is None
    assert any("manually" in warning for warning in result.warnings)
