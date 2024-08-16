#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import  Select

from src.app.organizations.crud.crud_counseling import counseling_dao
from src.app.organizations.model import Counseling
from src.common.enums import StatusType
from src.app.organizations.schema.counseling import (
    CreateCounselingSchema,
    UpdateCounselingSchema)
from src.common.exception import errors
from database.db_psql import async_db_session
from src.app.task.celery_task.tasks import task_sent_counseling_request_email_message

class CounselingService:
    @staticmethod
    async def create(*, obj: CreateCounselingSchema) -> None:
        async with async_db_session.begin() as db:
            await counseling_dao.create(db, obj)
            task_sent_counseling_request_email_message.delay(obj.model_dump())

    @staticmethod
    async def update_info(*, uuid: str, status:StatusType) -> int:
        async with async_db_session.begin() as db:
            counseling = await counseling_dao.get(db,uuid)
            if not counseling:
                raise errors.NotFoundError(msg='Counseling not found')
            return await counseling_dao.update(db,uuid,{'status':status})

    @staticmethod
    async def get_counseling_info(
            *,counseling_id:int|None=None,
            counseling_uuid:str|None=None) -> Counseling:
        async with async_db_session() as db:
            counseling = await counseling_dao.get_with_relation(
                db,
                counseling_id=counseling_id,
                counseling_uuid=counseling_uuid)
            if not counseling:
                raise errors.NotFoundError(msg='counseling does not exist')
            return counseling

    @staticmethod
    async def get_select(
            *, name: str|None = None, 
            status: StatusType|None = None,
            created_before:datetime|None,
            created_after:datetime|None) -> Select:
        return await counseling_dao.get_list(
            name=name,
            status=status,
            created_before=created_before,
            created_after=created_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            counseling = await counseling_dao.get(db, uuid)
            if not counseling:
                raise errors.NotFoundError(msg='Counseling does not exist')
            return await counseling_dao.delete(db, counseling.uuid)

    @staticmethod
    async def delete_many(*, status: StatusType) -> int:
        async with async_db_session.begin() as db:
            return await counseling_dao.delete_many_by_status(db, status)


counseling_service = CounselingService()