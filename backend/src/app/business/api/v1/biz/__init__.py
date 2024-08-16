#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .card_history import router as card_history_router
from .card import router as card_router
from .tariff import router as tariff_router
router = APIRouter(prefix='/biz')

router.include_router(card_router, prefix='/card', tags=['Card Management'])
router.include_router(card_history_router, prefix='/card_history', tags=['Card History Management'])
router.include_router(tariff_router, prefix='/tariff', tags=['Tariff Management'])