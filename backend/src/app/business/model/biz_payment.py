#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Float,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.model import Base

class Payment(Base):
    __tablename__ = 'biz_payment'  # type: ignore

    tariff_uuid: Mapped[str] = mapped_column(  # type: ignore
        ForeignKey('biz_tariff.uuid', ondelete='CASCADE'))
    user_uuid: Mapped[str] = mapped_column(  # type: ignore
        ForeignKey('sys_user.uuid', ondelete='CASCADE'),unique=True)
        
    type: Mapped[str] = mapped_column(String, comment='Payment Type')
    status: Mapped[int] = mapped_column(default=2, comment='Payment Status (0 disabled, 1 active)')
    description: Mapped[str] = mapped_column(Text,default='No desctiption', comment='Usage discount percentage')

    tariff: Mapped['Tariff'] = relationship('Tariff',init=False, lazy='selectin')  # type: ignore # noqa: F821
