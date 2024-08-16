#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Select
from fastapi import Request
from src.app.core.crud.crud_permission import permission_dao
from src.app.core.model import Permission
from src.app.core.schema.permission import (
    CreatePermissionSchema,
    UpdatePermissionSchema
)
from src.common.exception import errors
from database.db_psql import async_db_session
from src.common.enums import StatusType

class PermissionService:
    @staticmethod
    async def create(*, obj: CreatePermissionSchema) -> Permission:
        async with async_db_session.begin() as db:
            return await permission_dao.create(db, obj)

    @staticmethod
    async def get_permission_info(*, uuid: str) -> Permission:
        async with async_db_session() as db:
            permission = await permission_dao.get_with_relation(db, permission_uuid=uuid)
            if not permission:
                raise errors.NotFoundError(msg='Permission does not exist')
            return permission

    @staticmethod
    async def update(*, request: Request, permission_uuid: str, obj: UpdatePermissionSchema) -> int:
        async with async_db_session.begin() as db:
            permission = await permission_dao.get(db, permission_uuid)
            if not permission:
                raise errors.NotFoundError(msg='Permission does not exist')
            return await permission_dao.update_permission_info(db, permission_uuid, obj)

    @staticmethod
    async def get_select(*, name: str|None = None, status: StatusType|None = None)->Select:
        return await permission_dao.get_list(name=name, status=status)

    @staticmethod
    async def update_status(*, permission_uuid: str, status: StatusType) -> int:
        async with async_db_session.begin() as db:
            permission = await permission_dao.get(db, permission_uuid)
            if not permission:
                raise errors.NotFoundError(msg='Permission does not exist')
            return await permission_dao.update_status(db, permission_uuid, status)

    @staticmethod
    async def delete(*, permission_uuid: str) -> int:
        async with async_db_session.begin() as db:
            permission = await permission_dao.get(db, permission_uuid)
            if not permission:
                raise errors.NotFoundError(msg='Permission does not exist')
            return await permission_dao.delete(db, permission_uuid)

permission_service = PermissionService()
