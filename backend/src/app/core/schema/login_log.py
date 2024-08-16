#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from pydantic import EmailStr

from src.common.enums import StatusType
from src.common.schema import SchemaBase


class LoginLogSchemaBase(SchemaBase):
    user_uuid: str
    email: EmailStr
    status: StatusType
    ip: str
    country: str | None
    region: str | None
    city: str | None
    user_agent: str
    browser: str | None
    os: str | None
    device: str | None
    msg: str
    login_time: datetime


class CreateLoginLogParam(LoginLogSchemaBase):
    pass


class UpdateLoginLogParam(LoginLogSchemaBase):
    pass


class GetLoginLogListDetails(LoginLogSchemaBase):
    id: int
    created_time: datetime

    class Config:
        from_attributes = True