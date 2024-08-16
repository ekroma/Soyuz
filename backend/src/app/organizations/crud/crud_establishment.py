#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.app.organizations.model import Establishment
from src.app.organizations.schema.establishment import (
    CreateEstablishmentSchema,
    UpdateEstablishmentSchema
)
from src.common.crud import BaseCRUDPlus
from src.utils.timezone import timezone
from src.common.enums import StatusType

class CRUDEstablishment(BaseCRUDPlus[Establishment]):

    async def get(self, db: AsyncSession, uuid: str) -> Establishment | None:
        return await self.select_model_by_uuid(db, uuid)

    async def get_by_email(self, db: AsyncSession, email: str) -> Establishment | None:
        return await self.select_model_by_column(db, 'email', email)

    async def create(self, db: AsyncSession, obj: CreateEstablishmentSchema) -> Establishment:
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, uuid: str, obj:UpdateEstablishmentSchema) -> int:
        return await self.update_model(db, uuid, obj)

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)
    
    async def get_list(
        self, 
        name: str | None = None, 
        status: StatusType | None = None, 
        created_after: datetime | None = None, 
        created_before: datetime | None = None):
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if name is not None:
            where_list.append(self.model.translates[('en')][('name')].astext == name)
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
            *,establishment_id: int | None = None, 
            establishment_uuid: str | None = None, 
            name: str | None = None) -> Establishment | None:
        where = []
        if establishment_id:
            where.append(self.model.id == establishment_id)
        if establishment_uuid:
            where.append(self.model.uuid == establishment_uuid)
        if name:
            where.append(self.model.translates[('en')][('name')].astext == name)
        establishment = await db.execute(
            select(self.model)
            .options(selectinload(self.model.users))
            .where(*where)
        )
        return establishment.scalars().first()

establishment_dao: CRUDEstablishment = CRUDEstablishment(Establishment)
