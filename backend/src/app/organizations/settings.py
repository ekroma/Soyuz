#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.path_conf import BasePath


class OrganizationsSettings(BaseSettings):
    """Core Settings"""

    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

@lru_cache
def get_core_settings() -> OrganizationsSettings:
    """获取 admin 配置"""
    return CoreSettings() # type: ignore


organizations_settings = get_core_settings()
