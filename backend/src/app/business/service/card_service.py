#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from sqlalchemy import Select
from datetime import datetime

from src.app.business.crud.crud_card import card_dao
from src.app.business.crud.crud_card_history import card_history_dao
from src.app.business.crud.crud_tariff import tariff_dao
from src.app.business.model.biz_card import Card
from src.common.enums import CardType, StatusType
from src.common.filebase import FileBase
from src.app.business.schema.card import (
    CreateCardSchema,
    UpdateCardSchema    
)
from src.app.business.schema.card_history import CreateCardHistorySchema
from src.utils.timezone import timezone
from src.common.exception import errors
from database.db_psql import async_db_session

class CardService:
    @staticmethod
    async def create(request:Request,*, obj: CreateCardSchema) -> Card:
        async with async_db_session.begin() as db:
            try:
                tariff = await tariff_dao.get(db, uuid=obj.tariff_uuid)
                if not tariff or tariff.status == StatusType.disable:
                    raise errors.NotFoundError(msg='Tariff not found')
                card = await card_dao.create(db, obj, tariff.id, request.user.id)
                await card_dao.update_code(db,card.uuid) # type: ignore
            except errors.NotFoundError as e:
                raise errors.HTTPError(code=404,msg=e.msg)
            else:
                await db.refresh(card)
                return card

    @staticmethod
    async def update(*, uuid: str, obj: UpdateCardSchema) -> int:
        async with async_db_session.begin() as db: 
            card = await card_dao.get(db,uuid)
            count = 0
            if not card:
                raise errors.NotFoundError(msg="Card not found")
            if obj.status:
                count += await card_dao.update_status(db,uuid,obj.status)
            if obj.type:
                count += await card_dao.update_type(db,uuid,obj.type)
            if obj.tariff_uuid:
                if not await tariff_dao.get(db,obj.tariff_uuid):
                    raise errors.NotFoundError(msg="Tariff not found")
                count += await card_dao.update_tariff(db,uuid,obj.tariff_uuid)
            return count

    @staticmethod
    async def get_card_info(*,card_id:int|None=None,card_uuid:str|None=None) -> Card:
        async with async_db_session() as db:
            card = await card_dao.get_with_relation(
                db,card_id=card_id,card_uuid=card_uuid)
            if not card:
                raise errors.NotFoundError(msg='Card does not exist')
            return card

    @staticmethod
    async def get_card_info_by_code_to_use(*,uuid:str,code:str) -> Card:
        async with async_db_session.begin() as db:
            card = await card_dao.get_with_relation(
                db,card_uuid=uuid)
            if not card:
                raise errors.NotFoundError(msg='Card does not exist')
            if not card.code != code:
                raise errors.NotFoundError(msg='Code doesn`t match')
            if not card.status:
                raise errors.ForbiddenError(msg='Card has expired')
            return card

    @staticmethod
    async def accept_card_use(*,request:Request,uuid:str,code:str) -> int:
        async with async_db_session.begin() as db:
            try:
                if not request.user.is_staff:
                    raise errors.ForbiddenError()
                card = await card_dao.get_with_relation(
                    db,card_uuid=uuid)
                if not card:
                    raise errors.NotFoundError(msg='Card does not exist')
                if card.code != code:
                    raise errors.NotFoundError(msg='Code doesn`t match')
                if timezone.f_datetime(card.expire_date) < timezone.now():
                    await card_dao.update_status(db,card.uuid,StatusType.disable)
                    raise errors.ForbiddenError(msg='Card has expired')
                if not card.status:
                    raise errors.ForbiddenError(msg='Card has expired')
                history_data = CreateCardHistorySchema(
                    translates={},
                    establishment_name=request.user.establishment.name,
                    client_email=card.user.email,
                    card_uuid=card.uuid,
                    establishment_uuid=request.user.establishment_uuid,
                    discount=request.user.establishment.discount
                )
                await card_history_dao.create(db,history_data)
            except errors.BaseExceptionMixin as e:
                raise errors.HTTPError(msg=e.msg,code=e.code)
            else:
                return await card_dao.update_code(db,card.uuid)

    @staticmethod
    async def get_select(
            *, type: CardType|None = None, 
            status: StatusType|None = None,
            created_before:datetime|None,
            created_after:datetime|None,
            expire_before:datetime|None,
            expire_after:datetime|None) -> Select:
        return await card_dao.get_list(
            type=type,
            status=status,
            created_before=created_before,
            created_after=created_after,
            expire_before=expire_before,
            expire_after=expire_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            card = await card_dao.get(db, uuid)
            if not card:
                raise errors.NotFoundError(msg='Card does not exist')
            return await card_dao.delete(db, card.uuid)


card_service = CardService()