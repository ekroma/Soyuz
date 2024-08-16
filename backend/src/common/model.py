#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Annotated, Generic, TypeVar

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column
from sqlalchemy import DateTime, String, JSON
from uuid import uuid4

from src.utils.timezone import timezone

T = TypeVar('T')

id_key = Annotated[
    int, mapped_column(primary_key=True, index=True, autoincrement=True,unique=True, sort_order=-999, comment='Primary key ID')
]

def uuid4_str() -> str:
    return str(uuid4())

class UserMixin(MappedAsDataclass):
    create_user: Mapped[int] = mapped_column(sort_order=998, comment='Creator')
    update_user: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=998, comment='Updater')

class DateTimeMixin(MappedAsDataclass):
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),init=False, default_factory=timezone.now, sort_order=999, comment='Creation time',
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),init=False, onupdate=timezone.now, sort_order=999, comment='Update time'
    )

class TranslateMixin(MappedAsDataclass, Generic[T]):
    translates: Mapped[dict[str,T]] = mapped_column(JSON,comment='Translations')

class MappedBase(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(String(50),init=False, index=True,default_factory=uuid4_str, unique=True, nullable=False)

class DataClassBase(MappedAsDataclass, MappedBase):
    __abstract__ = True

class Base(DataClassBase, DateTimeMixin):
    __abstract__ = True
