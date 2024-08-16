#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from typing import TYPE_CHECKING

from loguru import logger

from src.config import path_conf
from src.config.settings import settings

if TYPE_CHECKING:
    import loguru


class Logger:
    def __init__(self):
        self.log_path = path_conf.LOG_DIR

    def log(self) -> loguru.Logger:
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        log_stdout_file = os.path.join(self.log_path, settings.LOG_STDOUT_FILENAME)
        log_stderr_file = os.path.join(self.log_path, settings.LOG_STDERR_FILENAME)

        log_config = dict(rotation='10 MB', retention='15 days', compression='tar.gz', enqueue=True)
        logger.add(
            log_stdout_file, # type: ignore
            level='INFO',
            filter=lambda record: record['level'].name == 'INFO' or record['level'].no <= 25,
            **log_config, # type: ignore
            backtrace=False,
            diagnose=False,
        ) # type: ignore
        logger.add(
            log_stderr_file, # type: ignore
            level='ERROR',
            filter=lambda record: record['level'].name == 'ERROR' or record['level'].no >= 30,
            **log_config, # type: ignore
            backtrace=True,
            diagnose=True,
        ) # type: ignore

        return logger


log = Logger().log()
