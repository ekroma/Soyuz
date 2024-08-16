#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select, and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from src.app.core.model import LoginLog
from src.app.core.schema.login_log import CreateLoginLogParam


class CRUDLoginLog(CRUDPlus[LoginLog]):
    async def get_list(self,user_uuid: str | None = None, email: str | None = None, status: int | None = None, ip: str | None = None) -> Select:
        se = select(self.model).order_by(desc(self.model.created_time))
        where_list = []
        if user_uuid:
            where_list.append(self.model.user_uuid.like(f'%{user_uuid}%'))
        if email:
            where_list.append(self.model.email.like(f'%{email}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if ip:
            where_list.append(self.model.ip.like(f'%{ip}%'))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def create(self, db: AsyncSession, obj_in: CreateLoginLogParam) -> None:
        await self.create_model(db, obj_in)
        await db.commit()

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        logs = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return logs.rowcount

    async def delete_all(self, db: AsyncSession) -> int:
        logs = await db.execute(delete(self.model))
        return logs.rowcount


login_log_dao: CRUDLoginLog = CRUDLoginLog(LoginLog)
