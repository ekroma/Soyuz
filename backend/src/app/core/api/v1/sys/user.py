#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Body
from pydantic import EmailStr

from src.app.core.schema.user import (
    AddUserParam,
    AvatarParam,
    GetUserInfoDetail,
    GetUserInfoListDetails,
    RegisterUserParam,
    ResetPasswordParam,
    UpdateUserParam,
    RestorePasswordParam
)
from src.app.core.service.user_service import user_service
from src.common.security.jwt import superuser_verify
from src.common.enums import PermissionScopes, StatusType
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.jwt import DependsJwtAuth
from src.common.security.permission import RequestPermission
from src.common.security.rbac import DependsRBAC
from src.common.pagination import DependsPagination, paging_data
from database.db_psql import CurrentSession

router = APIRouter()

@router.post(
        '/pre-register', 
        summary='Pre-Register User')
async def pre_register_user(email: Annotated[str, Query()]) -> ResponseModel:
    await user_service.pre_register(email=email)
    return await response_base.success()

@router.post(
        '/register', 
        summary='Register User')
async def register_user(
        obj: RegisterUserParam,
        code: Annotated[str, Query()]) -> ResponseModel:
    await user_service.register(code=code,obj=obj)
    return await response_base.success()

@router.post(
        '/add', 
        summary='Add User', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.user:'c'})),
            DependsRBAC,],
        response_model=ResponseModel[GetUserInfoDetail])
async def add_user(request: Request, obj: AddUserParam) -> ResponseModel:
    await user_service.add(request=request, obj=obj)
    current_user = await user_service.get_user_info(email=obj.email)
    return await response_base.success(data=current_user)

@router.post(
        '/password/reset', 
        summary='Reset Password', 
        dependencies=[DependsJwtAuth])
async def password_restore(request: Request, obj: ResetPasswordParam) -> ResponseModel:
    count = await user_service.pwd_reset(request=request, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.post(
        '/password/pre-restore', 
        summary='Reset Password', 
        dependencies=[DependsJwtAuth])
async def pre_password_restore(email:EmailStr) -> ResponseModel:
    count = await user_service.pre_pwd_restore(email=email)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.post(
        '/password/restore', 
        summary='Reset Password', 
        dependencies=[DependsJwtAuth])
async def password_reset(request: Request, obj: RestorePasswordParam) -> ResponseModel:
    count = await user_service.pwd_restore(request=request, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
        '/me', 
        summary='Get Current User Info', 
        dependencies=[DependsJwtAuth],
        response_model=ResponseModel[GetUserInfoDetail])
async def get_current_user(request: Request):
    return await response_base.success(data=request.user)

@router.get(
        '/{email}', 
        summary='Get User Info', 
        dependencies=[DependsJwtAuth],
        response_model=ResponseModel[GetUserInfoDetail])
async def get_user(email: Annotated[str, Path(...)]) -> ResponseModel:
    current_user = await user_service.get_user_info(email=email)
    return await response_base.success(data=current_user)

@router.put(
        '/role/{email}', 
        summary='Update User Role', 
        dependencies=[DependsJwtAuth])
async def update_user_role(
        request: Request, 
        email: Annotated[str, Path(...)], 
        role_uuids:list[str] = Body(...)) -> ResponseModel:
    count = await user_service.update_role(
        request=request, 
        email=email, 
        role_uuids=role_uuids)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.put(
        '/{email}', 
        summary='Update User Info', 
        dependencies=[DependsJwtAuth])
async def update_user(
        request: Request, 
        email: Annotated[str, Path(...)], 
        obj: UpdateUserParam) -> ResponseModel:
    count = await user_service.update(request=request, email=email, obj=obj)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.put(
        '/{uuid}/establishment', 
        summary='Update User establishment', 
        dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.user:'u'})),
            DependsRBAC,])
async def update_user_establishment(
        request: Request, 
        uuid: Annotated[str, Path(...)], 
        establishment_uuid: Annotated[str, Query(...)]) -> ResponseModel:
    count = await user_service.update_establishment(request=request, pk=uuid, establishment_uuid=establishment_uuid)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.get(
    '',
    summary='Get All Users with Pagination',
    dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.user:'r'})),
            DependsRBAC,
            DependsPagination],
)
async def get_pagination_users(
    db: CurrentSession,
    email: Annotated[str | None, Query()] = None,
    phone: Annotated[str | None, Query()] = None,
    status: Annotated[StatusType | None, Query()] = None,
) -> ResponseModel:
    user_select = await user_service.get_select(
        email=email, 
        phone=phone, 
        status=status)
    page_data = await paging_data(db, user_select, GetUserInfoListDetails)
    return await response_base.success(data=page_data)

@router.put(
        '/{pk}/super', 
        summary='Update User Super Permission', 
        dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.user:'u'})),
            DependsRBAC,],
        status_code=200)
async def super_set(request: Request, pk: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.update_permission(request=request, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.put(
        '/{pk}/staff', 
        summary='Update User Staff Permission', 
        dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.user:'u'})),
            DependsRBAC,],)
async def staff_set(request: Request, pk: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.update_staff(request=request, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.put(
        '/{pk}/status', 
        summary='Update User Status', 
        dependencies=[
            Depends(superuser_verify),
            Depends(RequestPermission({PermissionScopes.user:'u'})),
            DependsRBAC,],)
async def status_set_user(request: Request, pk: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.update_status(request=request, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.put(
        '/{pk}/multi', 
        summary='Update User Multi Login Status', 
        dependencies=[
            Depends(RequestPermission({PermissionScopes.user:'u'})),
            DependsRBAC,],)
async def multi_set(request: Request, pk: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.update_multi_login(request=request, pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

@router.delete(
        path='/{email}',
        summary='Delete User',
        description='User deletion != User logout, after deletion, the user will be removed from the database',
        dependencies=[
            Depends(RequestPermission({PermissionScopes.user:'d'})),
            DependsRBAC,],)
async def delete_user(email: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.delete(email=email)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()
