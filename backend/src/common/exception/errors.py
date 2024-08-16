#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# noqa: E501

from typing import Any

from fastapi import HTTPException, status
from starlette.background import BackgroundTask
from src.common.response.response_code import CustomErrorCode


class BaseExceptionMixin(Exception):
    code: int

    def __init__(self, *, msg: str|None = None, data: Any = None, background: BackgroundTask | None = None):
        self.msg = msg
        self.data = data
        # The original background task: https://www.starlette.io/background/
        self.background = background


class HTTPError(HTTPException):
    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionMixin):
    def __init__(self, *, error: CustomErrorCode, data: Any = None, background: BackgroundTask | None = None):
        self.code = error.code
        super().__init__(msg=error.msg, data=data, background=background)


class RequestError(BaseExceptionMixin):
    code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *, msg: str = 'Bad Request', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(BaseExceptionMixin):
    code = status.HTTP_403_FORBIDDEN

    def __init__(self, *, msg: str = 'Forbidden', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)

class ConflictError(BaseExceptionMixin):
    code = status.HTTP_409_CONFLICT

    def __init__(self, *, msg: str = 'Conflict', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)

class NotFoundError(BaseExceptionMixin):
    code = status.HTTP_404_NOT_FOUND

    def __init__(self, *, msg: str|None = 'Not Found', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)

class InvalidDataError(BaseExceptionMixin):
    code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, *, msg: str|None = 'Invalid data provided', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)

class ServerError(BaseExceptionMixin):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self, *, msg: str = 'Internal Server Error', data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(BaseExceptionMixin):
    code = status.HTTP_502_BAD_GATEWAY

    def __init__(self, *, msg: str = 'Bad Gateway', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class AuthorizationError(BaseExceptionMixin):
    code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, msg: str = 'Permission Denied', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, msg: str = 'Not Authenticated', headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})
