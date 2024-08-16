#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from fastapi import Request
from sqlalchemy import Select

from src.app.core.crud.crud_user import user_dao
from src.app.core.crud.crud_role import role_dao
from src.app.organizations.crud.crud_establishment import establishment_dao
from src.app.core.model import User
from src.app.core.schema.user import (
    AddUserParam,
    AvatarParam,
    RegisterUserParam,
    ResetPasswordParam,
    UpdateUserParam,
    RestorePasswordParam
)
from src.common.enums import StatusType
from src.common.exception import errors
from src.common.security.jwt import get_token_from_cookie, password_verify, superuser_verify
from src.config.settings import settings
from database.db_psql import async_db_session
from database.db_redis import redis_client
from src.utils.tools import get_random_num
from src.app.task.celery_task.tasks import task_sent_code_email_message

class UserService:

    @staticmethod
    async def pre_register(*, email:str) -> None:
        async with async_db_session.begin() as db:
            user = await user_dao.get_by_email(db, email)
            code = get_random_num(6)
            if user:
                if user.status != StatusType.pending:
                    raise errors.ConflictError(msg='Email already used')
                await user_dao.update_userinfo(db,user,{'code':code})
                task_sent_code_email_message.delay(email, code)
                return
            await user_dao.pre_create(db, {
                'email':email,
                'status':StatusType.pending,
                'code':code})
            task_sent_code_email_message.delay(email, code)

    @staticmethod
    async def register(*,code:str, obj: RegisterUserParam) -> None:
        async with async_db_session.begin() as db:
            if not obj.password:
                raise errors.RequestError(msg='Password is empty')
            user = await user_dao.get_by_email(db, obj.email)
            if not user:
                raise errors.NotFoundError(msg='User not registered')
            if user.status != StatusType.pending:
                raise errors.ConflictError(msg='User already activated')
            if user.code != code:
                raise errors.RequestError(msg='Code doesn`t match')
            await user_dao.create(db,user, obj)

    @staticmethod
    async def add(*, request: Request, obj: AddUserParam) -> None:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            email = await user_dao.get_by_email(db, obj.email)
            if email:
                raise errors.ConflictError(msg='User already exist')
            if obj.establishment_uuid:
                establishment = await establishment_dao.get(db, obj.establishment_uuid)
                if not establishment:
                    raise errors.NotFoundError(msg='Establishment not found')
            roles = []
            for role_uuid in obj.roles:
                role = await role_dao.get(db, role_uuid)
                if not role:
                    raise errors.NotFoundError(msg='Role does not exist')
                roles.append(role)
            await user_dao.add(db, obj, roles)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: ResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            if not await password_verify(f'{obj.old_password}{request.user.salt}', request.user.password):
                raise errors.RequestError(msg='Old password is incorrect')
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg='The two passwords do not match')
            count = await user_dao.reset_password(db, request.user.id, obj.new_password, request.user.salt)
            prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:',
            ]
            for i in prefix:
                await redis_client.delete_prefix(i)
            return count

    @staticmethod
    async def pre_pwd_restore(*, email:str) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get_by_email(db, email)
            code = get_random_num(6)
            if not user:
                raise errors.NotFoundError(msg='User not registered')
            count = await user_dao.update_userinfo(db,user,{
                'code':code})
            task_sent_code_email_message.delay(email, code)
            return count

    @staticmethod
    async def pwd_restore(*, request: Request, obj: RestorePasswordParam) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get_by_email(db,obj.email)
            if not user:
                raise errors.NotFoundError(msg='User not registered')
            if user.code != obj.code:
                raise errors.RequestError(msg='Code is incorrect')
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg='The two passwords do not match')
            count = await user_dao.reset_password(db, request.user.id, obj.new_password, request.user.salt)
            prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:',
            ]
            for i in prefix:
                await redis_client.delete_prefix(i)
            return count

    @staticmethod
    async def get_user_info(*, email: str) -> User:
        async with async_db_session() as db:
            user = await user_dao.get_with_relation(db, email=email)
            if not user:
                raise errors.NotFoundError(msg='User does not exist')
            return user

    @staticmethod
    async def update(*, request: Request, email: str, obj: UpdateUserParam) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_with_relation(db, email=email)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            return await user_dao.update_userinfo(db, input_user, obj)
    
    @staticmethod
    async def update_role(*, request: Request, email: str, role_uuids: list[str]) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_with_relation(db, email=email)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            role_list = []
            for role_uuid in role_uuids:
                role_list.append(await role_dao.get(db,role_uuid))
            input_user.roles = role_list
            return 1

    @staticmethod
    async def get_select(*, email: str|None = None, phone: str|None = None, status: StatusType|None = None) -> Select:
        return await user_dao.get_list(email=email, phone=phone, status=status)

    @staticmethod
    async def update_permission(*, request: Request, pk: str) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            if pk == request.user.uuid:
                raise errors.ForbiddenError(msg='Modifying your own administrator permissions is prohibited')
            return await user_dao.set_super(db, pk)

    @staticmethod
    async def update_establishment(*, request: Request, pk: str, establishment_uuid:str) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='Modifying your own backend management login permissions is prohibited')
            user = await user_dao.get(db, pk)
            if not user:
                raise errors.NotFoundError(msg='User does not exist')
            if not await establishment_dao.get(db,uuid=establishment_uuid):
                raise errors.NotFoundError(msg='Establishment does not exist')
            return await user_dao.update_userinfo(db,user,{'establishment_uuid':establishment_uuid})

    @staticmethod
    async def update_staff(*, request: Request, pk: str) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='Modifying your own backend management login permissions is prohibited')
            return await user_dao.set_staff(db, pk)

    @staticmethod
    async def update_status(*, request: Request, pk: str) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            if pk == request.user.id:
                raise errors.ForbiddenError(msg='Modifying your own status is prohibited')
            return await user_dao.set_status(db, pk)

    @staticmethod
    async def update_multi_login(*, request: Request, pk: str) -> int:
        async with async_db_session.begin() as db:
            await superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            count = await user_dao.set_multi_login(db, pk)
            token = await get_token_from_cookie(request)
            user_uuid = request.user.uuid
            latest_multi_login = await user_dao.get_multi_login(db, pk)
            if pk == user_uuid:
                if not latest_multi_login:
                    prefix = f'{settings.TOKEN_REDIS_PREFIX}:{pk}:'
                    await redis_client.delete_prefix(prefix, exclude=prefix + token)
            else:
                if not latest_multi_login:
                    prefix = f'{settings.TOKEN_REDIS_PREFIX}:{pk}:'
                    await redis_client.delete_prefix(prefix)
            return count

    @staticmethod
    async def delete(*, email: str) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_email(db, email)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            count = await user_dao.delete(db, input_user.uuid)
            prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{input_user.id}:',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{input_user.id}:',
            ]
            for i in prefix:
                await redis_client.delete_prefix(i)
            return count


user_service = UserService()