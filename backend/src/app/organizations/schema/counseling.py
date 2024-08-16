#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import EmailStr

from src.common.schema import SchemaBase, CustomPhoneNumber


class CounselingSchemaBase(SchemaBase):
    name:str|None = None
    description:str|None = None
    client_email:EmailStr|None = None
    phone: CustomPhoneNumber | None = None


class CreateCounselingSchema(CounselingSchemaBase):
    pass


class UpdateCounselingSchema(CounselingSchemaBase):
    pass

class ReadCounselingSchema(CounselingSchemaBase):
    created_time:datetime

    class Config:
        from_attributes = True