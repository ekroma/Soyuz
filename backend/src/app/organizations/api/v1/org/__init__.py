#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .establishment import router as establishment_router
from .counseling import router as counseling_router
router = APIRouter(prefix='/org')

router.include_router(establishment_router, prefix='/establishment', tags=['Establishment Management'])
router.include_router(counseling_router, prefix='/counseling', tags=['Counseling Management'])