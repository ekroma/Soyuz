#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from fastapi import Request
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.crud.crud_login_log import login_log_dao
from src.app.core.model import User
from src.app.core.schema.login_log import CreateLoginLogParam
from src.common.log import log
from src.common.enums import StatusType
from database.db_psql import async_db_session


class LoginLogService:
    @staticmethod
    async def get_select(*, email: str|None, status: StatusType|None, ip: str|None,):
        return await login_log_dao.get_list(email=email, status=status, ip=ip)

    @staticmethod
    async def create(
        *, db: AsyncSession, request: Request, user: User, login_time: datetime, status: StatusType, msg: str
    ) -> None:
        try:
            obj_in = CreateLoginLogParam(
                user_uuid=user.uuid,
                email=user.email,
                status=status,
                ip=request.state.ip,
                country=request.state.country,
                region=request.state.region,
                city=request.state.city,
                user_agent=request.state.user_agent,
                browser=request.state.browser,
                os=request.state.os,
                device=request.state.device,
                msg=msg,
                login_time=login_time,
            )
            await login_log_dao.create(db, obj_in)
        except Exception as e:
            log.exception(f'Failed to create login log: {e}')

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await login_log_dao.delete(db, pk)
            return count

    @staticmethod
    async def delete_all() -> int:
        async with async_db_session.begin() as db:
            count = await login_log_dao.delete_all(db)
            return count


login_log_service = LoginLogService()
