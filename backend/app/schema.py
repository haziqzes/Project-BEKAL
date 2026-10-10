"""Phase 4 relational receipt schema. PDFs remain in private file storage."""

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer, MetaData, Numeric,
    String, Table, Text, func,
)

metadata = MetaData()

categories = Table(
    "categories", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(80), nullable=False, unique=True),
)

products = Table(
    "products", metadata,
    Column("id", String(36), primary_key=True),
    Column("canonical_name", String(255), nullable=False),
    Column("name_key", String(255), nullable=False, unique=True),
    Column("default_category_id", Integer, ForeignKey("categories.id"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

product_aliases = Table(
    "product_aliases", metadata,
    Column("id", String(36), primary_key=True),
    Column("source_alias", String(255), nullable=False),
    Column("alias_key", String(255), nullable=False, unique=True),
    Column("product_id", String(36), ForeignKey("products.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

receipts = Table(
    "receipts", metadata,
    Column("id", String(36), primary_key=True),
    Column("store_name", String(255), nullable=True),
    Column("receipt_date", Date, nullable=True),
    Column("receipt_number", String(120), nullable=True),
    Column("payment_method", String(120), nullable=True),
    Column("subtotal", Numeric(12, 2), nullable=True),
    Column("discount_total", Numeric(12, 2), nullable=True),
    Column("tax_total", Numeric(12, 2), nullable=True),
    Column("final_total", Numeric(12, 2), nullable=True),
    Column("currency", String(3), nullable=False),
    Column("original_file_path", Text, nullable=False, unique=True),
    Column("file_sha256", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

receipt_items = Table(
    "receipt_items", metadata,
    Column("id", String(36), primary_key=True),
    Column("receipt_id", String(36), ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
    Column("product_id", String(36), ForeignKey("products.id"), nullable=False),
    Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
    Column("source_name", String(255), nullable=True),
    Column("display_name", String(255), nullable=False),
    Column("quantity", Numeric(12, 3), nullable=True),
    Column("unit", String(30), nullable=True),
    Column("unit_price", Numeric(12, 2), nullable=True),
    Column("line_total", Numeric(12, 2), nullable=True),
    Column("review_flag", Boolean, nullable=False, server_default="false"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
