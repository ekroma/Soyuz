#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request, Response
from starlette.background import BackgroundTask, BackgroundTasks
from datetime import timedelta, datetime, timezone as datetime_timezone

from src.app.core.settings import core_settings
from src.app.core.crud.crud_user import user_dao
from src.app.core.schema.token import GetLoginToken, GetNewToken
from src.app.core.schema.user import AuthLoginParam
from src.app.core.service.login_log_service import LoginLogService
from src.common.enums import LoginLogStatusType
from src.common.exception import errors
from src.common.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token_from_cookie,
    jwt_decode,
    password_verify,
)
from src.config.settings import settings
from database.db_psql import async_db_session
from database.db_redis import redis_client
from src.utils.timezone import timezone


class AuthService:

    @staticmethod
    async def login(*, request: Request, obj: AuthLoginParam, background_tasks: BackgroundTasks) -> GetLoginToken:
        async with async_db_session.begin() as db:
            try:
                current_user = await user_dao.get_with_relation(db, email=obj.email)
                if not current_user:
                    raise errors.NotFoundError(msg='User not found')
                elif not await password_verify(obj.password + current_user.salt, current_user.password):
                    raise errors.AuthorizationError(msg='Incorrect password')
                elif not current_user.status:
                    raise errors.AuthorizationError(msg='User is locked, login failed')
                access_token, access_token_expire_time = await create_access_token(
                    str(current_user.uuid), multi_login=current_user.is_multi_login
                )
                refresh_token, refresh_token_expire_time = await create_refresh_token(
                    str(current_user.uuid), multi_login=current_user.is_multi_login
                )
                await user_dao.update_login_time(db, obj.email)
                await db.refresh(current_user)
            except errors.NotFoundError as e:
                raise errors.HTTPError(msg=e.msg,code=404)
            except (errors.AuthorizationError, errors.CustomError) as e:
                err_log_info = dict(
                    db=db,
                    request=request,
                    user=current_user,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.fail.value,
                    msg=e.msg,
                )
                task = BackgroundTask(LoginLogService.create, **err_log_info) # type: ignore
                raise errors.AuthorizationError(msg=e.msg, background=task) # type: ignore
            except Exception as e:
                raise e
            else:
                login_log = dict(
                    db=db,
                    request=request,
                    user=current_user,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.success.value,
                    msg='Login successful',
                )
                background_tasks.add_task(LoginLogService.create, **login_log) # type: ignore
                data = GetLoginToken(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    access_token_expire_time=access_token_expire_time,
                    refresh_token_expire_time=refresh_token_expire_time,
                    user=current_user,  # type: ignore
                )
                return data

    @staticmethod
    async def refresh_token(*, request: Request) -> GetNewToken:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            refresh_token = request.headers.get('Referer')
            if not refresh_token:
                raise errors.TokenError()
        user_uuid = await jwt_decode(refresh_token)
        async with async_db_session() as db:
            current_user = await user_dao.get(db, user_uuid)
            if not current_user:
                raise errors.NotFoundError(msg='User not found')
            elif not current_user.status:
                raise errors.AuthorizationError(msg='User is locked, operation failed')
            current_token = await get_token_from_cookie(request)
            (
                new_access_token,
                new_refresh_token,
                new_access_token_expire_time,
                new_refresh_token_expire_time,
            ) = await create_new_token(
                str(current_user.uuid), current_token, refresh_token, multi_login=current_user.is_multi_login
            )
            data = GetNewToken(
                access_token=new_access_token,
                access_token_expire_time=new_access_token_expire_time,
                refresh_token=new_refresh_token,
                refresh_token_expire_time=new_refresh_token_expire_time,
            )
            return data

    @staticmethod
    async def logout(*, request: Request) -> None:
        token = await get_token_from_cookie(request)
        if request.user.is_multi_login:
            key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
            await redis_client.delete(key)
        else:
            prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(prefix)

    @staticmethod
    def set_token_cookies(response:Response, access_token, refresh_token:str):
        access_token_expires = timedelta(minutes=settings.TOKEN_ACCESS_EXPIRE_SECONDS)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="strict",#type:ignore
            expires=(datetime.now(datetime_timezone.utc) + access_token_expires) # type: ignore
        )
        refresh_token_expires = timedelta(days=settings.TOKEN_REFRESH_EXPIRE_SECONDS)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="strict",#type:ignore
            expires=(datetime.now(datetime_timezone.utc) + refresh_token_expires) # type: ignore
        )
        return response

    @staticmethod
    def remove_token_cookies(response):
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response



auth_service = AuthService()
