#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, and_, desc, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload

from src.app.core.model import Permission
from src.app.core.schema.permission import (
    CreatePermissionSchema, UpdatePermissionSchema
)
from src.common.enums import StatusType
from src.common.crud import BaseCRUDPlus

class CRUDPermission(BaseCRUDPlus[Permission]):

    async def create(self, db: AsyncSession, obj: CreatePermissionSchema) -> Permission:
        return await self.create_model(db,obj)

    async def update_permission_info(self, db: AsyncSession, permission_uuid: str, obj: UpdatePermissionSchema) -> int:
        return await self.update_model(db, permission_uuid, obj)

    async def delete(self, db: AsyncSession, permission_uuid: str) -> int:
        return await self.delete_model(db, permission_uuid)

    async def get_list(
            self, 
            name: str | None = None, 
            status: StatusType | None = None) -> Select:
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if name:
            where_list.append(self.model.translates[('en')][('name')].astext == name)
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def update_status(self, db: AsyncSession, permission_uuid: str, status: StatusType) -> int:
        return await self.update_model(db, permission_uuid, {'status': status})

    async def get_with_relation(self, db: AsyncSession, *,permission_id: int | None = None, permission_uuid: str | None = None) -> Permission | None:
        where = []
        if permission_id:
            where.append(self.model.id == permission_id)
        if permission_uuid:
            where.append(self.model.uuid == permission_uuid)
        permission = await db.execute(
            select(self.model)
            .where(*where)
        )
        return permission.scalars().first()

permission_dao: CRUDPermission = CRUDPermission(Permission)
