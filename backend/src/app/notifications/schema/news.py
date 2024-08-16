#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from src.common.schema import SchemaBase


class NewsSchemaBase(SchemaBase):
    title: str = 'No title'
    url: str = 'No source site'
    link: str = 'No link'

class CreateNewsSchema(NewsSchemaBase):
    pass

class UpdateNewsSchema(NewsSchemaBase):
    pass

class ReadNewsSchema(NewsSchemaBase):
    uuid: str
    created_time:datetime

    class Config:
        from_attributes = True