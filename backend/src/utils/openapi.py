#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.routing import APIRoute


def simplify_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs for routes in the FastAPI application to make
    the generated client have simpler API function names.

    :param app: FastAPI application instance
    :return: None
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name
