#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from src.app.core.service.login_log_service import login_log_service
from src.app.core.service.opera_log_service import opera_log_service
from src.app.task.celery import celery_app
from src.app.task.settings import task_settings


@celery_app.task(
    name='auto_delete_db_opera_log',
    bind=True,
    retry_backoff=True,
    max_retries=task_settings.CELERY_TASK_MAX_RETRIES,
)
def auto_delete_db_opera_log(self) -> int:
    async def delete_db_opera_log():
        try:
            result = await opera_log_service.delete_all()
        except SQLAlchemyError as exc:
            raise self.retry(exc=exc)
        return result
    return asyncio.run(delete_db_opera_log())


@celery_app.task(
    name='auto_delete_db_login_log',
    bind=True,
    retry_backoff=True,
    max_retries=task_settings.CELERY_TASK_MAX_RETRIES,
)
def auto_delete_db_login_log(self) -> int:
    async def delete_db_login_log():
        try:
            result = await login_log_service.delete_all()
        except SQLAlchemyError as exc:
            raise self.retry(exc=exc)
        return result
    return asyncio.run(delete_db_login_log())
