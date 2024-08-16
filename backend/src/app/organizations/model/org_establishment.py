#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel
from sqlalchemy import String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.model import Base, TranslateMixin

class EstablishmentTranslateContent(BaseModel):
    name: str|None
    description: str|None

class Establishment(Base, TranslateMixin[EstablishmentTranslateContent]):
    __tablename__ = 'org_establishment' # type: ignore

    users: Mapped[list['User']] = relationship('User',init=False, back_populates='establishment',lazy='noload')  # type: ignore # noqa: F821

    address: Mapped[str] = mapped_column(Text, comment='Establishment address')
    coordinates: Mapped[str] = mapped_column(Text, comment='Establishment coordinates')
    phone: Mapped[str] = mapped_column(String(20), comment='Establishment phone')
    email: Mapped[str] = mapped_column(String(100), comment='Establishment email')
    images: Mapped[list[str]] = mapped_column(JSON,init=False, nullable=True, comment='List of image URLs')
    discount: Mapped[float] = mapped_column(Float, default=0, comment='Establishment Discount')
    status: Mapped[int] = mapped_column(default=1, comment='Establishment Status (0 disabled, 1 active)')
    website: Mapped[str] = mapped_column(String(100), nullable=True, default=None, comment='Establishment website')