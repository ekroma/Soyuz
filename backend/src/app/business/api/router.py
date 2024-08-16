#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from src.config.settings import settings

from .v1.biz import router as biz_router 
v1 = APIRouter(prefix=settings.API_V1_STR)

v1.include_router(biz_router)