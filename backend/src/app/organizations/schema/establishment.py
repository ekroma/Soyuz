#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl, model_validator

from src.app.organizations.model.org_establishment import EstablishmentTranslateContent
from src.common.enums import StatusType
from src.common.schema import SchemaBase, TranslateSchema


class EstablishmentSchemaBase(SchemaBase, TranslateSchema[EstablishmentTranslateContent]):
    address:str|None = None
    coordinates:str|None = None
    phone:str|None = None
    website:str|None = None
    email:EmailStr|None = None
    status:StatusType|None = None
    discount:float = Field(ge=0)


class CreateEstablishmentSchema(EstablishmentSchemaBase):
    pass


class UpdateEstablishmentSchema(EstablishmentSchemaBase):
    pass


class ReadEstablishmentSchema(EstablishmentSchemaBase):
    uuid: str
    created_time:datetime

    class Config:
        from_attributes = True

class ListEstablishmentSchema(EstablishmentSchemaBase):
    uuid: str

    class Config:
        from_attributes = True