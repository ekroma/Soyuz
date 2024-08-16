#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import and_, desc, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.app.business.model import CardHistory
from src.app.business.schema.card_history import (
    CreateCardHistorySchema,
    UpdateCardHistorySchema
)
from src.common.enums import StatusType
from src.utils.timezone import timezone
from src.common.crud import BaseCRUDPlus


class CRUDCardHistory(BaseCRUDPlus[CardHistory]):

    async def get(self, db: AsyncSession, uuid: str) -> CardHistory| None:
        return await self.select_model_by_uuid(db, uuid)

    async def create(self, db: AsyncSession,obj:CreateCardHistorySchema) -> CardHistory|None:
        return await self.create_model(db,obj=obj)

    async def update_history_info(self, db: AsyncSession, uuid: str, obj: UpdateCardHistorySchema|dict) -> int:
        return await self.update_model(db, uuid, obj)

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)
    
    async def get_list(
        self,
        establishment_uuid:str|None,
        card_uuid:str|None,
        created_after: datetime|None = None, 
        created_before: datetime|None = None,
    ):
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if card_uuid:
            where_list.append(self.model.card_uuid == card_uuid)
        if establishment_uuid:
            where_list.append(self.model.establishment_uuid == establishment_uuid)
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
            card_uuid: str | None = None,
            establishment_uuid: str | None = None,
            card_history_id: int | None = None, 
            card_history_uuid: str | None = None) -> CardHistory | None:
        where = []
        if card_uuid:
            where.append(self.model.card_uuid == card_uuid)
        if establishment_uuid:
            where.append(self.model.establishment_uuid == establishment_uuid)
        if card_history_id:
            where.append(self.model.id == card_history_id)
        if card_history_uuid:
            where.append(self.model.uuid == card_history_uuid)
        card_history = await db.execute(
            select(self.model)
            .where(*where)
        )
        return card_history.scalars().first()

card_history_dao: CRUDCardHistory = CRUDCardHistory(CardHistory)
