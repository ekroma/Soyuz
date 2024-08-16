#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, desc, and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.core.model import Role
from src.app.core.crud.crud_permission import permission_dao
from src.app.core.schema.role import (
    CreateRoleSchema,
    UpdateRoleSchema
)
from src.common.exception import errors
from src.common.enums import StatusType
from src.common.crud import BaseCRUDPlus

class CRUDRole(BaseCRUDPlus[Role]):

    async def create(self, db: AsyncSession, obj: CreateRoleSchema) -> Role|None:
        dict_obj = obj.model_dump(exclude={'perm_uuids'})
        new_role = self.model(**dict_obj)
        permissions = []
        for perm_uuid in obj.perm_uuids:
            perm = await permission_dao.get(db,uuid=perm_uuid)
            if not perm:
                raise errors.NotFoundError(msg=f'Permission with uuid {perm_uuid} not found')
            permissions.append(perm)
        new_role.permissions = permissions

        db.add(new_role)
        await db.flush()
        await db.refresh(new_role)
        return new_role

    async def update_role_info(self, db: AsyncSession, role_id: str, obj: UpdateRoleSchema) -> int:
        return await self.update_model(db, role_id, obj)

    async def delete(self, db: AsyncSession, role_id: str) -> int:
        return await self.delete_model(db, role_id)

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

    async def update_status(self, db: AsyncSession, role_uuid: str, status:StatusType) -> int:
        return await self.update_model(db, role_uuid, {'status': status})

    async def get_with_relations(self, db: AsyncSession, *, role_uuid: str | None = None, name: str | None = None) -> Role | None:
        where = []
        if role_uuid:
            where.append(self.model.uuid == role_uuid)
        if name:
            where.append(self.model.translates[('en')][('name')].astext == name)
        role = await db.execute(
            select(self.model)
            .options(selectinload(self.model.permissions), 
                    selectinload(self.model.users))
            .where(*where)
        )
        return role.scalars().first()

role_dao: CRUDRole = CRUDRole(Role)
