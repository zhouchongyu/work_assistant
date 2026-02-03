from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260201a008"
down_revision = "20260201a007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rk_supply",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_id", sa.String(length=255), nullable=True),
        sa.Column("file_md5", sa.String(length=255), nullable=True),
        sa.Column("file_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("vendor_id", sa.BigInteger(), nullable=True),
        sa.Column("vendor_contact_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("supply_user_name", sa.String(length=100), nullable=True),
        sa.Column("supply_user_age", sa.String(length=50), nullable=True),
        sa.Column("supply_user_gender", sa.String(length=50), nullable=True),
        sa.Column("supply_user_citizenship", sa.String(length=50), nullable=True),
        sa.Column("supply_birthday", sa.String(length=50), nullable=True),
        sa.Column("name_pinyin", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("status_detail", sa.String(length=100), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("skill_scores", sa.Text(), nullable=True),
        sa.Column("resume_res", sa.Text(), nullable=True),
        sa.Column("case_status", sa.String(length=100), nullable=True),
        sa.Column("audition_date", sa.String(length=100), nullable=True),
        sa.Column("audition_idea", sa.String(length=100), nullable=True),
        sa.Column("result_expected_date", sa.String(length=100), nullable=True),
        sa.Column("audition_time", sa.String(length=100), nullable=True),
        sa.Column("nearest_station", sa.String(length=100), nullable=True),
        sa.Column("work_location", sa.String(length=255), nullable=True),
        sa.Column("work_mode", sa.String(length=100), nullable=True),
        sa.Column("specialty", sa.String(length=200), nullable=True),
        sa.Column("years_of_work", sa.Float(), nullable=True),
        sa.Column("start_work_date", sa.String(length=50), nullable=True),
        sa.Column("available_date", sa.String(length=100), nullable=True),
        sa.Column("skillx", sa.Text(), nullable=True),
        sa.Column("skilly", sa.Text(), nullable=True),
        sa.Column("skillz", sa.Text(), nullable=True),
        sa.Column("father_skill", sa.String(length=255), nullable=True),
        sa.Column("japanese_level", sa.String(length=50), nullable=True),
        sa.Column("english_level", sa.String(length=50), nullable=True),
        sa.Column("japanese_level_ai", sa.String(length=100), nullable=True),
        sa.Column("english_level_ai", sa.String(length=100), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("role_level", sa.String(length=100), nullable=True),
        sa.Column("role_level_reason", sa.Text(), nullable=True),
        sa.Column("analysis_version", sa.String(length=100), nullable=True),
        sa.Column("analysis_status", sa.String(length=100), nullable=True),
        sa.Column("contact_analysis_status", sa.String(length=100), nullable=True),
        sa.Column("duplicate_status", sa.Integer(), nullable=True),
        sa.Column("duplicate_content", sa.String(length=255), nullable=True),
        sa.Column("error_status", sa.Text(), nullable=True),
        sa.Column("content_confirm", sa.Integer(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("acdtc", sa.Boolean(), nullable=True),
        sa.Column("contracted_member", sa.Boolean(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("price_update", sa.Integer(), nullable=True),
        sa.Column("price_original", sa.Integer(), nullable=True),
        sa.Column("price_update_task_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("task_status", sa.String(length=32), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code", name="uq_rk_supply_code"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_supply_name", "rk_supply", ["name"], schema="wa_v3")
    op.create_index("ix_rk_supply_vendor_id", "rk_supply", ["vendor_id"], schema="wa_v3")
    op.create_index("ix_rk_supply_user_id", "rk_supply", ["user_id"], schema="wa_v3")
    op.create_index("ix_rk_supply_owner_id", "rk_supply", ["owner_id"], schema="wa_v3")
    op.create_index("ix_rk_supply_active", "rk_supply", ["active"], schema="wa_v3")
    op.create_index("ix_rk_supply_analysis_status", "rk_supply", ["analysis_status"], schema="wa_v3")
    op.create_index("ix_rk_supply_file_md5", "rk_supply", ["file_md5"], schema="wa_v3")

    op.create_table(
        "rk_supply_ai",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("supply_id", sa.BigInteger(), nullable=False),
        sa.Column("work_experience", sa.JSON(), nullable=True),
        sa.Column("basic", sa.JSON(), nullable=True),
        sa.Column("x_raw", sa.JSON(), nullable=True),
        sa.Column("y_raw", sa.JSON(), nullable=True),
        sa.Column("z_raw", sa.JSON(), nullable=True),
        sa.Column("x_data", sa.JSON(), nullable=True),
        sa.Column("y_data", sa.JSON(), nullable=True),
        sa.Column("z_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["supply_id"], ["wa_v3.rk_supply.id"], name="fk_rk_supply_ai_supply_id_rk_supply"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_supply_ai_supply_id", "rk_supply_ai", ["supply_id"], schema="wa_v3")

    op.create_table(
        "rk_demand",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("customer_contact_id", sa.BigInteger(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("work_location", sa.String(length=255), nullable=True),
        sa.Column("work_mode", sa.String(length=255), nullable=True),
        sa.Column("skillx", sa.Text(), nullable=True),
        sa.Column("skilly", sa.Text(), nullable=True),
        sa.Column("skillz", sa.Text(), nullable=True),
        sa.Column("japanese_level", sa.String(length=255), nullable=True),
        sa.Column("english_level", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("father_skill", sa.String(length=255), nullable=True),
        sa.Column("change_status", sa.Integer(), nullable=True),
        sa.Column("unit_price_max", sa.Integer(), nullable=True),
        sa.Column("work_percent", sa.Integer(), nullable=True),
        sa.Column("citizenship", sa.String(length=255), nullable=True),
        sa.Column("role_list", sa.JSON(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("have_match", sa.Boolean(), nullable=True),
        sa.Column("analysis_status", sa.String(length=100), nullable=True),
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
    op.create_index("ix_rk_demand_code", "rk_demand", ["code"], schema="wa_v3")
    op.create_index("ix_rk_demand_customer_id", "rk_demand", ["customer_id"], schema="wa_v3")
    op.create_index("ix_rk_demand_owner_id", "rk_demand", ["owner_id"], schema="wa_v3")
    op.create_index("ix_rk_demand_active", "rk_demand", ["active"], schema="wa_v3")
    op.create_index("ix_rk_demand_analysis_status", "rk_demand", ["analysis_status"], schema="wa_v3")

    op.create_table(
        "rk_supply_demand_link",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("supply_id", sa.BigInteger(), nullable=True),
        sa.Column("demand_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("k", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("supply_demand_status1", sa.String(length=50), nullable=True),
        sa.Column("supply_demand_status2", sa.String(length=50), nullable=True),
        sa.Column("supply_demand_status3", sa.String(length=50), nullable=True),
        sa.Column("supply_demand_status4", sa.String(length=50), nullable=True),
        sa.Column("supply_demand_status5", sa.String(length=50), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("tag", sa.Boolean(), nullable=True),
        sa.Column("tag_reason", sa.Text(), nullable=True),
        sa.Column("demand_text", sa.Text(), nullable=True),
        sa.Column("years", sa.Integer(), nullable=True),
        sa.Column("father_skill", sa.String(length=255), nullable=True),
        sa.Column("demand_role", sa.String(length=255), nullable=True),
        sa.Column("demand_version", sa.Integer(), nullable=True),
        sa.Column("supply_version", sa.Integer(), nullable=True),
        sa.Column("warning_msg", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["supply_id"], ["wa_v3.rk_supply.id"], name="fk_rk_supply_demand_link_supply_id_rk_supply"),
        sa.ForeignKeyConstraint(["demand_id"], ["wa_v3.rk_demand.id"], name="fk_rk_supply_demand_link_demand_id_rk_demand"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_supply_demand_link_supply_id", "rk_supply_demand_link", ["supply_id"], schema="wa_v3")
    op.create_index("ix_rk_supply_demand_link_demand_id", "rk_supply_demand_link", ["demand_id"], schema="wa_v3")
    op.create_index("ix_rk_supply_demand_link_active", "rk_supply_demand_link", ["active"], schema="wa_v3")
    op.create_index("ix_rk_supply_demand_link_supply_demand_status3", "rk_supply_demand_link", ["supply_demand_status3"], schema="wa_v3")
    op.create_index("ix_rk_supply_demand_link_demand_role", "rk_supply_demand_link", ["demand_role"], schema="wa_v3")
    op.create_index("ix_rk_supply_demand_link_demand_version", "rk_supply_demand_link", ["demand_version"], schema="wa_v3")

    op.create_table(
        "rk_case_status",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("case_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["wa_v3.rk_supply_demand_link.id"], name="fk_rk_case_status_case_id_rk_supply_demand_link"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_case_status_case_id", "rk_case_status", ["case_id"], schema="wa_v3")
    op.create_index("ix_rk_case_status_active", "rk_case_status", ["active"], schema="wa_v3")

    op.create_table(
        "rk_match_res",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("demand_id", sa.BigInteger(), nullable=False),
        sa.Column("supply_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("warning_msg", sa.JSON(), nullable=True),
        sa.Column("demand_role", sa.String(length=255), nullable=True),
        sa.Column("years_data", sa.JSON(), nullable=True),
        sa.Column("demand_version", sa.Integer(), nullable=True),
        sa.Column("supply_version", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("msg", sa.JSON(), nullable=True),
        sa.Column("reject_type", sa.String(length=100), nullable=True),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["demand_id"], ["wa_v3.rk_demand.id"], name="fk_rk_match_res_demand_id_rk_demand"),
        sa.ForeignKeyConstraint(["supply_id"], ["wa_v3.rk_supply.id"], name="fk_rk_match_res_supply_id_rk_supply"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_match_res_demand_id", "rk_match_res", ["demand_id"], schema="wa_v3")
    op.create_index("ix_rk_match_res_supply_id", "rk_match_res", ["supply_id"], schema="wa_v3")
    op.create_index("ix_rk_match_res_demand_role", "rk_match_res", ["demand_role"], schema="wa_v3")
    op.create_index("ix_rk_match_res_demand_version", "rk_match_res", ["demand_version"], schema="wa_v3")
    op.create_index("ix_rk_match_res_type", "rk_match_res", ["type"], schema="wa_v3")

    op.create_table(
        "rk_llm_data",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("demand_id", sa.BigInteger(), nullable=True),
        sa.Column("supply_id", sa.BigInteger(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=True),
        sa.Column("res", sa.JSON(), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("special", sa.String(length=255), nullable=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("third_id", sa.BigInteger(), nullable=True),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("demand_version", sa.Integer(), nullable=True),
        sa.Column("supply_version", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="wa_v3",
    )
    op.create_index("ix_rk_llm_data_demand_id", "rk_llm_data", ["demand_id"], schema="wa_v3")
    op.create_index("ix_rk_llm_data_supply_id", "rk_llm_data", ["supply_id"], schema="wa_v3")
    op.create_index("ix_rk_llm_data_event_type", "rk_llm_data", ["event_type"], schema="wa_v3")
    op.create_index("ix_rk_llm_data_parent_id", "rk_llm_data", ["parent_id"], schema="wa_v3")
    op.create_index("ix_rk_llm_data_third_id", "rk_llm_data", ["third_id"], schema="wa_v3")

    op.create_table(
        "rk_notice",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("receiver_id", sa.BigInteger(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("from_user", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
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
    op.create_index("ix_rk_notice_receiver_id", "rk_notice", ["receiver_id"], schema="wa_v3")
    op.create_index("ix_rk_notice_is_read", "rk_notice", ["is_read"], schema="wa_v3")
    op.create_index("ix_rk_notice_active", "rk_notice", ["active"], schema="wa_v3")
    op.create_index("ix_rk_notice_type", "rk_notice", ["type"], schema="wa_v3")
    op.create_index("ix_rk_notice_model", "rk_notice", ["model"], schema="wa_v3")
    op.create_index("ix_rk_notice_from_user", "rk_notice", ["from_user"], schema="wa_v3")

    op.create_table(
        "rk_shared_links",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("resource_type", sa.String(length=50), nullable=True),
        sa.Column("resource_id", sa.JSON(), nullable=True),
        sa.Column("share_token", sa.String(length=50), nullable=True),
        sa.Column("expire_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("department_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("to_be_confirmed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("share_token", name="uq_rk_shared_links_share_token"),
        schema="wa_v3",
    )
    op.create_index("ix_rk_shared_links_resource_type", "rk_shared_links", ["resource_type"], schema="wa_v3")
    op.create_index("ix_rk_shared_links_expire_at", "rk_shared_links", ["expire_at"], schema="wa_v3")


def downgrade() -> None:
    op.drop_index("ix_rk_shared_links_expire_at", table_name="rk_shared_links", schema="wa_v3")
    op.drop_index("ix_rk_shared_links_resource_type", table_name="rk_shared_links", schema="wa_v3")
    op.drop_table("rk_shared_links", schema="wa_v3")

    op.drop_index("ix_rk_notice_from_user", table_name="rk_notice", schema="wa_v3")
    op.drop_index("ix_rk_notice_model", table_name="rk_notice", schema="wa_v3")
    op.drop_index("ix_rk_notice_type", table_name="rk_notice", schema="wa_v3")
    op.drop_index("ix_rk_notice_active", table_name="rk_notice", schema="wa_v3")
    op.drop_index("ix_rk_notice_is_read", table_name="rk_notice", schema="wa_v3")
    op.drop_index("ix_rk_notice_receiver_id", table_name="rk_notice", schema="wa_v3")
    op.drop_table("rk_notice", schema="wa_v3")

    op.drop_index("ix_rk_llm_data_third_id", table_name="rk_llm_data", schema="wa_v3")
    op.drop_index("ix_rk_llm_data_parent_id", table_name="rk_llm_data", schema="wa_v3")
    op.drop_index("ix_rk_llm_data_event_type", table_name="rk_llm_data", schema="wa_v3")
    op.drop_index("ix_rk_llm_data_supply_id", table_name="rk_llm_data", schema="wa_v3")
    op.drop_index("ix_rk_llm_data_demand_id", table_name="rk_llm_data", schema="wa_v3")
    op.drop_table("rk_llm_data", schema="wa_v3")

    op.drop_index("ix_rk_match_res_type", table_name="rk_match_res", schema="wa_v3")
    op.drop_index("ix_rk_match_res_demand_version", table_name="rk_match_res", schema="wa_v3")
    op.drop_index("ix_rk_match_res_demand_role", table_name="rk_match_res", schema="wa_v3")
    op.drop_index("ix_rk_match_res_supply_id", table_name="rk_match_res", schema="wa_v3")
    op.drop_index("ix_rk_match_res_demand_id", table_name="rk_match_res", schema="wa_v3")
    op.drop_table("rk_match_res", schema="wa_v3")

    op.drop_index("ix_rk_case_status_active", table_name="rk_case_status", schema="wa_v3")
    op.drop_index("ix_rk_case_status_case_id", table_name="rk_case_status", schema="wa_v3")
    op.drop_table("rk_case_status", schema="wa_v3")

    op.drop_index("ix_rk_supply_demand_link_demand_version", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_index("ix_rk_supply_demand_link_demand_role", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_index("ix_rk_supply_demand_link_supply_demand_status3", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_index("ix_rk_supply_demand_link_active", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_index("ix_rk_supply_demand_link_demand_id", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_index("ix_rk_supply_demand_link_supply_id", table_name="rk_supply_demand_link", schema="wa_v3")
    op.drop_table("rk_supply_demand_link", schema="wa_v3")

    op.drop_index("ix_rk_demand_analysis_status", table_name="rk_demand", schema="wa_v3")
    op.drop_index("ix_rk_demand_active", table_name="rk_demand", schema="wa_v3")
    op.drop_index("ix_rk_demand_owner_id", table_name="rk_demand", schema="wa_v3")
    op.drop_index("ix_rk_demand_customer_id", table_name="rk_demand", schema="wa_v3")
    op.drop_index("ix_rk_demand_code", table_name="rk_demand", schema="wa_v3")
    op.drop_table("rk_demand", schema="wa_v3")

    op.drop_index("ix_rk_supply_ai_supply_id", table_name="rk_supply_ai", schema="wa_v3")
    op.drop_table("rk_supply_ai", schema="wa_v3")

    op.drop_index("ix_rk_supply_file_md5", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_analysis_status", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_active", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_owner_id", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_user_id", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_vendor_id", table_name="rk_supply", schema="wa_v3")
    op.drop_index("ix_rk_supply_name", table_name="rk_supply", schema="wa_v3")
    op.drop_table("rk_supply", schema="wa_v3")
