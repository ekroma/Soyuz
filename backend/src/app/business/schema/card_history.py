#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from fastapi import UploadFile
from pydantic import Field, EmailStr

from src.app.business.model.biz_card_history import CardHistoryTranslateContent
from src.common.schema import SchemaBase, TranslateSchema

class CardHistorySchemaBase(SchemaBase, TranslateSchema[CardHistoryTranslateContent]):
    establishment_name:str|None
    client_email:str|None
    card_uuid:str|None
    discount:float|None
    establishment_uuid:str|None

class CreateCardHistorySchema(CardHistorySchemaBase):
    pass

class UpdateCardHistorySchema(CardHistorySchemaBase):
    pass

class ReadCardHistorySchema(CardHistorySchemaBase):
    pass

    class Config:
        from_attributes = True