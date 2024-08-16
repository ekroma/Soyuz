#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path

from src.app.task.service.task_service import task_service
from src.common.response.response_schema import ResponseModel, response_base
from src.common.enums import PermissionScopes
from src.common.security.jwt import DependsJwtAuth
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC

router = APIRouter()


@router.get('', summary='Get all executable task modules', dependencies=[DependsJwtAuth]) 
async def get_all_tasks() -> ResponseModel:
    tasks = task_service.get_list()
    return await response_base.success(data=tasks)


@router.get('/current', summary='Get currently executing tasks', dependencies=[DependsJwtAuth])
async def get_current_task() -> ResponseModel:
    task = task_service.get()
    return await response_base.success(data=task)


@router.get('/{uid}/status', summary='Get task status', dependencies=[DependsJwtAuth])
async def get_task_status(uid: Annotated[str, Path(description='Task ID')]) -> ResponseModel:
    status = task_service.get_status(uid)
    return await response_base.success(data=status)


@router.get('/{uid}', summary='Get task result', dependencies=[DependsJwtAuth])
async def get_task_result(uid: Annotated[str, Path(description='Task ID')]) -> ResponseModel:
    task = task_service.get_result(uid)
    return await response_base.success(data=task)


@router.post(
    '/{name}',
    summary='Execute task',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.task:'crud'})),
        DependsRBAC,
    ],
)
async def run_task(
    name: Annotated[str, Path(description='Task name')],
    args: Annotated[list | None, Body(description='Task function positional arguments')] = None,
    kwargs: Annotated[dict | None, Body(description='Task function keyword arguments')] = None,
) -> ResponseModel:
    task = task_service.run(name=name, args=args, kwargs=kwargs)
    return await response_base.success(data=task)