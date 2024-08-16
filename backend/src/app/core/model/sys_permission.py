#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel

from src.common.model import Base, TranslateMixin
from src.common.enums import PermissionScopes

class PermissionTranslateContent(BaseModel):
    name: str|None
    description: str|None

class Permission(Base, TranslateMixin[PermissionTranslateContent]):
    """Permission Table"""

    __tablename__ = 'sys_permission' # type: ignore

    status: Mapped[int] = mapped_column(default=1, comment='Permission Status (0 disabled, 1 active)')
    perm: Mapped[str] = mapped_column(String(4),comment='Permissions', default='r')  
    scope: Mapped[str] = mapped_column(default=PermissionScopes.user,comment='Permission Scope') # type: ignore