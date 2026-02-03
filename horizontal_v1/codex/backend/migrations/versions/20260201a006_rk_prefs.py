from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a006"
down_revision = "20260201a005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rk_customer_column",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("column_info", sa.Text(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("owner_id", "name", name="uq_rk_customer_column_owner_id_name"),
        schema="wa_v3",
    )
    op.create_index(
        "ix_rk_customer_column_name", "rk_customer_column", ["name"], unique=False, schema="wa_v3"
    )
    op.create_index(
        "ix_rk_customer_column_owner_id", "rk_customer_column", ["owner_id"], unique=False, schema="wa_v3"
    )

    op.create_table(
        "rk_active",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_rk_active_user_id"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_active_user_id", "rk_active", ["user_id"], unique=True, schema="wa_v3")


def downgrade() -> None:
    op.drop_index("ix_rk_active_user_id", table_name="rk_active", schema="wa_v3")
    op.drop_table("rk_active", schema="wa_v3")

    op.drop_index("ix_rk_customer_column_owner_id", table_name="rk_customer_column", schema="wa_v3")
    op.drop_index("ix_rk_customer_column_name", table_name="rk_customer_column", schema="wa_v3")
    op.drop_table("rk_customer_column", schema="wa_v3")

