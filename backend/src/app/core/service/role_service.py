#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from src.app.core.crud.crud_role import role_dao
from src.app.core.model import Role
from src.app.core.schema.role import (
    CreateRoleSchema,
    UpdateRoleSchema
)
from src.common.exception import errors
from src.common.enums import StatusType
from database.db_psql import async_db_session

class RoleService:
    @staticmethod
    async def create(*, obj: CreateRoleSchema) -> Role|None:
        async with async_db_session.begin() as db:
            return await role_dao.create(db,obj)

    @staticmethod
    async def get_role_info(*, name: str) -> Role:
        async with async_db_session() as db:
            role = await role_dao.get_with_relations(db, name=name)
            if not role:
                raise errors.NotFoundError(msg='Role does not exist')
            return role

    @staticmethod
    async def update(*, request: Request, role_uuid: str, obj: UpdateRoleSchema) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, role_uuid)
            if not role:
                raise errors.NotFoundError(msg='Role does not exist')
            return await role_dao.update_role_info(db, role_uuid, obj)

    @staticmethod
    async def get_select(*, name: str | None = None,status: StatusType | None = None):
        return await role_dao.get_list(name=name,status=status)

    @staticmethod
    async def update_status(*, request: Request, role_uuid: str, status: StatusType) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, role_uuid)
            if not role:
                raise errors.NotFoundError(msg='Role does not exist')
            return await role_dao.update_status(db, role_uuid, status)

    @staticmethod
    async def delete(*, role_uuid: str) -> int:
        async with async_db_session.begin() as db:
            role = await role_dao.get(db, role_uuid)
            if not role:
                raise errors.NotFoundError(msg='Role does not exist')
            return await role_dao.delete(db, role_uuid)

role_service = RoleService()
