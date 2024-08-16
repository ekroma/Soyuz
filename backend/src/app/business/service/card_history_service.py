#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from sqlalchemy import Select
from datetime import datetime

from src.app.business.crud.crud_card_history import card_history_dao
from src.common.enums import CardType, StatusType
from src.app.business.schema.card_history import CreateCardHistorySchema, UpdateCardHistorySchema
from src.app.business.model import CardHistory
from src.utils.timezone import timezone
from src.common.exception import errors
from database.db_psql import async_db_session

class CardHistoryService:

    @staticmethod
    async def update(*, uuid: str, obj: UpdateCardHistorySchema) -> int:
        async with async_db_session.begin() as db: 
            card_history = await card_history_dao.get(db,uuid)
            if not card_history:
                raise errors.NotFoundError(msg="Card history not found")
            return await card_history_dao.update_history_info(db,uuid=uuid,obj=obj)

    @staticmethod
    async def get_select(
            *, establishment_uuid: str|None = None, 
            card_uuid: str|None = None,
            created_before:datetime|None,
            created_after:datetime|None) -> Select:
        return await card_history_dao.get_list(
            establishment_uuid=establishment_uuid,
            card_uuid=card_uuid,
            created_before=created_before,
            created_after=created_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            return await card_history_dao.delete(db, uuid)


card_history_service = CardHistoryService()