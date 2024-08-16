from fastapi import Response
from .response_code import CustomResponseCode
from src.utils.serializers import MsgSpecJSONResponse


from asgiref.sync import sync_to_async
from fastapi import Response
from pydantic import BaseModel
from datetime import datetime
from typing import Any, TypeVar, Generic

from src.common.response.response_code import CustomResponse, CustomResponseCode
from src.config.settings import settings
from src.utils.serializers import MsgSpecJSONResponse

_ExcludeData = set[int | str] | dict[int | str, Any]

__all__ = ['ResponseModel', 'response_base']

T = TypeVar('T')

class ResponseModel(BaseModel,Generic[T]):
    code: int = CustomResponseCode.HTTP_200.code
    msg: str = CustomResponseCode.HTTP_200.msg
    data: T|None = None

    class Config:
        json_encoders = {
            datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)
        }

class ResponseBase():
    @staticmethod
    @sync_to_async
    def __response(*, res: CustomResponseCode | CustomResponse | None = None, data: Any | None = None) -> ResponseModel:
        return ResponseModel(code=res.code, msg=res.msg, data=data) # type: ignore

    async def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel:
        return await self.__response(res=res, data=data)

    async def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseModel:
        return await self.__response(res=res, data=data)

    @staticmethod
    @sync_to_async
    def fast_success(
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> Response:
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()


response_base = ResponseBase()