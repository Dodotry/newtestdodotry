#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-04-19 01:01:19
LastEditors: Dodotry
LastEditTime: 2026-04-22 21:27:03
'''
import sys
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QPushButton
from PySide6.QtCore import Slot
from testpy6 import Ui_app
from pathlib import PureWindowsPath


class MainWindow(QWidget, Ui_app): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    @Slot()
    def on_srcbtn_clicked(self):
        self.select_dir(self.src_dir)

    @Slot()
    def on_dstbtn_clicked(self):
        self.select_dir(self.save_dir)

    def select_dir(self, entry: QLineEdit):
        path =  QFileDialog.getExistingDirectory(self, "选择文件夹")
        if path:
            entry.setText(str(PureWindowsPath(path)))


    @Slot()
    def on_startbtn_clicked(self):
        src_dir = self.src_dir.text()
        save_dir = self.save_dir.text()
        if not src_dir or not save_dir:
            self.plainTextEdit.appendPlainText("请选择源目录和目标目录")
            return
        self.plainTextEdit.appendPlainText(f"开始转换:{src_dir}到{save_dir}")

    @Slot()
    def on_cleanbtn_clicked(self):
        self.plainTextEdit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())