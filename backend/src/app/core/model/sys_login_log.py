#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from src.common.model import DataClassBase, id_key
from src.utils.timezone import timezone


class LoginLog(DataClassBase):
    """LoginLog Table"""

    __tablename__ = 'sys_login_log' # type: ignore

    user_uuid: Mapped[str] = mapped_column(String(50), comment='User UUID')
    email: Mapped[str] = mapped_column(String, comment='Email')
    status: Mapped[int] = mapped_column(insert_default=0, comment='Login Status (0 failure, 1 success)')
    ip: Mapped[str] = mapped_column(String(50), comment='Login IP Address')
    country: Mapped[str | None] = mapped_column(String(50), comment='Country')
    region: Mapped[str | None] = mapped_column(String(50), comment='Region')
    city: Mapped[str | None] = mapped_column(String(50), comment='City')
    user_agent: Mapped[str] = mapped_column(String(255), comment='User Agent')
    os: Mapped[str | None] = mapped_column(String(50), comment='Operating System')
    browser: Mapped[str | None] = mapped_column(String(50), comment='Browser')
    device: Mapped[str | None] = mapped_column(String(50), comment='Device')
    msg: Mapped[str] = mapped_column(TEXT, comment='Message')
    login_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='Login Time')
    created_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), init=False, default_factory=timezone.now, comment='Created Time')
