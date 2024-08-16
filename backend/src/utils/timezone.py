#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zoneinfo
from datetime import datetime
from src.config.settings import settings


class TimeZone:
    def __init__(self, tz: str = settings.DATETIME_TIMEZONE):
        self.tz_info = zoneinfo.ZoneInfo(tz)

    def now(self) -> datetime:
        """
        Get the current time in the specified timezone.

        :return: Current datetime in the specified timezone
        """
        return datetime.now(self.tz_info)

    def f_datetime(self, dt: datetime) -> datetime:
        """
        Convert a datetime object to the specified timezone.

        :param dt: Datetime object to be converted
        :return: Datetime object in the specified timezone
        """
        return dt.astimezone(self.tz_info)

    def f_str(self, date_str: str, format_str: str = settings.DATETIME_FORMAT) -> datetime:
        """
        Convert a date string to a datetime object in the specified timezone.

        :param date_str: Date string to be converted
        :param format_str: Format of the date string
        :return: Datetime object in the specified timezone
        """
        return datetime.strptime(date_str, format_str).replace(tzinfo=self.tz_info)


timezone = TimeZone()
