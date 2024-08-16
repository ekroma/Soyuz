#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi_versioning import VersionedFastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware

from src.app.router import route
from src.common.exception.exception_handler import register_exception
from src.config.settings import settings
from src.config.path_conf import STATIC_DIR
from database.db_psql import create_table
from database.db_redis import redis_client
from src.middleware.jwt_auth_middleware import JwtAuthMiddleware
from src.utils.health_check import ensure_unique_route_names
from src.utils.openapi import simplify_operation_ids
from src.utils.serializers import MsgSpecJSONResponse
from src.middleware.opera_log_middleware import OperaLogMiddleware

sentry_sdk.init(
    dsn="https://0d46ebf650b7775be8634eb6b06f1989@o4506364877144064.ingest.sentry.io/4506364884025344",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

@asynccontextmanager
async def register_init(app: FastAPI):
    await create_table()
    await redis_client.open()
    await FastAPILimiter.init(redis_client, prefix=settings.LIMITER_REDIS_PREFIX)

    yield

    await redis_client.close()
    await FastAPILimiter.close()


def register_app():
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    register_static_file(app)
    register_middleware(app)
    register_router(app)
    register_page(app)
    register_exception(app)

    return app



def register_static_file(app: FastAPI):
    if settings.STATIC_FILES:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists(STATIC_DIR):
            os.mkdir(STATIC_DIR)
        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def register_middleware(app: FastAPI):
    app.add_middleware(OperaLogMiddleware)
    app.add_middleware(
        AuthenticationMiddleware, backend=JwtAuthMiddleware(), on_error=JwtAuthMiddleware.auth_exception_handler # type: ignore
    )

    if settings.MIDDLEWARE_ACCESS:
        from src.middleware.access_middleware import AccessMiddleware # type: ignore

        app.add_middleware(AccessMiddleware) # type: ignore

    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )


def register_router(app: FastAPI):
    app.include_router(route)

    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_page(app: FastAPI):
    add_pagination(app)
