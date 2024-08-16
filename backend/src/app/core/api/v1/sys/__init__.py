#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from .user import router as user_router
from .role import router as role_router
from .permission import router as permission_router

router = APIRouter(prefix='/sys')

router.include_router(user_router, prefix='/users', tags=['User Management'])
router.include_router(role_router, prefix='/roles', tags=['Role Management'])
router.include_router(permission_router, prefix='/perm', tags=['Permission Management'])