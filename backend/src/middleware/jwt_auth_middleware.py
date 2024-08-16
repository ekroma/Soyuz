#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Request, Response
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError
from starlette.requests import HTTPConnection

from src.common.exception.errors import TokenError
from src.utils.serializers import MsgSpecJSONResponse
from src.common.log import log
from src.common.security import jwt
from src.config.settings import settings
from database.db_psql import async_db_session

class _AuthenticationError(AuthenticationError):

    def __init__(self, *, code: int, msg: str|None = None, headers: dict[str, Any] | None = None):
        self.code = code
        self.msg = msg
        self.headers = headers


class JwtAuthMiddleware(AuthenticationBackend):

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: _AuthenticationError) -> Response:
        try:
            status_code = int(exc.code)
        except (ValueError, TypeError):
            log.error(f"Invalid status code: {exc.code}")
            status_code = 500

        return MsgSpecJSONResponse(content={'code': status_code, 'msg': exc.msg, 'data': None}, status_code=status_code)
    
    async def authenticate(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            token = request.headers.get('Authorization')
            if not token:
                return
            scheme, token = token.split()
            if scheme.lower() != 'bearer':
                return
        if request.url.path in settings.TOKEN_EXCLUDE:
            return
        try:
            sub = await jwt.jwt_authentication(token)
            async with async_db_session() as db:
                user = await jwt.get_current_user(db, data=sub)
        except TokenError as exc:
            raise _AuthenticationError(code=exc.code, msg=exc.detail, headers=exc.headers)
        except Exception as e:
            log.exception(e)
            raise _AuthenticationError(code=getattr(e, 'code', 500), msg=getattr(e, 'msg', 'Internal Server Error'))
        return AuthCredentials(['authenticated']), user