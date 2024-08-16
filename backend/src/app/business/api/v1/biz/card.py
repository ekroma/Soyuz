#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from datetime import datetime

from src.app.business.schema.card import (
    CreateCardSchema,
    ReadCardSchema,
    ReadDetailCardSchema,
    UpdateCardSchema
)
from src.utils.tools import generate_card_qr_code
from src.common.pagination import DependsPagination, paging_data
from src.common.enums import CardType, StatusType, PermissionScopes
from src.app.business.service.card_service import card_service
from src.common.exception import errors
from src.common.security.jwt import DependsJwtAuth
from src.common.response.response_schema import response_base, ResponseModel
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
    '', 
    summary='Create card',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel[ReadDetailCardSchema])
async def create_card(
        request: Request, 
        obj:CreateCardSchema) -> ResponseModel:
    if request.user.card:
        raise errors.ConflictError(msg="Card already exist")
    card = await card_service.create(request,obj=obj)
    return await response_base.success(data=card)

@router.get(
        '/user-card', 
        summary='Get User Card Info', 
        dependencies=[DependsJwtAuth],
        response_model=ResponseModel[ReadDetailCardSchema])
async def get_user_card(request: Request) -> ResponseModel:
    if not request.user.card:
        raise errors.NotFoundError(msg="Card not found")
    return await response_base.success(data=request.user.card)

@router.get(
        '', 
        summary='Get Card Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC],
        response_model=ResponseModel[ReadDetailCardSchema])
async def get_card(
        uuid: Annotated[str, Path(...)]):
    card = await card_service.get_card_info(card_uuid=uuid)
    return await response_base.success(data=card)

@router.get(
        '/qrcode', 
        summary='Get Card QRCode', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC],
        response_model=ResponseModel)
async def get_card_qrcode(request:Request):
    if not request.user.card:
        raise errors.NotFoundError(msg='Card not found')
    qrcode = generate_card_qr_code(request.user.card.uuid,request.user.card.code)
    return await response_base.success(data=qrcode)

@router.get(
        '/card-use/{uuid}/{code}', 
        summary='Accept Card Discount', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC])
async def accept_card(
        uuid:Annotated[str, Path(...)],
        code: Annotated[str, Path(...)],
        request:Request):
    count = await card_service.accept_card_use(request=request,uuid=uuid,code=code)
    if count > 0:
        return await response_base.success(data="Card discount used")
    return await response_base.fail()

@router.patch(
        '/{uuid}', 
        summary='Update Card Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'u'})),
            DependsRBAC,])
async def update_card(
        uuid: Annotated[str, Path(...)], 
        obj: UpdateCardSchema):
    count = await card_service.update(uuid=uuid,obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '/all',
    summary='Get All Cads with Pagination',
    dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_cards(
        db: CurrentSession,
        type: Annotated[CardType | None, Query()] = None,
        status: Annotated[StatusType | None, Query()] = None,
        created_before: Annotated[datetime| None, Query()] = None,
        created_after: Annotated[datetime| None, Query()] = None,
        expire_before: Annotated[datetime| None, Query()] = None,
        expire_after: Annotated[datetime| None, Query()] = None,
):
    card_select = await card_service.get_select(
        type=type,
        status=status,
        created_before=created_before,
        created_after=created_after,
        expire_before=expire_before,
        expire_after=expire_after)
    page_data = await paging_data(db, card_select, ReadCardSchema)
    return await response_base.success(data=page_data)

@router.delete(
        path='/{email}',
        summary='Delete Card',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.card:'d'})),
            DependsRBAC,])
async def delete_card(
        uuid: Annotated[str, Path(...)]):
    count = await card_service.delete(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
