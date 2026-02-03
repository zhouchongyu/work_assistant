from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260131a001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS wa_v3")
    op.execute("CREATE SCHEMA IF NOT EXISTS wa_v3_migration")

    op.create_table(
        "id_map",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("legacy_system", sa.String(length=50), nullable=False),
        sa.Column("legacy_table", sa.String(length=100), nullable=False),
        sa.Column("legacy_id", sa.String(length=100), nullable=False),
        sa.Column("new_table", sa.String(length=100), nullable=False),
        sa.Column("new_id", sa.BigInteger(), nullable=False),
        sa.Column("natural_key", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="wa_v3_migration",
    )
    op.create_index(
        "ix_id_map_legacy",
        "id_map",
        ["legacy_system", "legacy_table", "legacy_id"],
        unique=True,
        schema="wa_v3_migration",
    )
    op.create_index(
        "ix_id_map_new",
        "id_map",
        ["new_table", "new_id"],
        unique=False,
        schema="wa_v3_migration",
    )


def downgrade() -> None:
    op.drop_index("ix_id_map_new", table_name="id_map", schema="wa_v3_migration")
    op.drop_index("ix_id_map_legacy", table_name="id_map", schema="wa_v3_migration")
    op.drop_table("id_map", schema="wa_v3_migration")
    op.execute("DROP SCHEMA IF EXISTS wa_v3_migration")
    op.execute("DROP SCHEMA IF EXISTS wa_v3")

