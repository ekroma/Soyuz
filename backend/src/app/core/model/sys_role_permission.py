#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import INT, Column, ForeignKey, Integer, Table
from src.common.model import MappedBase

metadata = MappedBase.metadata

sys_role_permission = Table(
    'sys_role_permission',
    metadata,
    Column('id', INT, primary_key=True, unique=True, index=True, autoincrement=True, comment='ID'),
    Column('role_id', Integer, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True, comment='Role ID'),
    Column('permission_id', Integer, ForeignKey('sys_permission.id', ondelete='CASCADE'), primary_key=True, comment='Permission ID'),
    extend_existing=True
)
