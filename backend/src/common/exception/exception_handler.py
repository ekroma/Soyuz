#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asgiref.sync import sync_to_async
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.errors import PydanticUserError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from src.common.exception.errors import BaseExceptionMixin
from src.common.log import log
from src.common.response.response_code import StandardResponseCode
from src.common.schema import (
    CUSTOM_USAGE_ERROR_MESSAGES,
    CUSTOM_VALIDATION_ERROR_MESSAGES,
)
from src.config.settings import settings
from src.utils.serializers import MsgSpecJSONResponse


@sync_to_async
def _get_exception_code(status_code: int):
    """
    Get the return status code. OpenAPI, Uvicorn... use status codes based on RFC definitions. Detailed codes can be found in the links below:

    `Python status code standards <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http
    /__init__.py#L7>`__

    `IANA status code registry <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__

    :param status_code:
    :return:
    """
    try:
        STATUS_PHRASES[status_code]
    except Exception:
        code = StandardResponseCode.HTTP_400
    else:
        code = status_code
    return code


async def _validation_exception_handler(request: Request, e: RequestValidationError | ValidationError):
    """
    Data validation exception handler

    :param e:
    :return:
    """
    print(9999999999999999999999999999999999999)
    errors = []
    for error in e.errors():
        custom_message = CUSTOM_VALIDATION_ERROR_MESSAGES.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            if not ctx:
                error['msg'] = custom_message
            else:
                error['msg'] = custom_message.format(**ctx)
                ctx_error = ctx.get('error')
                if ctx_error:
                    error['ctx']['error'] = (  # type: ignore
                        ctx_error.__str__().replace("'", '"') if isinstance(ctx_error, Exception) else None
                    )
        errors.append(error)
    error = errors[0]
    if error.get('type') == 'json_invalid':
        message = 'JSON parsing failed'
    else:
        error_input = error.get('input')
        field = str(error.get('loc')[-1])
        error_msg = error.get('msg')
        message = f'{error_msg} {field}, input: {error_input}' if settings.ENVIRONMENT == 'dev' else error_msg
    msg = f'Invalid request parameters: {message}'
    data = {'errors': errors} if settings.ENVIRONMENT == 'dev' else None
    content = {
        'code': StandardResponseCode.HTTP_422,
        'msg': msg,
        'data': data,
    }
    request.state.__request_validation_exception__ = content  # Used to get exception information in middleware
    return MsgSpecJSONResponse(status_code=422, content=content)

def register_exception(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Global HTTP exception handler

        :param request:
        :param exc:
        :return:
        """
        print("HTTPException handler called")  # Debug message
        content = {
            'code': exc.status_code,
            'msg': exc.detail,
            'data': None,
        }
        request.state.__request_http_exception__ = content  # Used to get exception information in middleware
        return MsgSpecJSONResponse(
            status_code=await _get_exception_code(exc.status_code),
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        FastAPI data validation exception handler

        :param request:
        :param exc:
        :return:
        """
        print("RequestValidationError handler called")  # Debug message
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """
        Pydantic data validation exception handler

        :param request:
        :param exc:
        :return:
        """
        print("ValidationError handler called")  # Debug message
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """
        Pydantic user error handler

        :param request:
        :param exc:
        :return:
        """
        print("PydanticUserError handler called")  # Debug message
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content={
                'code': StandardResponseCode.HTTP_500,
                'msg': CUSTOM_USAGE_ERROR_MESSAGES.get(exc.code),  # type: ignore
                'data': None,
            },
        )

    @app.exception_handler(AssertionError)
    async def assertion_error_handler(request: Request, exc: AssertionError):
        """
        Assertion error handler

        :param request:
        :param exc:
        :return:
        """
        print("AssertionError handler called")  # Debug message
        content = {
            'code': StandardResponseCode.HTTP_500,
            'msg': str(''.join(exc.args) if exc.args else exc.__doc__),
            'data': None,
        }
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content=content,
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        Global exception handler

        :param request:
        :param exc:
        :return:
        """
        print("General Exception handler called")  # Debug message
        if isinstance(exc, BaseExceptionMixin):
            return MsgSpecJSONResponse(
                status_code=await _get_exception_code(exc.code),
                content={
                    'code': exc.code,
                    'msg': str(exc.msg),
                    'data': exc.data if exc.data else None,
                },
                background=exc.background,
            )
        else:
            import traceback

            log.error(f'Unknown exception: {exc}')
            log.error(traceback.format_exc())
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(exc),
                'data': None,
            }
            return MsgSpecJSONResponse(status_code=StandardResponseCode.HTTP_500, content=content)
