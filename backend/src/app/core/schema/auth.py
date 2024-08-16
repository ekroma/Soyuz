#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import EmailStr, Field

from src.common.enums import StatusType
from src.common.schema import CustomPhoneNumber, SchemaBase
from .role import ReadRoleSchema
from src.app.business.schema.card import ReadCardSchema
from src.app.organizations.schema.establishment import ReadEstablishmentSchema

class UserInfoSchemaBase(SchemaBase):
    first_name:str|None
    last_name:str|None
    email: EmailStr = Field(..., examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None

class GetUserInfoDetail(UserInfoSchemaBase):
    uuid: str
    status: StatusType = Field(default=StatusType.enable)
    is_superuser: bool
    is_staff: bool
    is_multi_login: bool
    created_time: datetime|None = None
    last_login_time: datetime | None = None
    roles: list[ReadRoleSchema]
    card: ReadCardSchema|None
    establishment:ReadEstablishmentSchema|None = None

    class Config:
        from_attributes = True