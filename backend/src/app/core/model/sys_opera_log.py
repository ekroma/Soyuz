#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.mysql import JSON, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from src.common.model import Base


class OperaLog(Base):
    """Operation Log Table"""

    __tablename__ = 'sys_opera_log' # type: ignore

    email: Mapped[EmailStr | None] = mapped_column(String(20), comment='Username')
    method: Mapped[str] = mapped_column(String(20), comment='Request Type')
    title: Mapped[str] = mapped_column(String(255), comment='Operation Module')
    path: Mapped[str] = mapped_column(String(500), comment='Request Path')
    ip: Mapped[str] = mapped_column(String(50), comment='IP Address')
    country: Mapped[str | None] = mapped_column(String(50), comment='Country')
    region: Mapped[str | None] = mapped_column(String(50), comment='Region')
    city: Mapped[str | None] = mapped_column(String(50), comment='City')
    user_agent: Mapped[str] = mapped_column(String(255), comment='User Agent')
    os: Mapped[str | None] = mapped_column(String(50), comment='Operating System')
    browser: Mapped[str | None] = mapped_column(String(50), comment='Browser')
    device: Mapped[str | None] = mapped_column(String(50), comment='Device')
    args: Mapped[str | None] = mapped_column(JSON(), comment='Request Parameters')
    status: Mapped[int] = mapped_column(comment='Operation Status (0: Abnormal, 1: Normal)')
    code: Mapped[str] = mapped_column(String(20), insert_default='200', comment='Operation Status Code')
    msg: Mapped[str | None] = mapped_column(TEXT, comment='Message')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='Request Duration (ms)')
    opera_time: Mapped[datetime] = mapped_column(DateTime(timezone=True),comment='Operation Time')
