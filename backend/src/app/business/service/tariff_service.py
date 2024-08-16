#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from datetime import datetime

from src.app.business.crud.crud_tariff import tariff_dao
from src.app.business.model.biz_tariff import Tariff
from src.common.enums import CardType, StatusType
from src.app.business.schema.tariff import (
    CreateTariffSchema,
    UpdateTariffSchema 
)
from database.db_psql import async_db_session
from src.common.exception import errors

class TariffService:
    @staticmethod
    async def create(*, obj: CreateTariffSchema) -> Tariff:
        async with async_db_session.begin() as db:
            return await tariff_dao.create(db, obj)

    @staticmethod
    async def update(*, uuid: str, obj: UpdateTariffSchema) -> int:
        async with async_db_session.begin() as db:
            tariff = await tariff_dao.get(db, uuid)
            count = 0
            if not tariff:
                raise errors.NotFoundError(msg="Tariff not found")
            count += await tariff_dao.update_model(db, uuid, obj)
            return count

    @staticmethod
    async def get_tariff_info(*, uuid: str) -> Tariff:
        async with async_db_session() as db:
            tariff = await tariff_dao.get_with_relation(db, tariff_uuid=uuid)
            if not tariff:
                raise errors.NotFoundError(msg='Tariff does not exist')
            return tariff

    @staticmethod
    async def get_select(
            *, card_type: CardType | None = None, 
            status: StatusType = StatusType.enable,
            created_before: datetime | None = None,
            created_after: datetime | None = None):
        return await tariff_dao.get_list(
            card_type=card_type,
            status=status,
            created_before=created_before,
            created_after=created_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            tariff = await tariff_dao.get(db, uuid)
            if not tariff:
                raise errors.NotFoundError(msg='Tariff does not exist')
            return await tariff_dao.delete(db, tariff.uuid)

tariff_service = TariffService()
