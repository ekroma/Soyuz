#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, desc, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.app.organizations.model import Counseling
from src.app.organizations.schema.counseling import (
    CreateCounselingSchema,
    UpdateCounselingSchema
)
from src.common.crud import BaseCRUDPlus
from src.utils.timezone import timezone
from src.common.enums import StatusType

class CRUDCounseling(BaseCRUDPlus[Counseling]):

    async def get(self, db: AsyncSession, uuid: str) -> Counseling | None:
        return await self.select_model_by_uuid(db, uuid)

    async def create(self, db: AsyncSession, obj: CreateCounselingSchema) -> Counseling:
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, uuid: str, obj:UpdateCounselingSchema|dict) -> int:
        return await self.update_model(db, uuid, obj)

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)
    
    async def get_list(
        self, 
        name: str | None = None, 
        email: str | None = None, 
        status: StatusType | None = None, 
        created_after: datetime | None = None, 
        created_before: datetime | None = None):
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if name is not None:
            where_list.append(self.model.name == name)
        if email is not None:
            where_list.append(self.model.client_email == email)
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
            *,counseling_id: int | None = None, 
            counseling_uuid: str | None = None) -> Counseling | None:
        where = []
        if counseling_id:
            where.append(self.model.id == counseling_id)
        if counseling_uuid:
            where.append(self.model.uuid == counseling_uuid)
        counseling = await db.execute(
            select(self.model)
            .where(*where)
        )
        return counseling.scalars().first()
    
    async def delete_many_by_status(self, db: AsyncSession, status: StatusType = StatusType.pending) -> int:
        result = await db.execute(
            delete(self.model).where(self.model.status == status)
        )
        return result.rowcount

counseling_dao: CRUDCounseling = CRUDCounseling(Counseling)
