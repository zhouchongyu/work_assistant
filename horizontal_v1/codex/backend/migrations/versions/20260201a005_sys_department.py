from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a005"
down_revision = "20260201a004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sys_department",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("order_num", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="wa_v3",
    )
    op.create_index("ix_sys_department_parent_id", "sys_department", ["parent_id"], schema="wa_v3")

    op.create_foreign_key(
        "fk_sys_user_department_id_sys_department",
        source_table="sys_user",
        referent_table="sys_department",
        local_cols=["department_id"],
        remote_cols=["id"],
        source_schema="wa_v3",
        referent_schema="wa_v3",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_sys_user_department_id_sys_department",
        table_name="sys_user",
        schema="wa_v3",
        type_="foreignkey",
    )
    op.drop_index("ix_sys_department_parent_id", table_name="sys_department", schema="wa_v3")
    op.drop_table("sys_department", schema="wa_v3")

