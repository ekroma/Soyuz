#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import and_, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from datetime import timedelta, datetime

from src.utils import get_random_string
from src.app.business.model import Card
from src.app.business.schema.card import (
    CreateCardSchema
)
from src.common.enums import CardType, StatusType
from src.utils.timezone import timezone
from src.common.crud import BaseCRUDPlus

class CRUDCard(BaseCRUDPlus[Card]):

    async def get(self, db: AsyncSession, uuid: str) -> Card| None:
        return await self.select_model_by_uuid(db, uuid)

    async def get_by_code(self, db: AsyncSession, code: str) -> Card| None:
        return await self.select_model_by_column(db, 'code', code)

    async def update_expire_date(self, db: AsyncSession, uuid: str, expire_date:datetime) -> int:
        card = await db.execute(
            update(self.model).where(self.model.uuid == uuid).values(expire_date=timezone.f_datetime(expire_date)))
        return card.rowcount

    async def create(self, db: AsyncSession, obj: CreateCardSchema, tariff_id:int, user_id:int) -> Card:
        dict_obj = obj.model_dump(exclude='tariff_uuid') # type: ignore
        dict_obj.update({
            'expire_date':timezone.now() + timedelta(days=30*obj.expire_date),
            'tariff_id':tariff_id,
            'user_id':user_id})
        new_card = self.model(**dict_obj)
        db.add(new_card)
        await db.flush()
        await db.refresh(new_card)
        return new_card
    
    async def update_tariff(self, db: AsyncSession, uuid:str, tariff_uuid:str) -> int:
        return await self.update_model(db, uuid, {'tariff_uuid':tariff_uuid})

    async def update_status(self, db: AsyncSession, uuid:str, status) -> int:
        return await self.update_model(db, uuid, {'status':status})
    
    async def update_type(self, db: AsyncSession, uuid:str, type:CardType) -> int:
        return await self.update_model(db, uuid, {'type':type})

    async def update_code(self, db: AsyncSession, uuid:str) -> int:
        return await self.update_model(db, uuid, {'code':get_random_string(6)})

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)
    
    async def get_list(
        self,  
        type: CardType|None = None, 
        status: StatusType|None = None, 
        created_after: datetime|None = None, 
        created_before: datetime|None = None, 
        expire_after: datetime|None = None, 
        expire_before: datetime|None = None,
    ) -> Select:
        se = (
            select(self.model)
            .options(selectinload(self.model.user))
            .order_by(desc(self.model.created_time)) # type: ignore
        )
        where_list = []
        if type is not None:
            where_list.append(self.model.type == type)
        if status is not None:
            where_list.append(self.model.status == status)
        if created_after is not None:
            where_list.append(self.model.created_time >= timezone.f_datetime(created_after))
        if created_before is not None:
            where_list.append(self.model.created_time <= timezone.f_datetime(created_before))
        if expire_after is not None:
            where_list.append(self.model.expire_date >= timezone.f_datetime(expire_after))
        if expire_before is not None:
            where_list.append(self.model.expire_date <= timezone.f_datetime(expire_before))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def get_with_relation(
            self, 
            db: AsyncSession, 
            *, 
            card_id: int | None = None, 
            card_uuid: str | None = None) -> Card | None:
        where = []
        if card_id:
            where.append(self.model.id == card_id)
        if card_uuid:
            where.append(self.model.uuid == card_uuid)
        card = await db.execute(
            select(self.model)
            .options(
                selectinload(self.model.tariff),
                selectinload(self.model.user))
            .where(*where)
        )
        return card.scalars().first()

card_dao: CRUDCard = CRUDCard(Card)
