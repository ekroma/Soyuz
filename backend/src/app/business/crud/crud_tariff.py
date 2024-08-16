#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, desc, and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.app.business.model import Tariff
from src.app.business.schema.tariff import (
    CreateTariffSchema,
    UpdateTariffSchema
)
from src.common.enums import CardType, StatusType
from src.common.crud import BaseCRUDPlus
from src.utils.timezone import timezone

class CRUDTariff(BaseCRUDPlus[Tariff]):
    async def get(self, db: AsyncSession, uuid: str) -> Tariff| None:
        return await self.select_model_by_uuid(db, uuid)

    async def create(self, db: AsyncSession, obj: CreateTariffSchema) -> Tariff:
        return await self.create_model(db, obj)

    async def update_tariff_info(self, db: AsyncSession, uuid: str, obj: UpdateTariffSchema|dict) -> int:
        return await self.update_model(db, uuid, obj)

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)

    async def get_list(
        self, 
        name: str | None = None, 
        card_type: CardType | None = None, 
        status: StatusType | None = None, 
        min_price: float | None = None, 
        max_price: float | None = None,
        created_after: datetime|None = None, 
        created_before: datetime|None = None, 
    ) -> Select:
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if name:
            where_list.append(self.model.translates[('en')][('name')].astext == name)
        if card_type is not None:
            where_list.append(self.model.card_type == card_type)
        if status is not None:
            where_list.append(self.model.status == status)
        if min_price is not None:
            where_list.append(self.model.price >= min_price)
        if max_price is not None:
            where_list.append(self.model.price <= max_price)
        if created_after is not None:
            where_list.append(self.model.created_time >= timezone.f_datetime(created_after))
        if created_before is not None:
            where_list.append(self.model.created_time <= timezone.f_datetime(created_before))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def update_status(self, db: AsyncSession, uuid: str, status: StatusType) -> int:
        return await self.update_model(db, uuid, {'status': status})
    
    async def get_with_relation(
            self, 
            db: AsyncSession, 
            *, tariff_id: int | None = None,
            tariff_uuid: str | None = None, 
            name: str | None = None) -> Tariff | None:
        where = []
        if tariff_id:
            where.append(self.model.id == tariff_id)
        if tariff_id:
            where.append(self.model.uuid == tariff_uuid)
        tariff = await db.execute(
            select(self.model)
            .options(selectinload(self.model.cards))
            .where(*where)
        )
        return tariff.scalars().first()

tariff_dao: CRUDTariff = CRUDTariff(Tariff)
