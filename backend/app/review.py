"""Conservative, temporary review preparation for extracted receipts."""

import re
from decimal import Decimal

from pydantic import BaseModel

from app.extraction import ExtractionData, ItemData, ReceiptData


CATEGORIES = (
    "Meat & Poultry", "Seafood", "Vegetables", "Fruit", "Dairy", "Eggs",
    "Rice & Grains", "Bread & Bakery", "Drinks", "Snacks", "Frozen Food",
    "Canned / Packaged Food", "Condiments", "Household", "Personal Care", "Other",
)

# Match whole words only. Ambiguous names stay in Other for human review.
CATEGORY_WORDS = {
    "Meat & Poultry": ("chicken", "beef", "lamb", "pork"),
    "Seafood": ("fish", "prawn", "shrimp", "squid"),
    "Vegetables": ("carrot", "onion", "potato", "tomato", "spinach"),
    "Fruit": ("apple", "banana", "orange", "mango"),
    "Dairy": ("milk", "cheese", "yogurt", "butter"),
    "Eggs": ("egg", "eggs"),
    "Rice & Grains": ("rice", "oat", "oats", "flour"),
    "Bread & Bakery": ("bread", "bun", "buns"),
    "Drinks": ("water", "juice", "coffee", "tea"),
    "Snacks": ("biscuit", "biscuits", "chips", "chocolate"),
    "Frozen Food": ("frozen",),
    "Canned / Packaged Food": ("canned",),
    "Condiments": ("salt", "sugar", "sauce", "ketchup"),
    "Household": ("detergent", "tissue"),
    "Personal Care": ("shampoo", "toothpaste", "deodorant"),
}
QUANTITY_IN_NAME = re.compile(r"(?:^|\s)(\d+(?:\.\d+)?)\s*(kg|g|ml|l|pcs|pc|packs?|units?)\b", re.I)


class ReviewItem(BaseModel):
    raw_name: str
    display_name: str
    quantity: float | None
    unit: str | None
    unit_price: float | None
    line_total: float | None
    category: str
    warnings: list[str]


class ReviewData(BaseModel):
    receipt: ReceiptData
    items: list[ReviewItem]
    warnings: list[str]
    calculated_items_total: float | None
    reconciliation: str


def _money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def prepare_item(item: ItemData) -> ReviewItem:
    raw = item.display_name
    name = " ".join(raw.split()).strip(" -_*")
    category = "Other"
    for candidate, words in CATEGORY_WORDS.items():
        if any(re.search(rf"\b{re.escape(word)}\b", name, re.I) for word in words):
            category = candidate
            break
    if category != "Other" and (name.isupper() or name.islower()):
        name = name.title()
    quantity, unit = item.quantity, item.unit
    if quantity is None or unit is None:
        match = QUANTITY_IN_NAME.search(name)
        if (match and item.unit_price is not None and item.line_total is not None
                and abs(_money(float(match.group(1)) * item.unit_price) - _money(item.line_total)) <= Decimal("0.01")):
            if quantity is None:
                quantity = float(match.group(1))
            if unit is None:
                unit = match.group(2).lower()
    warnings = []
    if not name:
        warnings.append("Product name needs review")
    if category == "Other":
        warnings.append("Category needs review")
    if quantity is None or unit is None:
        warnings.append("Quantity or unit is unknown")
    if item.line_total is None:
        warnings.append("Line total is unknown")
    if (quantity is not None and item.unit_price is not None and item.line_total is not None
            and abs(_money(quantity * item.unit_price) - _money(item.line_total)) > Decimal("0.01")):
        warnings.append("Quantity × unit price differs from line total")
    return ReviewItem(raw_name=raw, display_name=name, quantity=quantity, unit=unit,
                      unit_price=item.unit_price, line_total=item.line_total,
                      category=category, warnings=warnings)


def prepare_review(extraction: ExtractionData) -> ReviewData:
    receipt = extraction.receipt
    items = [prepare_item(item) for item in extraction.items]
    warnings = []
    if extraction.extraction_status == "no_data" or not items:
        warnings.append("No usable item rows; enter receipt data manually")
    if not receipt.store_name or not receipt.receipt_date:
        warnings.append("Store or date needs review")
    complete = bool(items) and all(item.line_total is not None for item in items)
    calculated = float(sum((_money(item.line_total) for item in items if item.line_total is not None), Decimal(0))) if complete else None
    if calculated is None:
        reconciliation = "Cannot compare totals until every item has a line total"
    elif receipt.subtotal is not None:
        if abs(_money(calculated) - _money(receipt.subtotal)) > Decimal("0.01"):
            reconciliation = "Items do not match subtotal"
        elif receipt.final_total is None or abs(_money(receipt.subtotal) - _money(receipt.final_total)) <= Decimal("0.01"):
            reconciliation = "Items match subtotal"
        elif receipt.discount_total is None or receipt.tax_total is None:
            reconciliation = "Items match subtotal; receipt total needs review because discount or tax is unknown"
        elif abs(_money(receipt.subtotal) - _money(receipt.discount_total) + _money(receipt.tax_total) - _money(receipt.final_total)) <= Decimal("0.01"):
            reconciliation = "Items and receipt total reconcile"
        else:
            reconciliation = "Subtotal, discount, tax, and receipt total do not reconcile"
    elif receipt.final_total is not None:
        reconciliation = "Items match receipt total directly" if abs(_money(calculated) - _money(receipt.final_total)) <= Decimal("0.01") else "Items do not match receipt total; check discounts and tax"
    else:
        reconciliation = "Receipt total is unknown"
    if any(marker in reconciliation for marker in ("do not match", "unknown", "Cannot", "do not reconcile", "needs review")):
        warnings.append(reconciliation)
    return ReviewData(receipt=receipt, items=items, warnings=warnings,
                      calculated_items_total=calculated, reconciliation=reconciliation)
