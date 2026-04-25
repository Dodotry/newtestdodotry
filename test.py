#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-04-25 14:22:10
LastEditors: Dodotry
LastEditTime: 2026-04-25 23:37:32
'''
from loguru import logger
import time
import random
logger.remove()
from pathlib import PureWindowsPath
from PySide6.QtCore import Slot, QObject, Signal, QThread
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QLineEdit,
)
from ui.Ui_gui import Ui_mainwind


class LogSignals(QObject):
    log_received = Signal(str)

class QTextEditSink:
    def __init__(self, signals: LogSignals):
        self.signals = signals
        # 定义不同级别的颜色
        self.level_colors = {
            "DEBUG": "#7f8c8d",  # 灰色
            "INFO": "#000000",  # 黑色
            "SUCCESS": "#27ae60",  # 绿色
            "WARNING": "#f39c12",  # 橙色
            "ERROR": "#e74c3c",  # 红色
            "CRITICAL": "#8e44ad",  # 紫色
        }

    def write(self, message):
        # 1. 获取日志记录对象
        record = message.record
        level = record["level"].name
        color = self.level_colors.get(level, "#000000")

        # 2. 格式化为你想要的文本内容（例如：时间 | 级别 | 消息）
        time_str = record["time"].strftime("%H:%M:%S")
        msg_content = record["message"]

        # 3. 拼装成 HTML 字符串
        html_text = (
            f'<span style="color:{color};">{time_str} | {level} | {msg_content}</span>'
        )

        # 4. 发送信号
        self.signals.log_received.emit(html_text)


class Window(QWidget, Ui_mainwind):
    """主界面"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_log()

    @Slot()
    def on_srcbtn_clicked(self):
        self.select_dir(self.src_dir)

    @Slot()
    def on_dstbtn_clicked(self):
        self.select_dir(self.output_dir)

    def select_dir(self, entry: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if path:
            win_path = str(PureWindowsPath(path))
            logger.info(f"用户选择了文件夹: {win_path}")
            entry.setText(win_path)
        else:
            logger.info("用户取消了选择文件夹")

    @Slot()
    def on_startbtn_clicked(self):
        from src.appfun import WorkerThread
        self.worker = WorkerThread()
        # 启动线程
        self.worker.start()
        # 禁用按钮防止重复点击
        self.startbtn.setEnabled(False)
        self.startbtn.setText("执行中...")
        self.worker.finished.connect(self.reset_btn)

    def reset_btn(self):
        self.startbtn.setText("开始")
        self.startbtn.setEnabled(True)

    def init_log(self):
        self.signals = LogSignals()
        self.sink = QTextEditSink(self.signals)
        self.signals.log_received.connect(self.append_log)
        logger.add(
            self.sink, format="{time:HH:mm:ss} | {level} | {message}", colorize=True,enqueue=True
        )
        self.logpannel.document().setMaximumBlockCount(2000)

    def append_log(self, text):
        """将接收到的日志追加到 QPlainTextEdit"""
        self.logpannel.append(text.strip())
        # 自动滚动到底部
        self.logpannel.ensureCursorVisible()
        # 2. 获取垂直滚动条
        scrollbar = self.logpannel.verticalScrollBar()
        # 3. 将滚动条位置设置为它的最大值（即最底部）
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event: QThread.event):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.terminate()  # 强制停止（如果任务不涉及数据库写入等安全操作）
            self.worker.wait()  # 等待线程完全退出
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    w = Window()
    w.show()
    app.exec()
