#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import EmailStr, Field, HttpUrl

from src.common.enums import StatusType
from src.common.schema import CustomPhoneNumber, SchemaBase
from .role import ReadRoleSchema
from src.app.business.schema.card import ReadCardSchema
from src.app.organizations.schema.establishment import ReadEstablishmentSchema

class AuthSchemaBase(SchemaBase):
    email: str
    password: str

class AuthLoginParam(AuthSchemaBase):
    pass

class RegisterUserParam(AuthSchemaBase):
    first_name:str
    last_name:str
    email: EmailStr = Field(..., examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None

class AddUserParam(AuthSchemaBase):
    roles: list[str]
    first_name:str
    last_name:str
    email: EmailStr = Field(..., examples=['user@example.com'])
    establishment_uuid:str|None

class UserInfoSchemaBase(SchemaBase):
    first_name:str|None
    last_name:str|None
    email: EmailStr = Field(..., examples=['user@example.com'])
    phone: CustomPhoneNumber | None = None

class UpdateUserParam(UserInfoSchemaBase):
    pass

class UpdateUserRoleParam(SchemaBase):
    roles: list[str]

class AvatarParam(SchemaBase):
    url: HttpUrl = Field(...,)

class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    uuid: str
    status: StatusType = Field(default=StatusType.enable)
    is_superuser: bool
    is_staff: bool
    is_multi_login: bool
    created_time: datetime|None = None
    last_login_time: datetime | None = None

    class Config:
        from_attributes = True

class GetUserInfoListDetails(GetUserInfoNoRelationDetail):

    class Config:
        from_attributes = True

class GetUserInfoDetail(GetUserInfoListDetails):
    roles: list[ReadRoleSchema]
    establishment:ReadEstablishmentSchema|None = None

    class Config:
        from_attributes = True

class ResetPasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str

class RestorePasswordParam(SchemaBase):
    email:str
    code: str
    new_password: str
    confirm_password: str