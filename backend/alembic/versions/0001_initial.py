from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_role = sa.Enum("ADMIN", "STAFF", "CUSTOMER", name="user_role")
    category_status = sa.Enum("ACTIVE", "INACTIVE", name="category_status")
    product_status = sa.Enum("ACTIVE", "INACTIVE", name="product_status")
    order_status = sa.Enum("PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED", name="order_status")
    payment_status = sa.Enum("PENDING", "PAID", "FAILED", "REFUNDED", name="payment_status")
    payment_method = sa.Enum("CARD", "UPI", "CASH", "BANK_TRANSFER", name="payment_method")
    notification_type = sa.Enum("ORDER", "STOCK", "PAYMENT", name="notification_type")
    for e in [user_role, category_status, product_status, order_status, payment_status, payment_method, notification_type]:
        e.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("profile_image", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", category_status, nullable=False),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    op.create_index("ix_categories_status", "categories", ["status"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sku", sa.String(80), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("status", product_status, nullable=False),
        sa.Column("image_path", sa.String(500)),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_price_status", "products", ["price", "status"])

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_stock", sa.Integer(), nullable=False),
        sa.Column("minimum_stock_level", sa.Integer(), nullable=False),
        sa.Column("maximum_stock_level", sa.Integer(), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("product_id"),
    )
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"], unique=True)

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_customer_status", "orders", ["customer_id", "status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", payment_method, nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", payment_status, nullable=False),
        sa.UniqueConstraint("order_id", name="uq_payment_order"),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("customer_id", "product_id", "order_id", name="uq_review_customer_product_order"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
    )
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])
    op.create_index("ix_reviews_customer_id", "reviews", ["customer_id"])
    op.create_index("ix_reviews_order_id", "reviews", ["order_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", notification_type, nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    op.create_table(
        "file_uploads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("stored_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("stored_name"),
    )
    op.create_index("ix_file_uploads_owner_id", "file_uploads", ["owner_id"])


def downgrade():
    for table in ["file_uploads", "notifications", "reviews", "payments", "order_items", "orders", "inventory", "products", "categories", "users"]:
        op.drop_table(table)
    for name in ["notification_type", "payment_method", "payment_status", "order_status", "product_status", "category_status", "user_role"]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
