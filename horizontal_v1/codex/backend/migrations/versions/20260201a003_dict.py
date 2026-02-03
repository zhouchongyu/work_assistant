from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a003"
down_revision = "20260201a002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dict_type",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("page", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="wa_v3",
    )
    op.create_index("ix_dict_type_key", "dict_type", ["key"], schema="wa_v3")

    op.create_table(
        "dict_info",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=True),
        sa.Column("order_num", sa.Integer(), server_default="0", nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("field_name", sa.String(length=255), nullable=True),
        sa.Column("is_show", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_process", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["type_id"], ["wa_v3.dict_type.id"], name="fk_dict_info_type_id_dict_type"),
        schema="wa_v3",
    )
    op.create_index("ix_dict_info_type_id", "dict_info", ["type_id"], schema="wa_v3")


def downgrade() -> None:
    op.drop_index("ix_dict_info_type_id", table_name="dict_info", schema="wa_v3")
    op.drop_table("dict_info", schema="wa_v3")
    op.drop_index("ix_dict_type_key", table_name="dict_type", schema="wa_v3")
    op.drop_table("dict_type", schema="wa_v3")

