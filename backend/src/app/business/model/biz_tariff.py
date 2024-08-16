#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.model import Base, TranslateMixin

class TariffTranslateContent(BaseModel):
    name: str|None
    description: list[str]

class Tariff(Base, TranslateMixin[TariffTranslateContent]):
    __tablename__ = 'biz_tariff' # type: ignore

    card_type: Mapped[str] = mapped_column(String, comment='Card Type') # type: ignore
    price: Mapped[float] = mapped_column(Float, default=0, comment='Tariff Price')
    status: Mapped[int] = mapped_column(default=1, comment='Tariff Status (0 disabled, 1 active)')
    cards: Mapped[list['Card']] = relationship('Card',init=False, back_populates='tariff', lazy=None) # type: ignore