#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.path_conf import BasePath


class CoreSettings(BaseSettings):
    """Core Settings"""

    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    # OAuth2
    OAUTH2_GITHUB_REDIRECT_URI: str = 'http://127.0.0.1:8000/api/v1/auth/github/callback'

@lru_cache
def get_core_settings() -> CoreSettings:
    return CoreSettings() # type: ignore


core_settings = get_core_settings()
