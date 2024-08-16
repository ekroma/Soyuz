#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import validator
import re
from src.app.core.model.sys_permission import PermissionTranslateContent
from src.common.enums import StatusType, PermissionScopes
from src.common.schema import SchemaBase, TranslateSchema


class PermissionSchemaBase(SchemaBase, TranslateSchema[PermissionTranslateContent]):
    status:StatusType = StatusType.enable
    scope: PermissionScopes
    perm: str

    @validator('perm')
    def validate_perm(cls, v):
        pattern = re.compile(r'^[crud]*$')
        if not pattern.match(v):
            raise ValueError('Invalid permission string. Only characters c, r, u, d are allowed.')
        return v

class CreatePermissionSchema(PermissionSchemaBase):
    pass

class UpdatePermissionSchema(PermissionSchemaBase):
    pass

class ReadPermissionSchema(PermissionSchemaBase):
    uuid: str

    class Config:
        from_attributes = True

class ListPermissionSchema(PermissionSchemaBase):
    uuid:str
    
    class Config:
        from_attributes = True