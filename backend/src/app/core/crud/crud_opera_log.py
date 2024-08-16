#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select, and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from src.app.core.model import OperaLog
from src.app.core.schema.opera_log import CreateOperaLogParam


class CRUDOperaLogDao(CRUDPlus[OperaLog]):
    async def get_list(self, email: str | None = None, status: int | None = None, ip: str | None = None) -> Select:
        se = select(self.model).order_by(desc(self.model.created_time))
        where_list = []
        if email:
            where_list.append(self.model.email.like(f'%{email}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if ip:
            where_list.append(self.model.ip.like(f'%{ip}%'))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def create(self, db: AsyncSession, obj_in: CreateOperaLogParam) -> None:
        await self.create_model(db, obj_in)

    async def delete(self, db: AsyncSession, pk: list[str]) -> int:
        logs = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return logs.rowcount

    async def delete_all(self, db: AsyncSession) -> int:
        logs = await db.execute(delete(self.model))
        return logs.rowcount


opera_log_dao: CRUDOperaLogDao = CRUDOperaLogDao(OperaLog)
