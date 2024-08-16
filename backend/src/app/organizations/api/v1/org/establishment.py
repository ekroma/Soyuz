#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, UploadFile, File
from datetime import datetime

from src.app.organizations.schema.establishment import (
    CreateEstablishmentSchema,
    ReadEstablishmentSchema,
    UpdateEstablishmentSchema,
    ListEstablishmentSchema
)
from src.common.enums import StatusType
from src.app.organizations.service.establishment_service import establishment_service
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
        summary='Create establishment',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'c'})),
            DependsRBAC,])
async def create_establishment(obj: CreateEstablishmentSchema) -> ResponseModel:
    await establishment_service.create(obj=obj)
    return await response_base.success()

@router.get(
        '/by/{uuid}', 
        summary='Get Establishment Info', 
        dependencies=[DependsJwtAuth], 
        response_model=ReadEstablishmentSchema)
async def get_establishment(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    establishment = await establishment_service.get_establishment_info(establishment_uuid=uuid)
    return await response_base.success(data=establishment)

@router.patch(
        '/{uuid}', 
        summary='Update Establishment Info', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'u'})),
            DependsRBAC,])
async def update_establishment(uuid: Annotated[str, Path(...)], obj: UpdateEstablishmentSchema) -> ResponseModel:
    count = await establishment_service.update_info(uuid=uuid, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '/all',
    summary='Get All Establishments with Pagination',
    dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'r'})),
            DependsRBAC,
            DependsPagination])
async def get_pagination_establishments(
        db: CurrentSession,
        status: Annotated[StatusType | None, Query()] = None,
        created_before: Annotated[datetime | None, Query()] = None,
        created_after: Annotated[datetime | None, Query()] = None) -> ResponseModel:
    establishment_select = await establishment_service.get_select(
        status=status,
        created_before=created_before,
        created_after=created_after)
    page_data = await paging_data(db, establishment_select, ListEstablishmentSchema)
    return await response_base.success(data=page_data)

@router.delete(
        '/{uuid}',
        summary='Delete Establishment',
        description='Establishment deletion != User logout, after deletion, the establishment will be removed from the database',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'d'})),
            DependsRBAC,])
async def delete_establishment(uuid: Annotated[str, Path(...)]) -> ResponseModel:
    count = await establishment_service.delete(uuid=uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.post(
        '/{uuid}/images',
        summary='Add Images to Establishment',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'u'})),
            DependsRBAC,])
async def add_images(uuid: Annotated[str, Path(...)],images: list[UploadFile] = File(...)) -> ResponseModel:
    count = await establishment_service.add_images(uuid=uuid, images=images)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.delete(
        '/{uuid}/images',
        summary='Delete Images from Establishment',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.establishment:'u'})),
            DependsRBAC,])
async def delete_images(uuid: Annotated[str, Path(...)],images: list[str] = Query(...)) -> ResponseModel:
    count = await establishment_service.delete_images(uuid=uuid, images_path=images)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
