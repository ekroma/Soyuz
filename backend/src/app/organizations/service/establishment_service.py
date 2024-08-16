#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import UploadFile
from datetime import datetime

from sqlalchemy import  Select

from src.common.filebase import FileBase
from src.app.organizations.crud.crud_establishment import establishment_dao
from src.app.organizations.model import Establishment
from src.common.enums import StatusType
from src.app.organizations.schema.establishment import (
    CreateEstablishmentSchema,
    UpdateEstablishmentSchema)
from src.common.exception import errors
from database.db_psql import async_db_session

class EstablishmentService:
    @staticmethod
    async def create(*, obj: CreateEstablishmentSchema) -> None:
        async with async_db_session.begin() as db:
            await establishment_dao.create(db, obj)

    @staticmethod
    async def update_info(*, uuid: str, obj: UpdateEstablishmentSchema) -> int:
        async with async_db_session.begin() as db:
            establishment = await establishment_dao.get(db,uuid)
            if not establishment:
                raise errors.NotFoundError(msg='Establishment not found')
            return await establishment_dao.update(db,uuid,obj)

    @staticmethod
    async def add_images(*, uuid: str, images: list[UploadFile]) -> int:
        async with async_db_session.begin() as db:
            establishment = await establishment_dao.get(db,uuid)
            if not establishment:
                raise errors.NotFoundError(msg='Establishment not found')
            images_path = []
            for image in images:
                images_path.append(await FileBase.save_upload_file(
                    image, 
                    destination_path="org/establishment/images"))
            images_path.extend(images_path)
            establishment.images = images_path
            return 1

    @staticmethod
    async def delete_images(*, uuid: str, images_path: list[str]) -> int:
        async with async_db_session.begin() as db:
            establishment = await establishment_dao.get(db,uuid)
            if not establishment:
                raise errors.NotFoundError(msg='Establishment not found')
            images_path = establishment.images
            for image_path in images_path:
                await FileBase.delete_file(image_path)
                images_path.remove(image_path)
            establishment.images = images_path
            return 1

    @staticmethod
    async def get_establishment_info(
            *,establishment_id:int|None=None,
            establishment_uuid:str|None=None,
            name:str|None=None) -> Establishment:
        async with async_db_session() as db:
            establishment = await establishment_dao.get_with_relation(
                db,
                establishment_id=establishment_id,
                establishment_uuid=establishment_uuid,
                name=name)
            if not establishment:
                raise errors.NotFoundError(msg='Establishment does not exist')
            return establishment

    @staticmethod
    async def get_select(
            *, name: str|None = None, 
            status: StatusType|None = None,
            created_before:datetime|None,
            created_after:datetime|None) -> Select:
        return await establishment_dao.get_list(
            name=name,
            status=status,
            created_before=created_before,
            created_after=created_after)

    @staticmethod
    async def delete(*, uuid: str) -> int:
        async with async_db_session.begin() as db:
            card = await establishment_dao.get(db, uuid)
            if not card:
                raise errors.NotFoundError(msg='Card does not exist')
            return await establishment_dao.delete(db, card.uuid)


establishment_service = EstablishmentService()