#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .news import router as news_router
router = APIRouter(prefix='/ntf')

router.include_router(news_router, prefix='/news', tags=['News'])


