#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import select, update, delete, desc, and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload,noload

from src.common.crud import BaseCRUDPlus
from src.app.core.model import User, Role
from src.app.business.model import Card
from src.app.core.schema.user import (
    AddUserParam,
    AvatarParam,
    RegisterUserParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from src.utils.tools import get_random_string
from src.common.security.jwt import get_hash_password
from src.common.enums import StatusType
from src.utils.timezone import timezone

class CRUDUser(BaseCRUDPlus[User]):

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        return await self.select_model_by_column(db, 'email', email)

    async def update_login_time(self, db: AsyncSession, uuid: str) -> int:
        return await self.update_model(db, uuid, {"last_login_time":timezone.now()})

    async def pre_create(self, db: AsyncSession, data:dict) -> None:
        new_user = self.model(**data) # type: ignore
        db.add(new_user)

    async def create(self, db: AsyncSession, user: User, obj: RegisterUserParam) -> None:
        salt = get_random_string(5)
        obj.password = await get_hash_password(f'{obj.password}{salt}')
        dict_obj = obj.model_dump()
        dict_obj.update({'status': StatusType.enable})
        dict_obj.update({'salt': salt})
        await db.execute(
            update(self.model)
            .where(self.model.uuid == user.uuid)
            .values(dict_obj)
        )

    async def add(self, db: AsyncSession, obj: AddUserParam, roles:list[Role]) -> None:
        salt = get_random_string(5)
        obj.password = await get_hash_password(f'{obj.password}{salt}')
        dict_obj = obj.model_dump(exclude={'roles'})
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)
        new_user.roles.extend(roles)
        db.add(new_user)
        await db.flush()
        new_user.establishment_uuid = obj.establishment_uuid
        await db.flush()
        await db.refresh(new_user)

    async def update_userinfo(self, db: AsyncSession, input_user: User, obj: UpdateUserParam|dict) -> int:
        return await self.update_model(db, input_user.uuid, obj)

    async def delete(self, db: AsyncSession, user_uuid: str) -> int:
        return await self.delete_model(db, user_uuid)

    async def reset_password(self, db: AsyncSession, uuid: str, password: str, salt: str) -> int:
        new_pwd = await get_hash_password(f'{password}{salt}')
        return await self.update_model(db, uuid, {'password': new_pwd})

    async def get_super(self, db: AsyncSession, user_uuid: str) -> bool:
        user = await self.get(db, user_uuid)
        return user.is_superuser # type: ignore

    async def get_staff(self, db: AsyncSession, user_uuid: str) -> bool:
        user = await self.get(db, user_uuid)
        return user.is_staff # type: ignore

    async def get_status(self, db: AsyncSession, user_uuid: str) -> bool:
        user = await self.get(db, user_uuid)
        return user.status # type: ignore

    async def get_multi_login(self, db: AsyncSession, user_uuid: str) -> bool:
        user = await self.get(db, user_uuid)
        return user.is_multi_login # type: ignore

    async def set_super(self, db: AsyncSession, user_uuid: str) -> int:
        super_status = await self.get_super(db, user_uuid)
        return await self.update_model(db, user_uuid, {'is_superuser': False if super_status else True})

    async def set_staff(self, db: AsyncSession, user_uuid: str) -> int:
        staff_status = await self.get_staff(db, user_uuid)
        return await self.update_model(db, user_uuid, {'is_staff': False if staff_status else True})

    async def set_status(self, db: AsyncSession, user_uuid: str) -> int:
        status = await self.get_status(db, user_uuid)
        return await self.update_model(db, user_uuid, {'status': False if status else True})

    async def set_multi_login(self, db: AsyncSession, user_uuid: str) -> int:
        multi_login = await self.get_multi_login(db, user_uuid)
        return await self.update_model(db, user_uuid, {'is_multi_login': False if multi_login else True})

    async def get_list(
        self,
        email: str|None = None,
        phone: str|None = None,
        status: StatusType|None = None,
    ) -> Select:
        se = (
            select(self.model)
            .order_by(desc(self.model.created_time))
        )
        where_list = []
        if email:
            where_list.append(self.model.email.like(f'%{email}%'))
        if phone:
            where_list.append(self.model.phone.like(f'%{phone}%'))
        if status is not None:
            where_list.append(self.model.status == status)
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def get_with_relation(self, db: AsyncSession, *, user_uuid: str | None = None, email: str | None = None) -> User | None:
        where = []
        if user_uuid:
            where.append(self.model.uuid == user_uuid)
        if email:
            where.append(self.model.email == email)
        
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(self.model.roles).selectinload(Role.permissions),
                selectinload(self.model.card).selectinload(Card.tariff),
                selectinload(self.model.establishment)
            )
            .where(*where)
        )
        current_user = result.scalars().first()
        return current_user
    
    async def delete_many_by_status(self, db: AsyncSession, status: StatusType = StatusType.pending) -> int:
        result = await db.execute(
            delete(self.model).where(self.model.status == status)
        )
        return result.rowcount

user_dao: CRUDUser = CRUDUser(User)