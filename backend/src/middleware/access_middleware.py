#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.common.log import log
from src.utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = timezone.now()
        response = await call_next(request)
        end_time = timezone.now()
        log.info(f'{response.status_code} {request.client.host} {request.method} {request.url} {end_time - start_time}') # type: ignore
        return response
