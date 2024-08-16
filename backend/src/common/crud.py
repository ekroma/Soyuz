#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, Literal, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import (
    Row, RowMapping, and_, asc, desc, or_, 
    select,update as sa_update,delete as sa_delete,
    func)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus.errors import ModelColumnError, SelectExpressionError

_Model = TypeVar('_Model')
_CreateSchema = TypeVar('_CreateSchema', bound=BaseModel)
_UpdateSchema = TypeVar('_UpdateSchema', bound=BaseModel)


class BaseCRUDPlus(Generic[_Model]):
    def __init__(self, model: Type[_Model]):
        self.model = model

    async def get(self, db: AsyncSession, uuid: str) -> _Model | None:
        return await self.select_model_by_uuid(db, uuid)

    async def create_model(self, session: AsyncSession, obj: _CreateSchema, **kwargs) -> _Model: # type: ignore
        if kwargs:
            instance = self.model(**obj.model_dump(), **kwargs)
        else:
            instance = self.model(**obj.model_dump())
        session.add(instance)
        await session.flush()
        await session.refresh(instance) 
        return instance

    async def select_model_by_id(self, session: AsyncSession, id: int) -> _Model | None:
        query = await session.execute(select(self.model).where(self.model.id == id)) # type: ignore
        return query.scalars().first()

    async def select_model_by_uuid(self, session: AsyncSession, uuid: str) -> _Model | None:
        query = await session.execute(select(self.model).where(self.model.uuid == uuid)) # type: ignore
        return query.scalars().first()

    async def select_model_by_column(self, session: AsyncSession, column: str, column_value: Any) -> _Model | None:
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
            query = await session.execute(select(self.model).where(model_column == column_value))  # type: ignore
            return query.scalars().first()
        else:
            raise ModelColumnError(f'Model column {column} is not found')

    async def select_model_by_columns(
        self, session: AsyncSession, expression: Literal['and', 'or'] = 'and', **conditions
    ) -> _Model | None:
        where_list = []
        for column, value in conditions.items():
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                where_list.append(model_column == value)
            else:
                raise ModelColumnError(f'Model column {column} is not found')
        match expression:
            case 'and':
                query = await session.execute(select(self.model).where(and_(*where_list)))
            case 'or':
                query = await session.execute(select(self.model).where(or_(*where_list)))
            case _:
                raise SelectExpressionError(f'select expression {expression} is not supported')
        return query.scalars().first()

    async def select_models(self, session: AsyncSession) -> Sequence[Row | RowMapping | Any] | None:
        query = await session.execute(select(self.model))
        return query.scalars().all()

    async def select_models_order(
        self,
        session: AsyncSession,
        *columns,
        model_sort: Literal['skip', 'asc', 'desc'] = 'skip',
    ) -> Sequence[Row | RowMapping | Any] | None:
        if model_sort != 'skip':
            if len(columns) != 1:
                raise SelectExpressionError('ASC and DESC only allow you to specify one column for sorting')
        sort_list = []
        for column in columns:
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                sort_list.append(model_column)
            else:
                raise ModelColumnError(f'Model column {column} is not found')
        match model_sort:
            case 'skip':
                query = await session.execute(select(self.model).order_by(*sort_list))
            case 'asc':
                query = await session.execute(select(self.model).order_by(asc(*sort_list)))
            case 'desc':
                query = await session.execute(select(self.model).order_by(desc(*sort_list)))
            case _:
                raise SelectExpressionError(f'select sort expression {model_sort} is not supported')
        return query.scalars().all()

    async def update_model(self, session: AsyncSession, uuid: str, obj: _UpdateSchema | dict[str, Any], **kwargs) -> int: # type: ignore
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        result = await session.execute(sa_update(self.model).where(self.model.uuid == uuid).values(**instance_data)) # type: ignore
        return result.rowcount  # type: ignore

    async def delete_model(self, session: AsyncSession, uuid: str, **kwargs) -> int:
        if not kwargs:
            result = await session.execute(sa_delete(self.model).where(self.model.uuid == uuid)) # type: ignore
        else:
            result = await session.execute(sa_update(self.model).where(self.model.uuid == uuid).values(**kwargs)) # type: ignore
        return result.rowcount  # type: ignore
