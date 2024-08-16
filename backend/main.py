#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

import uvicorn

from src.config.registrar import register_app

app = register_app()


if __name__ == '__main__':
    try:
        uvicorn.run(app=f'{Path(__file__).stem}:app', port=8000,reload=True)
    except Exception as e:
        raise e
