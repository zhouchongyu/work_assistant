from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.mixins import BusinessMixin, TimestampMixin


class RkSupply(Base, TimestampMixin, BusinessMixin):
    __tablename__ = "rk_supply"

    id: Mapped[int] = mapped_column(
        sa.BigInteger().with_variant(sa.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, unique=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False, index=True)

    path: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    file_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    file_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    file_md5: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    file_update: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    vendor_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    vendor_contact_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)
    user_id: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True, index=True)

    supply_user_name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    supply_user_age: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_user_gender: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_user_citizenship: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    supply_birthday: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    name_pinyin: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    last_name: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    first_name: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)

    remark: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    status_detail: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    score: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    skill_scores: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    resume_res: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    case_status: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    audition_date: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    audition_idea: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    result_expected_date: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    audition_time: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    nearest_station: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    work_location: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    specialty: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    years_of_work: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    start_work_date: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    available_date: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    skillx: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    skilly: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    skillz: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    father_skill: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    japanese_level: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    english_level: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    japanese_level_ai: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    english_level_ai: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)

    role: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    role_level: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    role_level_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    analysis_version: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    analysis_status: Mapped[str | None] = mapped_column(sa.String(100), nullable=True, index=True)
    contact_analysis_status: Mapped[str | None] = mapped_column(sa.String(100), nullable=True, index=True)

    duplicate_status: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    duplicate_content: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    error_status: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    content_confirm: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    version: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    acdtc: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    contracted_member: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)

    price: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    price_update: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    price_original: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    price_update_task_date: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    task_status: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
