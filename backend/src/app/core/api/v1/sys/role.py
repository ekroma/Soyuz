#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from src.app.core.schema.role import (
    CreateRoleSchema,
    UpdateRoleSchema,
    ReadRoleSchema,
    ListRoleSchema
)
from src.common.response.response_schema import response_base, ResponseModel
from src.app.core.service.role_service import role_service
from src.common.enums import PermissionScopes, StatusType
from src.common.pagination import DependsPagination, paging_data
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
    '/create', 
    summary='Create Role',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.role:'c'})),
        DependsRBAC],
    response_model=ResponseModel[ReadRoleSchema])
async def create_role(obj: CreateRoleSchema):
    role = await role_service.create(obj=obj)
    return await response_base.success(data=role)

@router.get(
    '/{name}', 
    summary='Get Role Info', 
    dependencies=[
        Depends(RequestPermission({PermissionScopes.role:'r'})),
        DependsRBAC],
    response_model=ResponseModel[ReadRoleSchema])
async def get_role(name: Annotated[str, Path(...)]):
    role = await role_service.get_role_info(name=name)
    return await response_base.success(data=role)

@router.put(
        '/{uuid}', 
        summary='Update Role Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.role:'u'})),
            DependsRBAC])
async def update_role(
        request: Request, 
        uuid: Annotated[str, Path(...)], 
        obj: UpdateRoleSchema):
    count = await role_service.update(request=request, role_uuid=uuid, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '',
    summary='Get All Roles with Pagination',
    dependencies=[
            Depends(RequestPermission({PermissionScopes.role:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_roles(
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    status: Annotated[StatusType | None, Query()] = None):
    role_select = await role_service.get_select(name=name, status=status)
    page_data = await paging_data(db, role_select, ListRoleSchema)
    return await response_base.success(data=page_data)

@router.put(
        '/{uuid}/status', 
        summary='Update Role Status', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.role:'u'})),
            DependsRBAC,])
async def status_set_role(
        request: Request, 
        uuid: Annotated[str, Path(...)], 
        status: Annotated[StatusType, Query(...)]):
    count = await role_service.update_status(request=request, role_uuid=uuid, status=status)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.delete(
    path='/{uuid}',
    summary='Delete Role',
    description='Role deletion will remove it from the database',
    dependencies=[
            Depends(RequestPermission({PermissionScopes.role:'d'})),
            DependsRBAC])
async def delete_role(uuid: Annotated[str, Path(...)]):
    count = await role_service.delete(role_uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
