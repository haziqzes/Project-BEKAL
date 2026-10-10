"""Receipt persistence tables and predefined categories.

Revision ID: 0002_receipt_persistence
Revises: 0001_foundation
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_receipt_persistence"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None

# Snapshot the V0.1 category set so future app changes do not alter this migration.
CATEGORY_NAMES = (
    "Meat & Poultry", "Seafood", "Vegetables", "Fruit", "Dairy", "Eggs",
    "Rice & Grains", "Bread & Bakery", "Drinks", "Snacks", "Frozen Food",
    "Canned / Packaged Food", "Condiments", "Household", "Personal Care", "Other",
)


def upgrade() -> None:
    op.create_table(
        "categories", sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "products", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("canonical_name", sa.String(255), nullable=False),
        sa.Column("name_key", sa.String(255), nullable=False, unique=True),
        sa.Column("default_category_id", sa.Integer, sa.ForeignKey("categories.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "product_aliases", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_alias", sa.String(255), nullable=False),
        sa.Column("alias_key", sa.String(255), nullable=False, unique=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "receipts", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("store_name", sa.String(255)),
        sa.Column("receipt_date", sa.Date),
        sa.Column("receipt_number", sa.String(120)),
        sa.Column("payment_method", sa.String(120)),
        sa.Column("subtotal", sa.Numeric(12, 2)),
        sa.Column("discount_total", sa.Numeric(12, 2)),
        sa.Column("tax_total", sa.Numeric(12, 2)),
        sa.Column("final_total", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("original_file_path", sa.Text, nullable=False, unique=True),
        sa.Column("file_sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "receipt_items", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("receipt_id", sa.String(36), sa.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("source_name", sa.String(255)),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3)),
        sa.Column("unit", sa.String(30)),
        sa.Column("unit_price", sa.Numeric(12, 2)),
        sa.Column("line_total", sa.Numeric(12, 2)),
        sa.Column("review_flag", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    category_table = sa.table("categories", sa.column("name", sa.String(80)))
    op.bulk_insert(category_table, [{"name": name} for name in CATEGORY_NAMES])


def downgrade() -> None:
    op.drop_table("receipt_items")
    op.drop_table("receipts")
    op.drop_table("product_aliases")
    op.drop_table("products")
    op.drop_table("categories")
