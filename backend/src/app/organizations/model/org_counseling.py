#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.model import Base

class Counseling(Base):
    __tablename__ = 'org_counseling' # type: ignore

    name: Mapped[str] = mapped_column(Text, comment='Client name')
    client_email: Mapped[str] = mapped_column(String(100), comment='Client email')
    description: Mapped[str] = mapped_column(Text, comment='Client description')
    phone: Mapped[str] = mapped_column(String(20), comment='Establishment phone')
    status: Mapped[int] = mapped_column(default=1, comment='Establishment Status (0 disabled, 1 active)')