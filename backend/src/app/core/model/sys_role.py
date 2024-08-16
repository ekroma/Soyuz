#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr

from src.common.model import Base, TranslateMixin
from .sys_role_permission import sys_role_permission
from .sys_user_role import sys_user_role


class RoleTranslateContent(BaseModel):
    name: str|None
    description: str|None

class Role(Base, TranslateMixin[RoleTranslateContent]):
    """Role Table"""

    __tablename__ = 'sys_role' # type: ignore

    status: Mapped[int] = mapped_column(default=True, comment='User Account Status (0 disabled, 1 active)')
    users: Mapped[list['User']] = relationship(  # noqa: F821 # type: ignore
        init=False, secondary=sys_user_role, back_populates='roles',lazy='noload')
    permissions: Mapped[list['Permission']] = relationship('Permission',  # noqa: F821 # type: ignore
        init=False, secondary=sys_role_permission, lazy='selectin')