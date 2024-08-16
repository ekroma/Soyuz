#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import and_, desc, select, update, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta, datetime

from src.app.business.model import Payment
from src.app.business.schema.payment import CreatePaymentSchema
from src.common.enums import StatusType, PaymentType
from src.utils.timezone import timezone
from src.common.crud import BaseCRUDPlus

class CRUDPayment(BaseCRUDPlus[Payment]):

    async def get(self, db: AsyncSession, uuid: str) -> Payment | None:
        return await self.select_model_by_uuid(db, uuid)

    async def create(self, db: AsyncSession, obj: CreatePaymentSchema, user_uuid: str) -> Payment:
        dict_obj = obj.model_dump()  # type: ignore
        dict_obj.update({
            'user_uuid': user_uuid
        })
        new_payment = self.model(**dict_obj)
        db.add(new_payment)
        await db.flush()
        await db.refresh(new_payment)
        return new_payment

    async def update_status(self, db: AsyncSession, uuid: str, status: StatusType) -> int:
        return await self.update_model(db, uuid, {'status': status})

    async def update_description(self, db: AsyncSession, uuid: str, description: str) -> int:
        return await self.update_model(db, uuid, {'description': description})

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)
    
    async def get_list(
        self,  
        payment_type: PaymentType|None = None, 
        status: int|None = None, 
        created_after: datetime|None = None, 
        created_before: datetime|None = None, 
    ) -> Select:
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if payment_type is not None:
            where_list.append(self.model.type == payment_type)
        if status is not None:
            where_list.append(self.model.status == status)
        if created_after is not None:
            where_list.append(self.model.created_time >= timezone.f_datetime(created_after))
        if created_before is not None:
            where_list.append(self.model.created_time <= timezone.f_datetime(created_before))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def get_with_relation(
            self, 
            db: AsyncSession, 
            *, 
            payment_id: int | None = None, 
            payment_uuid: str | None = None) -> Payment | None:
        where = []
        if payment_id:
            where.append(self.model.id == payment_id)
        if payment_uuid:
            where.append(self.model.uuid == payment_uuid)
        payment = await db.execute(
            select(self.model)
            .where(*where)
            .order_by(desc(self.model.created_time))
        )
        return payment.scalars().first()

payment_dao: CRUDPayment = CRUDPayment(Payment)
