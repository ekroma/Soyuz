#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from datetime import datetime

from src.app.business.schema.card_history import (
    CardHistorySchemaBase,
    ReadCardHistorySchema,
    UpdateCardHistorySchema
)
from src.common.security.jwt import superuser_verify, staff_verify, DependsJwtAuth
from src.common.pagination import DependsPagination, paging_data
from src.common.enums import CardType, StatusType, PermissionScopes
from src.app.business.service.card_history_service import card_history_service
from src.common.exception import errors
from src.common.response.response_schema import response_base, ResponseModel
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.patch(
        '/{uuid}', 
        summary='Update Card Info', 
        dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.card:'u'})),
            DependsRBAC,])
async def update_card_history(
        uuid: Annotated[str, Path(...)], 
        obj: UpdateCardHistorySchema):
    count = await card_history_service.update(uuid=uuid,obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '/all',
    summary='Get All Card history with Pagination',
    dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_card_history(
        db: CurrentSession,
        establishment_uuid: Annotated[str | None, Query()] = None,
        card_uuid: Annotated[str | None, Query()] = None,
        created_before: Annotated[datetime| None, Query()] = None,
        created_after: Annotated[datetime| None, Query()] = None,
):
    card_history_select = await card_history_service.get_select(
        establishment_uuid=establishment_uuid,
        card_uuid=card_uuid,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, card_history_select, ReadCardHistorySchema)
    return await response_base.success(data=page_data)

@router.get(
    '/staff-establishment',
    summary='Get All Establishment Card history with Pagination',
    dependencies=[
            Depends(staff_verify),
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_cards_establishment(
        db: CurrentSession,
        request:Request,
        card_uuid: Annotated[str | None, Query()] = None,
        created_before: Annotated[datetime| None, Query()] = None,
        created_after: Annotated[datetime| None, Query()] = None,
):
    if not request.user.establishment:
        raise errors.HTTPError(code=404,msg="Establishment not found")
    card_history_select = await card_history_service.get_select(
        establishment_uuid=request.user.establishment.uuid,
        card_uuid=card_uuid,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, card_history_select, ReadCardHistorySchema)
    return await response_base.success(data=page_data)

@router.get(
    '/client-history',
    summary='Get All Client Card history with Pagination',
    dependencies=[
        DependsJwtAuth,
        DependsPagination])
async def get_pagination_client_card_history(
        db: CurrentSession,
        request:Request,
        establishment_uuid: Annotated[str | None, Query()] = None,
        card_uuid: Annotated[str | None, Query()] = None,
        created_before: Annotated[datetime| None, Query()] = None,
        created_after: Annotated[datetime| None, Query()] = None,
):
    if not request.user.card:
        raise errors.HTTPError(code=404,msg="Card not found")
    card_history_select = await card_history_service.get_select(
        establishment_uuid=establishment_uuid,
        card_uuid=request.user.card.uuid,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, card_history_select, ReadCardHistorySchema)
    return await response_base.success(data=page_data)

@router.delete(
        path='/{email}',
        summary='Delete Card History',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'d'})),
            DependsRBAC,])
async def delete_card_history(
        uuid: Annotated[str, Path(...)]):
    count = await card_history_service.delete(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
