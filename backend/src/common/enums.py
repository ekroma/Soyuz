#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from enum import IntEnum as SourceIntEnum
from typing import Type


class _EnumBase:
    @classmethod
    def get_member_keys(cls: Type[Enum]) -> list[str]: # type: ignore
        return [name for name in cls.__members__.keys()]

    @classmethod
    def get_member_values(cls: Type[Enum]) -> list: # type: ignore
        return [item.value for item in cls.__members__.values()]


class IntEnum(_EnumBase, SourceIntEnum):
    """Integer Enumeration"""

    pass


class StrEnum(_EnumBase, str, Enum):
    """String Enumeration"""

    pass


class PermissionScopes(StrEnum):
    """Permission Scopes"""

    user = 'user'
    role = 'role'
    permission = 'permission'
    log = 'log'
    card = 'card'
    tariff = 'tariff'
    server = 'server'
    establishment = 'establishment'
    task = 'task'
    counseling = 'counseling'

class CardType(StrEnum):
    """Card Type"""

    COMPATRIOT = 'compatriot'
    FOREIGNER = 'foreigner'

class PaymentType(StrEnum):
    """Payment Type"""

    TARIFF = 'tariff'

class MethodType(StrEnum):
    """Request Method"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


class LoginLogStatusType(IntEnum):
    """Login Log Status"""

    fail = 0
    success = 1


class BuildTreeType(StrEnum):
    """Tree Structure Type"""

    traversal = 'traversal'
    recursive = 'recursive'


class OperaLogCipherType(IntEnum):
    """Operation Log Encryption Type"""

    aes = 0
    md5 = 1
    itsdangerous = 2
    plan = 3


class StatusType(IntEnum):
    """Status Type"""

    disable = 0
    enable = 1
    pending = 2


class UserSocialType(StrEnum):
    """User Social Type"""

    github = 'GitHub'
