#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-04-25 23:04:27
LastEditors: Dodotry
LastEditTime: 2026-04-25 23:26:51
'''
from PySide6.QtCore import QThread
from loguru import logger
import time
import random

class WorkerThread(QThread):
    def __init__(self):
        super().__init__()
        self.setObjectName("cleanthread" )
    def run(self):
        """在这里执行耗时操作，logger 是线程安全的"""
        i =0
        while 1:
            logger.info(f"第 {i+1} 次执行")
            logger.debug("这是一个调试日志")
            logger.success("这是一个成功日志")

            # 模拟耗时操作，不会阻塞 UI
            time.sleep(random.uniform(1, 6))

            logger.warning("这是一个警告日志")
            logger.error("这是一个错误日志")
            logger.critical("这是一个严重错误日志")
            i += 1
