#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.app.core.service.login_log_service import login_log_service
from src.common.response.response_schema import ResponseModel, response_base
from src.common.enums import StatusType
from src.common.pagination import DependsPagination, paging_data
from src.common.security.permission import RequestPermission
from src.app.core.schema.login_log import GetLoginLogListDetails
from src.common.security.rbac import DependsRBAC
from src.common.enums import PermissionScopes
from database.db_psql import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='Get paginated login logs with optional filters',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'r'})),
        DependsRBAC,
        DependsPagination
    ],
)
async def get_pagination_login_logs(
    db: CurrentSession,
    email: Annotated[str | None, Query()] = None,
    status: Annotated[StatusType | None, Query()] = None,
    ip: Annotated[str | None, Query()] = None,
) -> ResponseModel:
    log_select = await login_log_service.get_select(
        email=email, 
        status=status, 
        ip=ip)
    page_data = await paging_data(db, log_select, GetLoginLogListDetails)
    return await response_base.success(data=page_data)

@router.delete(
    '',
    summary='Batch delete login logs',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'d'})),
        DependsRBAC,
    ],
)
async def delete_login_log(pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await login_log_service.delete(pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.delete(
    '/all',
    summary='Clear all login logs',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'d'})),
        DependsRBAC]
)
async def delete_all_login_logs() -> ResponseModel:
    count = await login_log_service.delete_all()
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
