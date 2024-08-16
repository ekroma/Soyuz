#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from datetime import datetime

from src.app.organizations.schema.counseling import (
    CreateCounselingSchema,
    ReadCounselingSchema,
    UpdateCounselingSchema
)
from src.common.enums import StatusType
from src.app.organizations.service.counseling_service import counseling_service
from src.common.enums import PermissionScopes
from src.common.security.jwt import DependsJwtAuth
from src.common.pagination import DependsPagination, paging_data
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
        '', 
        summary='Create counseling')
async def create_counseling(obj: CreateCounselingSchema) -> ResponseModel:
    await counseling_service.create(obj=obj)
    return await response_base.success()

@router.get(
        '/by/{uuid}', 
        summary='Get counseling Info', 
        dependencies=[DependsJwtAuth], 
        response_model=ReadCounselingSchema)
async def get_counseling(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    counseling = await counseling_service.get_counseling_info(counseling_uuid=uuid)
    return await response_base.success(data=counseling)

@router.patch(
        '/{uuid}', 
        summary='Update counseling Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.counseling:'u'})),
            DependsRBAC,])
async def update_counseling(uuid: Annotated[str, Path(...)], status: StatusType) -> ResponseModel:
    count = await counseling_service.update_info(uuid=uuid, status=status)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '/all',
    summary='Get all counselings with pagination',
    dependencies=[
            Depends(RequestPermission({PermissionScopes.counseling:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_counselings(
        db: CurrentSession,
        status: Annotated[StatusType | None, Query()] = None,
        created_before: Annotated[datetime | None, Query()] = None,
        created_after: Annotated[datetime | None, Query()] = None) -> ResponseModel:
    counseling_select = await counseling_service.get_select(
        status=status,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, counseling_select, ReadCounselingSchema)
    return await response_base.success(data=page_data)

@router.delete(
        '/{uuid}',
        summary='Delete counseling',
        description='Counseling deletion != User logout, after deletion, the counseling will be removed from the database',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.counseling:'d'})),
            DependsRBAC,])
async def delete_counseling(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await counseling_service.delete(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()