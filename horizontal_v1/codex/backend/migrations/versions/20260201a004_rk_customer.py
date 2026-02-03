from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a004"
down_revision = "20260201a003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rk_customer",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("director", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=100), nullable=True),
        sa.Column("check", sa.Boolean(), nullable=True),
        sa.Column("check_remark", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("customer_status1", sa.String(length=50), nullable=True),
        sa.Column("customer_status2", sa.String(length=50), nullable=True),
        sa.Column("customer_status3", sa.String(length=50), nullable=True),
        sa.Column("customer_status4", sa.String(length=50), nullable=True),
        sa.Column("customer_status5", sa.String(length=50), nullable=True),
        sa.Column("customer_status6", sa.String(length=50), nullable=True),
        sa.Column("customer_status7", sa.String(length=50), nullable=True),
        sa.Column("customer_status8", sa.String(length=50), nullable=True),
        sa.Column("customer_status9", sa.String(length=50), nullable=True),
        sa.Column("customer_status10", sa.String(length=50), nullable=True),
        sa.Column("enterprise_id", sa.String(length=50), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="wa_v3",
    )
    op.create_index("ix_rk_customer_code", "rk_customer", ["code"], schema="wa_v3")
    op.create_index("ix_rk_customer_name", "rk_customer", ["name"], schema="wa_v3")
    op.create_index("ix_rk_customer_owner_id", "rk_customer", ["owner_id"], schema="wa_v3")
    op.create_index("ix_rk_customer_active", "rk_customer", ["active"], schema="wa_v3")


def downgrade() -> None:
    op.drop_index("ix_rk_customer_active", table_name="rk_customer", schema="wa_v3")
    op.drop_index("ix_rk_customer_owner_id", table_name="rk_customer", schema="wa_v3")
    op.drop_index("ix_rk_customer_name", table_name="rk_customer", schema="wa_v3")
    op.drop_index("ix_rk_customer_code", table_name="rk_customer", schema="wa_v3")
    op.drop_table("rk_customer", schema="wa_v3")

