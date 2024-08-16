#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .core.api.router import v1 as core_router
from .business.api.router import v1 as biz_router
from .organizations.api.router import v1 as org_router
from .notifications.api.router import v1 as news_router

route = APIRouter()

route.include_router(core_router)
route.include_router(biz_router)
route.include_router(org_router)
route.include_router(news_router)