#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from src.app.core.api.v1.monitor.redis import router as redis_router
from src.app.core.api.v1.monitor.server import router as server_router

router = APIRouter(prefix='/monitors', tags=['Monitoring Management'])

router.include_router(redis_router, prefix='/redis')

router.include_router(server_router, prefix='/server')
