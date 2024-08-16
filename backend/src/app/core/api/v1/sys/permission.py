#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Request
from src.app.core.schema.permission import (
    CreatePermissionSchema,
    UpdatePermissionSchema,
    ReadPermissionSchema,
    ListPermissionSchema
)
from src.app.core.service.permission_service import permission_service
from src.common.enums import PermissionScopes, StatusType
from src.common.pagination import DependsPagination, paging_data
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
        '/create', 
        summary='Create Permission',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.permission:'c'})),
            DependsRBAC,],)
async def create_permission(db: CurrentSession,obj: CreatePermissionSchema) -> ResponseModel:
    await permission_service.create(obj=obj)
    return await response_base.success()

@router.get(
        '/{uuid}', 
        summary='Get Permission Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.permission:'r'})),
            DependsRBAC,],
        response_model=ResponseModel[ReadPermissionSchema])
async def get_permission(
        uuid: Annotated[str, Path(...)]) -> ResponseModel:
    permission = await permission_service.get_permission_info(uuid=uuid)
    return await response_base.success(data=permission)

@router.put(
        '/{uuid}', 
        summary='Update Permission Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.permission:'u'})),
            DependsRBAC,])
async def update_permission(
        request: Request, 
        uuid: Annotated[str, Path(...)], 
        obj: UpdatePermissionSchema) -> ResponseModel:
    count = await permission_service.update(request=request, permission_uuid=uuid, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '',
    summary='Get All Permissions with Pagination',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.permission:'r'})),
        DependsRBAC,
        DependsPagination])
async def get_pagination_permissions(
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[StatusType | None, Query()] = None) -> ResponseModel:
    permission_select = await permission_service.get_select(name=name, status=status)
    page_data = await paging_data(db, permission_select, ListPermissionSchema)
    return await response_base.success(data=page_data)

@router.put(
        '/{uuid}/status', 
        summary='Update Permission Status', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.permission:'u'})),
            DependsRBAC,])
async def status_set_permission(
        uuid: Annotated[str, Path(...)], 
        status: Annotated[StatusType, Query(...)]) -> ResponseModel:
    count = await permission_service.update_status(permission_uuid=uuid, status=status)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.delete(
    path='/{uuid}',
    summary='Delete Permission',
    description='Permission deletion will remove it from the database',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.permission:'d'})),
        DependsRBAC])
async def delete_permission(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await permission_service.delete(permission_uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
