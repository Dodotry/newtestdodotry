#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-01-18 15:07:51
LastEditors: Dodotry
LastEditTime: 2026-01-18 16:46:42
'''
from contextlib import suppress

with suppress(ModuleNotFoundError):
    import pyi_splash,time
    pyi_splash.update_text("正在启动，请稍候...")
    time.sleep(5)
    pyi_splash.close()
