#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi_limiter.depends import RateLimiter
from starlette.background import BackgroundTasks

from src.app.core.schema.user import AuthLoginParam
from src.app.core.schema.token import GetLoginToken
from src.app.core.service.auth_service import auth_service
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.jwt import DependsJwtAuth

router = APIRouter()

@router.post(
    '/login',
    summary='User Login',
    description='JSON format login, only supported for third-party API tool debugging, such as Postman',
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    response_model=ResponseModel[GetLoginToken])
async def user_login(
        response: Response,
        request: Request, 
        obj: AuthLoginParam, 
        background_tasks: BackgroundTasks) -> ResponseModel:
    data = await auth_service.login(
        request=request, 
        obj=obj, 
        background_tasks=background_tasks)
    auth_service.set_token_cookies(
        response=response,
        access_token=data.access_token,
        refresh_token=data.refresh_token)
    return await response_base.success(data=data)

@router.post(
    '/refresh-token', 
    summary='Refresh token', 
    dependencies=[DependsJwtAuth])
async def refresh_token(
        request: Request,
        response: Response) -> ResponseModel:
    data = await auth_service.refresh_token(request=request)
    auth_service.set_token_cookies(
        response=response, 
        access_token=data.access_token, 
        refresh_token=data.refresh_token)
    return await response_base.success(data=data)

@router.post(
    '/logout', 
    summary='User Logout', 
    dependencies=[DependsJwtAuth])
async def user_logout(
        request: Request, 
        response: Response) -> ResponseModel:
    await auth_service.logout(request=request)
    auth_service.remove_token_cookies(response)
    return await response_base.success()
