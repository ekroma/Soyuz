#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from src.config.settings import settings

from .v1.auth import router as auth_router
from .v1.log import router as log_router
from .v1.monitor import router as monitor_router
from .v1.sys import router as sys_router 

v1 = APIRouter(prefix=settings.API_V1_STR)

v1.include_router(auth_router)
v1.include_router(sys_router)
v1.include_router(log_router)
v1.include_router(monitor_router)
