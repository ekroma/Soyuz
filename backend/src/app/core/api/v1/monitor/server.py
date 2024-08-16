#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from src.common.response.response_schema import ResponseModel, response_base
from src.common.enums import PermissionScopes
from src.common.security.rbac import DependsRBAC
from src.common.security.permission import RequestPermission
from src.utils.server_info import server_info

router = APIRouter()


@router.get(
    '',
    summary='Server Monitoring',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'r'})),
        DependsRBAC,
    ],
)
async def get_server_info() -> ResponseModel:
    """IO-intensive task, using thread pool to minimize performance loss"""
    data = {
        'cpu': await run_in_threadpool(server_info.get_cpu_info),
        'mem': await run_in_threadpool(server_info.get_mem_info),
        'sys': await run_in_threadpool(server_info.get_sys_info),
        'disk': await run_in_threadpool(server_info.get_disk_info),
        'service': await run_in_threadpool(server_info.get_service_info),
    }
    return await response_base.success(data=data)
