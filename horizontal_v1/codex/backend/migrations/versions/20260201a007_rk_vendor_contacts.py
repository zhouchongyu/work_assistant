from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a007"
down_revision = "20260201a006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rk_vendor",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("director", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=100), nullable=True),
        sa.Column("check", sa.Boolean(), nullable=True),
        sa.Column("check_remark", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("vendor_status1", sa.String(length=50), nullable=True),
        sa.Column("vendor_status2", sa.String(length=50), nullable=True),
        sa.Column("vendor_status3", sa.String(length=50), nullable=True),
        sa.Column("vendor_status4", sa.String(length=50), nullable=True),
        sa.Column("vendor_status5", sa.String(length=50), nullable=True),
        sa.Column("vendor_status6", sa.String(length=50), nullable=True),
        sa.Column("vendor_status7", sa.String(length=50), nullable=True),
        sa.Column("vendor_status8", sa.String(length=50), nullable=True),
        sa.Column("vendor_status9", sa.String(length=50), nullable=True),
        sa.Column("vendor_status10", sa.String(length=50), nullable=True),
        sa.Column("enterprise_id", sa.String(length=50), nullable=True),
        sa.Column("folder_id", sa.String(length=255), nullable=True),
        sa.Column("folder_url", sa.String(length=500), nullable=True),
        sa.Column("delta_link", sa.String(length=500), nullable=True),
        sa.Column("folder_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", "owner_id", name="uq_rk_vendor_name_owner_id"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_vendor_code", "rk_vendor", ["code"], schema="wa_v3")
    op.create_index("ix_rk_vendor_name", "rk_vendor", ["name"], schema="wa_v3")
    op.create_index("ix_rk_vendor_owner_id", "rk_vendor", ["owner_id"], schema="wa_v3")
    op.create_index("ix_rk_vendor_active", "rk_vendor", ["active"], schema="wa_v3")

    op.create_table(
        "rk_vendor_contact",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("postal", sa.String(length=50), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=100), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("vendor_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vendor_id"], ["wa_v3.rk_vendor.id"], name="fk_rk_vendor_contact_vendor_id_rk_vendor"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_vendor_contact_vendor_id", "rk_vendor_contact", ["vendor_id"], schema="wa_v3")

    op.create_table(
        "rk_customer_contact",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("postal", sa.String(length=50), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=100), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["wa_v3.rk_customer.id"], name="fk_rk_customer_contact_customer_id_rk_customer"
        ),
        schema="wa_v3",
    )
    op.create_index("ix_rk_customer_contact_customer_id", "rk_customer_contact", ["customer_id"], schema="wa_v3")


def downgrade() -> None:
    op.drop_index("ix_rk_customer_contact_customer_id", table_name="rk_customer_contact", schema="wa_v3")
    op.drop_table("rk_customer_contact", schema="wa_v3")

    op.drop_index("ix_rk_vendor_contact_vendor_id", table_name="rk_vendor_contact", schema="wa_v3")
    op.drop_table("rk_vendor_contact", schema="wa_v3")

    op.drop_index("ix_rk_vendor_active", table_name="rk_vendor", schema="wa_v3")
    op.drop_index("ix_rk_vendor_owner_id", table_name="rk_vendor", schema="wa_v3")
    op.drop_index("ix_rk_vendor_name", table_name="rk_vendor", schema="wa_v3")
    op.drop_index("ix_rk_vendor_code", table_name="rk_vendor", schema="wa_v3")
    op.drop_table("rk_vendor", schema="wa_v3")

