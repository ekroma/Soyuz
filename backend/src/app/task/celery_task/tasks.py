#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid
import asyncio

from src.app.task.celery import celery_app
from src.app.core.crud.crud_user import user_dao
from src.app.notifications.news_parser import parser
from database.db_psql import async_db_session
from src.config.path_conf import STATIC_DIR
from src.config.settings import settings
from jinja2 import Template
from src.utils.sent_mail import send_email


@celery_app.task(name='auto_delete_pending_user')
def task_delete_pending_users():
    async def delete_pending_users():
        async with async_db_session.begin() as db:
            count = await user_dao.delete_many_by_status(db)
            return f"{count} pending users deleted"
    
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(delete_pending_users())

@celery_app.task(name='auto_update_news')
def task_update_news():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser.run())


@celery_app.task(name='sent_email_message_to_activate_account')
def task_sent_code_email_message(email: str, code: str):
    subject = "Получен код верификации аккаунта"

    template_path = f'{STATIC_DIR}/templates/activate_code_email_template.html'
    with open(template_path, 'r', encoding='utf-8') as file:
        template = Template(file.read())
    
    html_content = template.render(code=code)
    
    asyncio.run(send_email(email, subject, html_content, html=True))


@celery_app.task(name='sent_email_message_request_counseling')
def task_sent_counseling_request_email_message(obj):
    subject = "Получен запрос на консультацию"

    template_path = f'{STATIC_DIR}/templates/counseling_email_template.html'
    with open(template_path, 'r', encoding='utf-8') as file:
        template = Template(file.read())
    
    html_content = template.render(
        name=obj['name'],
        client_email=obj['client_email'],
        phone=obj['phone'],
        description=obj['description'].replace('\n', '<br>')
    )
    
    asyncio.run(send_email(settings.COUNSELING_EMAIL, subject, html_content, html=True))