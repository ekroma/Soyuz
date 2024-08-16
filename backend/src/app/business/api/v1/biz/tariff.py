#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from datetime import datetime

from src.app.business.schema.tariff import (
    CreateTariffSchema,
    ReadTariffSchema,
    UpdateTariffSchema,
    ListTariffSchema
)
from src.common.enums import CardType, StatusType
from src.app.business.service.tariff_service import tariff_service
from src.common.pagination import DependsPagination, paging_data
from src.common.enums import PermissionScopes
from src.common.security.jwt import DependsJwtAuth
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
    '', 
    summary='Create tariff',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.tariff: 'c'})),
        DependsRBAC,],
    response_model=ResponseModel[ReadTariffSchema])
async def create_tariff(obj: CreateTariffSchema) -> ResponseModel:
    tariff =await tariff_service.create(obj=obj)
    return await response_base.success(data=tariff)

@router.get(
    '/all',
    summary='Get All Tariffs with Pagination',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.tariff: 'r'})),
        DependsRBAC,
        DependsPagination]
)
async def get_pagination_tariffs(
        db: CurrentSession,
        card_type: Annotated[CardType | None, Query()] = None,
        status: Annotated[StatusType, Query()] = StatusType.enable,
        created_before: Annotated[datetime | None, Query()] = None,
        created_after: Annotated[datetime | None, Query()] = None,):
    tariff_select = await tariff_service.get_select(
        card_type=card_type,
        status=status,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db,tariff_select, ListTariffSchema)
    return await response_base.success(data=page_data)

@router.get(
    '/{uuid}', 
    summary='Get Tariff Info', 
    dependencies=[
        Depends(RequestPermission({PermissionScopes.tariff: 'r'})),
        DependsRBAC,],
    response_model=ResponseModel[ReadTariffSchema])
async def get_tariff(
        uuid: Annotated[str, Path(...)])-> ResponseModel:
    tariff = await tariff_service.get_tariff_info(uuid=uuid)
    return await response_base.success(data=tariff)

@router.patch(
    '/{uuid}', 
    summary='Update Tariff Info', 
    dependencies=[
        Depends(RequestPermission({PermissionScopes.tariff: 'u'})),
        DependsRBAC,])
async def update_tariff(
        uuid: Annotated[str, Path(...)], 
        obj: UpdateTariffSchema) -> ResponseModel:
    count = await tariff_service.update(uuid=uuid, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '/all/client',
    summary='Get All Tariffs with Pagination',
    dependencies=[DependsPagination]
)
async def get_pagination_tariffs_active(
        db: CurrentSession,
        card_type: Annotated[CardType | None, Query()] = None,
        created_before: Annotated[datetime | None, Query()] = None,
        created_after: Annotated[datetime | None, Query()] = None,) -> ResponseModel:
    user_select = await tariff_service.get_select(
        card_type=card_type,
        status=StatusType.enable,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, user_select, ListTariffSchema)
    return await response_base.success(data=page_data)


@router.delete(
    '/{uuid}',
    summary='Delete Tariff',
    description='Tariff deletion will remove the tariff from the database',
    dependencies=[
        Depends(RequestPermission({PermissionScopes.tariff: 'd'})),
        DependsRBAC,])
async def delete_tariff(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await tariff_service.delete(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
