#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import APIKeyCookie
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.model import User
from src.common.exception.errors import AuthorizationError, TokenError
from src.common.exception import errors
from src.config.settings import settings
from database.db_redis import redis_client
from src.utils.timezone import timezone

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


DependsJwtAuth = Depends(APIKeyCookie(name="access_token"))

async def create_access_token(sub: str, **kwargs) -> tuple[str, datetime]:
    """
    Generate encryption token

    :param sub: The subject/userid of the JWT
    :param expires_delta: Increased expiry time
    :return:
    """
    expire = timezone.now() + timedelta(seconds=settings.TOKEN_ACCESS_EXPIRE_SECONDS)
    multi_login = kwargs.pop('multi_login', None)
    to_encode = {'exp': expire, 'sub': sub, **kwargs}
    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    if multi_login is False:
        prefix = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:'
        await redis_client.delete_prefix(prefix)
    key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}'
    await redis_client.setex(key, settings.TOKEN_ACCESS_EXPIRE_SECONDS, token)
    return token, expire


async def create_refresh_token(sub: str, **kwargs) -> tuple[str, datetime]:
    """
    Generate encryption refresh token, only used to create a new token

    :param sub: The subject/userid of the JWT
    :param expire_time: expiry time
    :return:
    """
    expire = timezone.now() + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)
    multi_login = kwargs.pop('multi_login', None)
    to_encode = {'exp': expire, 'sub': sub, **kwargs}
    refresh_token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    if multi_login is False:
        prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:'
        await redis_client.delete_prefix(prefix)
    key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}'
    await redis_client.setex(key, settings.TOKEN_REFRESH_EXPIRE_SECONDS, refresh_token)
    return refresh_token, expire


async def create_new_token(sub: str, token: str, refresh_token: str, **kwargs) -> tuple[str, str, datetime, datetime]:
    """
    Generate new token

    :param sub:
    :param token
    :param refresh_token:
    :return:
    """
    redis_refresh_token = await redis_client.get(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}')
    if not redis_refresh_token or redis_refresh_token != refresh_token:
        raise errors.TokenError(msg='Refresh Token incorrect')
    new_access_token, new_access_token_expire_time = await create_access_token(sub, **kwargs)
    new_refresh_token, new_refresh_token_expire_time = await create_refresh_token(sub, **kwargs)
    token_key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}'
    refresh_token_key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{refresh_token}'
    await redis_client.delete(token_key)
    await redis_client.delete(refresh_token_key)
    return new_access_token, new_refresh_token, new_access_token_expire_time, new_refresh_token_expire_time

@sync_to_async
def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise errors.TokenError(msg='Refresh token not found')
    elif not token:
        raise errors.TokenError(msg='Access token not found')
    return token


@sync_to_async
def get_hash_password(password: str) -> str:
    """
    Encrypt passwords using the hash algorithm

    :param password:
    :return:
    """
    return pwd_context.hash(password)

@sync_to_async
def password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    Password verification

    :param plain_password: The password to verify
    :param hashed_password: The hash ciphers to compare
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)

@sync_to_async
def jwt_decode(token: str) -> str:
    """
    Decode token

    :param token: The JWT token to decode
    :return: The user ID from the token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_uuid = payload.get('sub')  # type: ignore
        if not user_uuid:
            raise errors.TokenError(msg='Invalid token')
    except ExpiredSignatureError:
        raise TokenError(msg='Token has expired')
    except (JWTError, Exception):
        raise TokenError(msg='Invalid token')
    return user_uuid


async def jwt_authentication(token: str) -> dict[str, str]:
    """
    JWT authentication

    :param token: The JWT token to authenticate
    :return: A dictionary containing the user ID
    """
    user_uuid = await jwt_decode(token)
    key = f'{settings.TOKEN_REDIS_PREFIX}:{user_uuid}:{token}'
    token_verify = await redis_client.get(key)
    if not token_verify:
        raise errors.TokenError(msg='Token has expired')
    return {'sub': user_uuid}

async def get_current_user(db: AsyncSession, data: dict) -> User|None:
    """
    Get the current user through token

    :param db: The database session
    :param data: The data from the token
    :return: The current user
    """
    user_uuid = data.get('sub')
    from src.app.core.crud.crud_user import user_dao

    user = await user_dao.get_with_relation(db, user_uuid=user_uuid)  # type: ignore
    if not user:
        return None
    if not user.status:
        raise errors.AuthorizationError(msg='User is locked')
    if user.roles:
        role_status = [role.status for role in user.roles]
        if all(status == 0 for status in role_status):
            raise errors.AuthorizationError(msg='User`s roles are locked')
    return user

@sync_to_async
def superuser_verify(request: Request) -> bool:
    """
    Verify the current user permissions through token

    :param request: The request object containing user information
    :return: True if the user is a superuser, otherwise raises an AuthorizationError
    """
    is_superuser = request.user.is_superuser
    if not is_superuser:
        raise errors.AuthorizationError(msg='Only administrators are authorized to perform this operation')
    if not request.user.is_staff:
        raise errors.AuthorizationError(msg='This administrator has been prohibited from performing backend management operations')
    return is_superuser


@sync_to_async
def staff_verify(request: Request) -> bool:
    """
    Verify the current user permissions through token

    :param request: The request object containing user information
    :return: True if the user is a superuser, otherwise raises an AuthorizationError
    """
    if not request.user.is_staff:
        raise errors.AuthorizationError(msg='This staff has been prohibited from performing backend management operations')
    return request.user.is_staff