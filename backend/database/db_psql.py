#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from typing import Annotated


from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.common.log import log
from src.common.model import MappedBase
from src.config.settings import settings


def create_engine_and_session(url: str | URL):
    try:
        engine = create_async_engine(url, echo=settings.POSTGRES_ECHO, future=True, pool_pre_ping=True)
    except Exception as e:
        log.error('❌ Database connection error {}', e)
        sys.exit()
    else:
        db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        return engine, db_session


SQLALCHEMY_DATABASE_URL = (
    f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:'
    f'{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
)

async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


async def get_db() -> AsyncSession: # type: ignore
    """session 生成器"""
    session = async_db_session()
    try:
        yield session # type: ignore
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()


CurrentSession = Annotated[AsyncSession, Depends(get_db)]


async def create_table():
    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all) # type: ignore


