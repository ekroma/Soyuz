#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from src.app.core.model.sys_role import RoleTranslateContent
from src.common.enums import StatusType
from src.common.schema import SchemaBase, TranslateSchema
from .permission import ReadPermissionSchema


class RoleSchemaBase(SchemaBase,TranslateSchema[RoleTranslateContent]):
    status:StatusType = StatusType.enable

class CreateRoleSchema(RoleSchemaBase):
    perm_uuids: list[str]

class UpdateRoleSchema(RoleSchemaBase):
    perm_uuids: list[str]

class ReadRoleSchema(RoleSchemaBase):
    uuid: str
    permissions: list[ReadPermissionSchema]

    class Config:
        from_attributes = True

class ListRoleSchema(RoleSchemaBase):
    uuid: str

    class Config:
        from_attributes = True