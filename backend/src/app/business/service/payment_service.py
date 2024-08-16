#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from sqlalchemy import Select
from datetime import datetime

from src.app.business.model import Payment
from src.app.business.crud.crud_payment import payment_dao
from src.app.business.crud.crud_card import card_dao
from src.app.business.crud.crud_tariff import tariff_dao 
from src.common.enums import PaymentType, StatusType
from src.app.business.schema.payment import (
    CreatePaymentSchema,
    UpdatePaymentSchema    
)
from src.common.exception import errors
from database.db_psql import async_db_session

class PaymentService:

    @staticmethod
    async def create(request: Request, *, obj: CreatePaymentSchema) -> Payment:
        async with async_db_session.begin() as db:
            try:
                if not await tariff_dao.get(db,uuid=obj.tariff_uuid):
                    raise errors.NotFoundError
                payment = await payment_dao.create(db,obj=obj, user_uuid=request.user.uuid) 
            except errors.NotFoundError as e:
                raise errors.HTTPError(code=404, msg=e.msg)
            else:
                await db.refresh(payment)
                return payment

    @staticmethod
    async def update(*, uuid: str, obj: UpdatePaymentSchema) -> int:
        async with async_db_session.begin() as db:
            payment = await payment_dao.get(db, uuid)
            count = 0
            if not payment:
                raise errors.NotFoundError(msg="Payment not found")
            if obj.status:
                count += await payment_dao.update_status(db, uuid, obj.status)
            if obj.description:
                count += await payment_dao.update_description(db, uuid, obj.description)
            return count

    @staticmethod
    async def get_payment_info(*, payment_id: int | None = None, payment_uuid: str | None = None) -> Payment:
        async with async_db_session() as db:
            payment = await payment_dao.get_with_relation(
                db, payment_id=payment_id, payment_uuid=payment_uuid)
            if not payment:
                raise errors.NotFoundError(msg='Payment does not exist')
            return payment

    @staticmethod
    async def get_select(
            *, payment_type: PaymentType | None = None, 
            status: StatusType | None = None,
            created_before: datetime | None = None,
            created_after: datetime | None = None) -> Select:
        return await payment_dao.get_list(
            payment_type=payment_type,
            status=status,
            created_before=created_before,
            created_after=created_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            payment = await payment_dao.get(db, uuid)
            if not payment:
                raise errors.NotFoundError(msg='Payment does not exist')
            return await payment_dao.delete(db, payment.uuid)


payment_service = PaymentService()
