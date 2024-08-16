#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import Field

from src.common.enums import StatusType, PaymentType
from src.common.schema import SchemaBase

class PaymentSchemaBase(SchemaBase):
    type: PaymentType = Field()
    price: float = Field(ge=0)
    description: str|None = None
    tariff_uuid:str

class CreatePaymentSchema(PaymentSchemaBase):
    status: StatusType = Field(default=StatusType.pending)

class UpdatePaymentSchema(PaymentSchemaBase):
    type:PaymentType|None = None
    status: StatusType|None = None
    price: float|None = Field(default=None,ge=0)

class ReadPaymentSchema(PaymentSchemaBase):
    uuid: str
    status: StatusType

    class Config:
        from_attributes = True