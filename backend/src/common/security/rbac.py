#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Depends, Request
import json
from src.common.enums import MethodType, StatusType
from src.common.exception import errors
from src.common.security.jwt import DependsJwtAuth
from src.config.settings import settings
from database.db_redis import redis_client


class RBAC:
    async def rbac_verify(self, request: Request, _token: str = DependsJwtAuth) -> None:
        """
        RBAC Permission Verification

        :param request:
        :param _token:
        :return:
        """
        if not request.user:
            raise errors.InvalidDataError(msg='Invalid Token')
        if not request.user.status:
            raise errors.ForbiddenError(msg='User is locked')
        path = request.url.path
        if path in settings.TOKEN_EXCLUDE:
            return
        if not request.auth.scopes:
            raise errors.TokenError
        if request.user.is_superuser:
            return
        user_roles = request.user.roles
        if not user_roles:
            raise errors.ForbiddenError(msg='User not assigned a role, authorization failed')
        user_uuid = request.user.uuid
        path_auth_perms:dict = request.state.permission
        user_perms_json = await redis_client.get(f'{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}')
        if not user_perms_json:
            user_perms = {}
            for role in user_roles:
                for perm in role.permissions:
                    if perm.status == StatusType.enable:
                        user_perms[perm.scope] = perm.perm
            user_perms_json = json.dumps(user_perms)
            await redis_client.set(
                f'{settings.PERMISSION_REDIS_PREFIX}:{user_uuid}', user_perms_json
            )
        user_perms:dict = json.loads(user_perms_json)
        for perm_scope,perm_value in path_auth_perms.items():
            if perm_value not in user_perms.get(perm_scope,''):
                raise errors.ForbiddenError(msg="Permission denied")


rbac = RBAC()
DependsRBAC = Depends(rbac.rbac_verify)
