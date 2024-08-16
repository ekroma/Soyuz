#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.app.core.service.opera_log_service import opera_log_service
from src.common.pagination import DependsPagination, paging_data
from src.common.enums import PermissionScopes
from src.common.response.response_schema import ResponseModel, response_base
from src.common.enums import StatusType
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from src.app.core.schema.opera_log import GetOperaLogListDetails
from database.db_psql import CurrentSession

router = APIRouter()


@router.get(
    '',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'r'})),
        DependsRBAC,
        DependsPagination
    ],
)
async def get_pagination_opera_logs(
    db: CurrentSession,
    email: Annotated[str | None, Query()] = None,
    status: Annotated[StatusType | None, Query()] = None,
    ip: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 10,
) -> ResponseModel:
    opera_log_select = await opera_log_service.get_select(
        email=email, 
        status=status, 
        ip=ip)
    page_data = await paging_data(db, opera_log_select, GetOperaLogListDetails)
    return await response_base.success(data=page_data)

@router.delete(
    '',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'d'})),
        DependsRBAC,
    ],
)
async def delete_opera_log(pk: Annotated[list[str], Query(...)]) -> ResponseModel:
    count = await opera_log_service.delete(pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()


@router.delete(
    '/all',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'d'})),
        DependsRBAC]
)
async def delete_all_opera_logs() -> ResponseModel:
    count = await opera_log_service.delete_all()
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
