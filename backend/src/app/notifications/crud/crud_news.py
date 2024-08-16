#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import select, update, delete, desc, and_, Select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.timezone import timezone
from src.app.notifications.schema.news import CreateNewsSchema, UpdateNewsSchema
from src.common.crud import BaseCRUDPlus
from src.app.notifications.model import News

class CRUDNews(BaseCRUDPlus[News]):

    async def create(self, db: AsyncSession, obj: CreateNewsSchema) -> News:
        return await self.create_model(db,obj)

    async def get_by_title(self, db: AsyncSession, title: str) -> News| None:
        return await self.select_model_by_column(db, 'title', title)

    async def update_news_info(self, db: AsyncSession,uuid:str, obj: UpdateNewsSchema|dict) -> int:
        return await self.update_model(db, uuid, obj)

    async def delete(self, db: AsyncSession, uuid: str) -> int:
        return await self.delete_model(db, uuid)

    async def get_records_containing_any(
        self,
        db: AsyncSession, 
        title_list: list[str]):
        conditions = [getattr(self.model, 'title').ilike(f"%{item}%") for item in title_list]
        query = select(self.model).where(or_(*conditions))
        result = await db.execute(query)
        return result.scalars().all()

    async def get_list(
        self,
        title: str|None = None,
        url: str|None = None,
        link: str|None = None,
        created_after: datetime|None = None, 
        created_before: datetime|None = None, 
    ) -> Select:
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if title:
            where_list.append(self.model.title.like(f'%{title}%'))
        if url:
            where_list.append(self.model.url.like(f'%{url}%'))
        if link:
            where_list.append(self.model.link.like(f'%{link}%'))
        if created_after is not None:
            where_list.append(self.model.created_time >= timezone.f_datetime(created_after))
        if created_before is not None:
            where_list.append(self.model.created_time <= timezone.f_datetime(created_before))
        if where_list:
            se = se.where(and_(*where_list))
        return se
    
    async def delete_many_by(self, 
        db: AsyncSession, 
        url: str|None = None,
        created_after: datetime|None = None, 
        created_before: datetime|None = None, ) -> int:
        where_list = []
        if url:
            where_list.append(self.model.url.like(f'%{url}%'))
        if created_after is not None:
            where_list.append(self.model.created_time >= timezone.f_datetime(created_after))
        if created_before is not None:
            where_list.append(self.model.created_time <= timezone.f_datetime(created_before))
        if not where_list:
            return 0
        result = await db.execute(
            delete(self.model).where(and_(*where_list))
        )
        return result.rowcount

news_dao: CRUDNews = CRUDNews(News)