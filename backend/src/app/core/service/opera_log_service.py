#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select

from src.app.core.crud.crud_opera_log import opera_log_dao
from src.app.core.schema.opera_log import CreateOperaLogParam
from database.db_psql import async_db_session
from src.common.enums import StatusType

class OperaLogService:
    @staticmethod
    async def get_select(*, email: str | None = None, status: StatusType | None = None, ip: str | None = None) -> Select:
        return await opera_log_dao.get_list(email=email, status=status, ip=ip)

    @staticmethod
    async def create(*, obj_in: CreateOperaLogParam):
        async with async_db_session.begin() as db:
            await opera_log_dao.create(db, obj_in)

    @staticmethod
    async def delete(*, pk: list[str]) -> int:
        async with async_db_session.begin() as db:
            count = await opera_log_dao.delete(db, pk)
            return count

    @staticmethod
    async def delete_all() -> int:
        async with async_db_session.begin() as db:
            count = await opera_log_dao.delete_all(db)
            return count


opera_log_service = OperaLogService()
