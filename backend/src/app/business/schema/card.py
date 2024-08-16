#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from fastapi import UploadFile
from pydantic import Field, EmailStr

from src.common.enums import StatusType, CardType
from src.common.schema import SchemaBase
from .tariff import ReadTariffSchema

class CardSchemaBase(SchemaBase):
    type: CardType = Field()

class UserShortInfo(SchemaBase):
    first_name:str
    last_name:str
    email:EmailStr
    uuid:str

class CreateCardSchema(CardSchemaBase):
    status: StatusType = Field(default=StatusType.enable)
    expire_date: int = Field(default=1)
    tariff_uuid: str = Field()


class UpdateCardSchema(CardSchemaBase):
    type:CardType|None = None
    status: StatusType|None = None
    expire_date: datetime|None
    tariff_uuid: str|None

class ReadCardSchema(CardSchemaBase):
    uuid: str
    expire_date: datetime
    tariff: ReadTariffSchema
    status: StatusType

    class Config:
        from_attributes = True

class ReadCardWithUserSchema(ReadCardSchema):
    user:UserShortInfo

    class Config:
        from_attributes = True

class ReadDetailCardSchema(CardSchemaBase):
    uuid: str
    expire_date: datetime
    tariff: ReadTariffSchema
    status: StatusType