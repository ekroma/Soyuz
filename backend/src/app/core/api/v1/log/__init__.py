#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .login_log import router as login_log
from .opera_log import router as opera_log

router = APIRouter(prefix='/logs')

router.include_router(login_log, prefix='/login', tags=['Login Log Management'])

router.include_router(opera_log, prefix='/opera', tags=['Operation Log Management'])
