#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from src.common.response.response_schema import ResponseModel, response_base
from src.common.enums import PermissionScopes
from src.common.security.rbac import DependsRBAC
from src.common.security.permission import RequestPermission
from src.utils.redis_info import redis_info

router = APIRouter()


@router.get(
    '',
    summary='Redis Monitoring',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.log:'r'})),
        DependsRBAC,
    ],
)
async def get_redis_info() -> ResponseModel:
    data = {'info': await redis_info.get_info(), 'stats': await redis_info.get_stats()}
    return await response_base.success(data=data)
