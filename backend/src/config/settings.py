#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .path_conf import BasePath


class Settings(BaseSettings):
    """Global Settings"""

    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    ENVIRONMENT: Literal['dev', 'pro']

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_ECHO: bool = False
    POSTGRES_DB: str = 'temp_test'
    POSTGRES_CHARSET: str = 'utf8mb4'

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    SECRET_KEY: str

    OPERA_LOG_ENCRYPT_SECRET_KEY: str

    TITLE: str = 'FastAPI'
    VERSION: str = '0.0.1'
    DESCRIPTION: str = 'Soyuzkg Api'
    API_V1_STR: str = '/api/v1'
    DOCS_URL: str | None = f'{API_V1_STR}/docs'
    REDOCS_URL: str | None = f'{API_V1_STR}/redoc'
    OPENAPI_URL: str | None = f'{API_V1_STR}/openapi'

    ALLOW_HOSTS: list[str] = [
        "localhost",
        "0.0.0.0",
        ]
    ALLOW_METHODS: list[str] = [
        "GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"]
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:3000"]
    ALLOW_CREDENTIALS: bool = True 
    ALLOW_HEADERS: list[str] = [
        "Content-Type", 'Set-Cookie',"Access-Control-Allow-Headers", 
        "Access-Control-Allow-Origin","Authorization"]

    @model_validator(mode='before') # type: ignore
    @classmethod
    def validate_openapi_url(cls, values):
        if values['ENVIRONMENT'] == 'pro':
            values['OPENAPI_URL'] = None
        return values

    STATIC_FILES: bool = False

    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    COUNSELING_EMAIL:str

    BASE_URL: str = "http://localhost:8000"
    MEDIA_ROOT: str
    MEDIA_DIR: str = "media"

    LOCATION_PARSE: Literal['online', 'offline', 'false'] = 'offline'

    LIMITER_REDIS_PREFIX: str = 'skg_limiter'

    DATETIME_TIMEZONE: str = 'Asia/Bishkek'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'


    REDIS_TIMEOUT: int = 5

    ALGORITHM: str = 'HS256'
    TOKEN_ACCESS_EXPIRE_SECONDS: int = 60 * 5
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7
    TOKEN_REDIS_PREFIX: str = 'token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'refresh_token'
    TOKEN_EXCLUDE: list[str] = [
        f'{API_V1_STR}/auth/login',
        f'{API_V1_STR}/auth/refresh-token',
        f'{API_V1_STR}/ntf/news/all',
        DOCS_URL,
        REDOCS_URL,
        OPENAPI_URL,
        f'{API_V1_STR}/org/counseling',
        f'{API_V1_STR}/sys/users/pre-register',
        f'{API_V1_STR}/sys/users/register',
    ]
    COOKIE_TOKEN_NAME:str = 'access_token'

    LOG_STDOUT_FILENAME: str = 'access.log'
    LOG_STDERR_FILENAME: str = 'error.log'

    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = False

    PERMISSION_MODE: Literal['casbin', 'role-menu'] = 'casbin'
    PERMISSION_REDIS_PREFIX: str = 'permission'

    CASBIN_EXCLUDE: set[tuple[str, str]] = {
        ('POST', f'auth/logout'),
        ('POST', f'auth/token/new'),
    }

    OPERA_LOG_EXCLUDE: list[str] = [
        '/favicon.ico',
        DOCS_URL,
        REDOCS_URL,
        OPENAPI_URL,
        f'auth/login/swagger',
        f'auth/github/callback',
    ]
    OPERA_LOG_ENCRYPT: int = 1
    OPERA_LOG_ENCRYPT_INCLUDE: list[str] = [
        'password',
        'old_password',
        'new_password',
        'confirm_password',
    ]

    IP_LOCATION_REDIS_PREFIX: str = 'ip_location'
    IP_LOCATION_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1


@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore


settings = get_settings()