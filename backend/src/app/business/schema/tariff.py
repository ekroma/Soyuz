#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl, model_validator

from src.app.business.model.biz_tariff import TariffTranslateContent
from src.common.enums import StatusType, CardType
from src.common.schema import SchemaBase, TranslateSchema


class TariffSchemaBase(SchemaBase,TranslateSchema[TariffTranslateContent]):
    card_type: CardType
    status: StatusType
    price: float = Field(ge=0)

class CreateTariffSchema(TariffSchemaBase):
    pass

class UpdateTariffSchema(SchemaBase,TranslateSchema[TariffTranslateContent]):
    card_type: CardType|None = None
    status: StatusType|None = None
    price: float|None = Field(ge=0,default=None)

class ReadTariffSchema(TariffSchemaBase):
    uuid:str

    class Config:
        from_attributes = True 

class ListTariffSchema(TariffSchemaBase):
    uuid:str

    class Config:
        from_attributes = True


