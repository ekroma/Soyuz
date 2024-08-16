#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr

from src.common.model import Base
from src.utils.timezone import timezone
from .sys_user_role import sys_user_role
from src.app.organizations.model import Establishment

class User(Base):
    """User Table"""

    __tablename__ = 'sys_user' # type: ignore

    email: Mapped[EmailStr] = mapped_column(String(50), unique=True, index=True, comment='Email') 
    first_name: Mapped[str|None] = mapped_column(String(20),default=None, comment='First name') 
    last_name: Mapped[str|None] = mapped_column(String(20),default=None, comment='Last name') 
    password: Mapped[str] = mapped_column(String(255),default='processing', comment='Password')
    salt: Mapped[str] = mapped_column(String(10),default='processing', comment='Salt')
    code: Mapped[str|None] = mapped_column(String(6),default=None, comment='Code')
    is_superuser: Mapped[bool] = mapped_column(default=0, comment='Superuser (0 no, 1 yes)')
    is_staff: Mapped[bool] = mapped_column(default=0, comment='Admin Login (0 no, 1 yes)')
    status: Mapped[int] = mapped_column(default=1, comment='User Account Status (0 disabled, 1 active)')
    is_multi_login: Mapped[bool] = mapped_column(default=False, comment='Allow Multiple Logins (0 no, 1 yes)')
    phone: Mapped[str | None] = mapped_column(String, default=None, comment='Phone Number')
    last_login_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), init=False, onupdate=timezone.now, comment='Last Login Time')

    establishment_uuid: Mapped[str|None] = mapped_column(  # type: ignore
        ForeignKey('org_establishment.uuid', ondelete='SET NULL'), default=None, nullable=True)
    
    establishment: Mapped[Optional[Establishment]] = relationship('Establishment', # type: ignore
        default=None,uselist=False, lazy='selectin', back_populates='users',)  
    card: Mapped[Optional['Card']] = relationship('Card', # type: ignore
        back_populates='user', default=None,uselist=False, lazy='selectin')  
    roles: Mapped[list['Role']] = relationship('Role',  # type: ignore
        init=False, secondary=sys_user_role, back_populates='users',uselist=True, lazy='selectin')