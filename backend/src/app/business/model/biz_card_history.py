#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String, ForeignKey, Float 
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr

from src.common.model import Base, TranslateMixin

class CardHistoryTranslateContent(BaseModel):
    title: str|None
    description: str|None

class CardHistory(Base, TranslateMixin[CardHistoryTranslateContent]):
    __tablename__ = 'biz_card_history' # type: ignore

    card_uuid: Mapped[str] = mapped_column(
        ForeignKey('biz_card.uuid', ondelete='SET NULL'), nullable=False)
    establishment_uuid: Mapped[str] = mapped_column(  # type: ignore
        ForeignKey('org_establishment.uuid', ondelete='CASCADE'),unique=True)
    client_email: Mapped[EmailStr] = mapped_column(String(50), comment='User Email') 
    discount:Mapped[float] = mapped_column(Float,default=0, comment='Usage discount percentage')
    establishment_name: Mapped[str|None] = mapped_column(String(50),default="Not establishment", comment='Establishment UUID')