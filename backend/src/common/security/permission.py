#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request

class RequestPermission:

    def __init__(self, value: dict):
        self.value = value

    async def __call__(self, request: Request):
        request.state.permission = self.value