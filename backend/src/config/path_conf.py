#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from pathlib import Path

BasePath = Path(__file__).resolve().parent.parent.parent

ALEMBIC_Versions_DIR = os.path.join(BasePath, 'alembic', 'versions')

LOG_DIR = os.path.join(BasePath, 'log')

IP2REGION_XDB = os.path.join(BasePath, 'static', 'ip2region.xdb')

STATIC_DIR = os.path.join(BasePath, 'static')
