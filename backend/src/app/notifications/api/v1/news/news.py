#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Query

from database.db_psql import CurrentSession
from src.common.pagination import DependsPagination, paging_data
from src.common.response.response_schema import response_base
from src.app.notifications.crud.crud_news import news_dao
from src.app.notifications.schema.news import ReadNewsSchema


router = APIRouter()

@router.get(
    '/all',
    summary='Get News with Pagination',
    dependencies=[
        DependsPagination])
async def get_pagination_news(
        db: CurrentSession,
        title: Annotated[str | None, Query()] = None,
        url: Annotated[str | None, Query()] = None,
        link: Annotated[str | None, Query()] = None,
        created_before: Annotated[datetime| None, Query()] = None,
        created_after: Annotated[datetime| None, Query()] = None,
):
    card_select = await news_dao.get_list(
        title=title,
        url=url,
        link=link,
        created_before=created_before,
        created_after=created_after,)
    page_data = await paging_data(db, card_select, ReadNewsSchema)
    return await response_base.success(data=page_data)