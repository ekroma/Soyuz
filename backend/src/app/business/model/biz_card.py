#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.model import Base

class Card(Base):
    __tablename__ = 'biz_card'  # type: ignore

    type: Mapped[str] = mapped_column(String, comment='Card Type')
    expire_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='Card Expire Date')
    
    tariff_id: Mapped[int] = mapped_column(  # type: ignore
        ForeignKey('biz_tariff.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(  # type: ignore
        ForeignKey('sys_user.id', ondelete='CASCADE'),unique=True)
    
    tariff: Mapped['Tariff'] = relationship('Tariff',init=False, back_populates='cards', lazy='selectin')  # type: ignore # noqa: F821
    user: Mapped['User'] = relationship('User',init=False, back_populates='card',foreign_keys=[user_id],single_parent=True, lazy='joined')  # type: ignore # noqa: F821
    card_history: Mapped[list['CardHistory']] = relationship('CardHistory',init=False,uselist=True, lazy='noload')  # type: ignore
    
    code: Mapped[str|None] = mapped_column(String(6),init=False,default=None, nullable=True, comment='Code') # type: ignore
    status: Mapped[int] = mapped_column(default=1, comment='User Card Status (0 disabled, 1 active)')

    __table_args__ = (UniqueConstraint("user_id"),)