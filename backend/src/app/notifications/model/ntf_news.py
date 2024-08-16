#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.common.model import Base


class News(Base):
    """Role Table"""

    __tablename__ = 'ntf_news' # type: ignore

    title: Mapped[str] = mapped_column(Text, comment='News title') 
    url: Mapped[str] = mapped_column(String, comment='News source site') 
    link: Mapped[str] = mapped_column(String, comment='News link') 