from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a002"
down_revision = "20260131a001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sys_user",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("password_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("nick_name", sa.String(length=100), nullable=True),
        sa.Column("head_img", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("socket_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username", name="uq_sys_user_username"),
        schema="wa_v3",
    )
    op.create_index("ix_sys_user_username", "sys_user", ["username"], schema="wa_v3")

    op.create_table(
        "sys_role",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("relevance", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_sys_role_name"),
        sa.UniqueConstraint("label", name="uq_sys_role_label"),
        schema="wa_v3",
    )
    op.create_index("ix_sys_role_name", "sys_role", ["name"], schema="wa_v3")

    op.create_table(
        "sys_user_role",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "role_id", name="pk_sys_user_role"),
        sa.ForeignKeyConstraint(["user_id"], ["wa_v3.sys_user.id"], name="fk_sys_user_role_user_id_sys_user"),
        sa.ForeignKeyConstraint(["role_id"], ["wa_v3.sys_role.id"], name="fk_sys_user_role_role_id_sys_role"),
        schema="wa_v3",
    )

    op.create_table(
        "sys_menu",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("router", sa.String(length=255), nullable=True),
        sa.Column("perms", sa.Text(), nullable=True),
        sa.Column("type", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=True),
        sa.Column("order_num", sa.Integer(), server_default="0", nullable=False),
        sa.Column("view_path", sa.String(length=255), nullable=True),
        sa.Column("keep_alive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_show", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="wa_v3",
    )
    op.create_index("ix_sys_menu_parent_id", "sys_menu", ["parent_id"], schema="wa_v3")

    op.create_table(
        "sys_role_menu",
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("menu_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("role_id", "menu_id", name="pk_sys_role_menu"),
        sa.ForeignKeyConstraint(["role_id"], ["wa_v3.sys_role.id"], name="fk_sys_role_menu_role_id_sys_role"),
        sa.ForeignKeyConstraint(["menu_id"], ["wa_v3.sys_menu.id"], name="fk_sys_role_menu_menu_id_sys_menu"),
        schema="wa_v3",
    )


def downgrade() -> None:
    op.drop_table("sys_role_menu", schema="wa_v3")
    op.drop_index("ix_sys_menu_parent_id", table_name="sys_menu", schema="wa_v3")
    op.drop_table("sys_menu", schema="wa_v3")
    op.drop_table("sys_user_role", schema="wa_v3")
    op.drop_index("ix_sys_role_name", table_name="sys_role", schema="wa_v3")
    op.drop_table("sys_role", schema="wa_v3")
    op.drop_index("ix_sys_user_username", table_name="sys_user", schema="wa_v3")
    op.drop_table("sys_user", schema="wa_v3")

