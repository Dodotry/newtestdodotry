#!/usr/bin/env python3
# encoding=utf-8
'''
Author: Dodotry
Date: 2026-04-19 00:56:18
LastEditors: Dodotry
LastEditTime: 2026-04-19 01:40:37
'''
################################################################################
## Form generated from reading UI file 'testuiLGfXsB.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_app(object):
    def setupUi(self, app):
        if not app.objectName():
            app.setObjectName(u"app")
        app.resize(746, 490)
        font = QFont()
        font.setPointSize(10)
        app.setFont(font)
        self.setWindowIcon(QIcon(r"D:\Users\Dodotry\Downloads\fit.ico"))
        self.verticalLayout = QVBoxLayout(app)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.src_label = QLabel(app)
        self.src_label.setObjectName(u"src_label")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.src_label.setFont(font1)
        self.src_label.setTextFormat(Qt.TextFormat.AutoText)
        self.src_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.src_label)

        self.src_dir = QLineEdit(app)
        self.src_dir.setObjectName(u"src_dir")
        font2 = QFont()
        font2.setFamilies([u"Microsoft YaHei UI"])
        font2.setPointSize(12)
        font2.setBold(False)
        font2.setItalic(False)
        self.src_dir.setFont(font2)
        self.src_dir.setStyleSheet(u"background-color: rgb(249, 249, 249);\n"
"font: 11pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.src_dir)

        self.srcbtn = QPushButton(app)
        self.srcbtn.setObjectName(u"srcbtn")
        self.srcbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.srcbtn.setStyleSheet(u"background-color: rgb(203, 0, 0);\n"
"border-color: rgb(255, 255, 127);\n"
"font: 11pt \"Microsoft YaHei UI\";\n"
"color: rgb(255, 255, 255);")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        self.srcbtn.setIcon(icon)
        self.srcbtn.setIconSize(QSize(12, 12))

        self.horizontalLayout.addWidget(self.srcbtn)

        self.save_label = QLabel(app)
        self.save_label.setObjectName(u"save_label")
        font3 = QFont()
        font3.setPointSize(12)
        self.save_label.setFont(font3)

        self.horizontalLayout.addWidget(self.save_label)

        self.save_dir = QLineEdit(app)
        self.save_dir.setObjectName(u"save_dir")
        self.save_dir.setFont(font2)
        self.save_dir.setStyleSheet(u"background-color: rgb(249, 249, 249);\n"
"font: 11pt \"Microsoft YaHei UI\";")

        self.horizontalLayout.addWidget(self.save_dir)

        self.dstbtn = QPushButton(app)
        self.dstbtn.setObjectName(u"dstbtn")
        self.dstbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.dstbtn.setStyleSheet(u"background-color: rgb(203, 0, 0);\n"
"border-color: rgb(255, 255, 127);\n"
"font: 11pt \"Microsoft YaHei UI\";\n"
"color: rgb(255, 255, 255);")
        self.dstbtn.setIcon(icon)
        self.dstbtn.setIconSize(QSize(12, 12))

        self.horizontalLayout.addWidget(self.dstbtn)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.startbtn = QPushButton(app)
        self.startbtn.setObjectName(u"startbtn")
        self.startbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.startbtn.setStyleSheet(u"background-color: rgb(203, 0, 0);\n"
"border-color: rgb(255, 255, 127);\n"
"font: 11pt \"Microsoft YaHei UI\";\n"
"color: rgb(255, 255, 255);")
        self.startbtn.setIconSize(QSize(12, 12))

        self.horizontalLayout_2.addWidget(self.startbtn)

        self.cleanbtn = QPushButton(app)
        self.cleanbtn.setObjectName(u"cleanbtn")
        self.cleanbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cleanbtn.setStyleSheet(u"background-color: rgb(203, 0, 0);\n"
"border-color: rgb(255, 255, 127);\n"
"font: 11pt \"Microsoft YaHei UI\";\n"
"color: rgb(255, 255, 255);")
        self.cleanbtn.setIconSize(QSize(12, 12))

        self.horizontalLayout_2.addWidget(self.cleanbtn)

        self.exitbtn = QPushButton(app)
        self.exitbtn.setObjectName(u"exitbtn")
        self.exitbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exitbtn.setStyleSheet(u"background-color: rgb(203, 0, 0);\n"
"border-color: rgb(255, 255, 127);\n"
"font: 11pt \"Microsoft YaHei UI\";\n"
"color: rgb(255, 255, 255);")
        self.exitbtn.setIconSize(QSize(12, 12))

        self.horizontalLayout_2.addWidget(self.exitbtn)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.plainTextEdit = QPlainTextEdit(app)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        font4 = QFont()
        font4.setPointSize(11)
        self.plainTextEdit.setFont(font4)
        self.plainTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEdit)


        self.retranslateUi(app)
        self.exitbtn.clicked.connect(app.close)

        QMetaObject.connectSlotsByName(app)
    # setupUi

    def retranslateUi(self, app):
        app.setWindowTitle(QCoreApplication.translate("app", u"\u6d4b\u8bd5", None))
        self.src_label.setText(QCoreApplication.translate("app", u"\u6e90\u6570\u636e", None))
#if QT_CONFIG(tooltip)
        self.src_dir.setToolTip(QCoreApplication.translate("app", u"\u9009\u62e9\u6e90\u76ee\u5f55", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.src_dir.setWhatsThis(QCoreApplication.translate("app", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.src_dir.setText("")
        self.src_dir.setPlaceholderText(QCoreApplication.translate("app", u"\u8bf7\u9009\u62e9\u6e90\u76ee\u5f55", None))
        self.srcbtn.setText(QCoreApplication.translate("app", u" \u6d4f\u89c8", None))
        self.save_label.setText(QCoreApplication.translate("app", u"\u4fdd \u5b58", None))
#if QT_CONFIG(tooltip)
        self.save_dir.setToolTip(QCoreApplication.translate("app", u"<html><head/><body><p>\u4fdd\u5b58\u76ee\u5f55\uff0c\u9ed8\u8ba4\u6e90\u76ee\u5f55\u4f4d\u7f6e</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.save_dir.setWhatsThis(QCoreApplication.translate("app", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.save_dir.setText("")
        self.save_dir.setPlaceholderText(QCoreApplication.translate("app", u"\u4fdd\u5b58\u76ee\u5f55", None))
        self.dstbtn.setText(QCoreApplication.translate("app", u" \u6d4f\u89c8", None))
        self.startbtn.setText(QCoreApplication.translate("app", u"\u5f00\u59cb", None))
        self.cleanbtn.setText(QCoreApplication.translate("app", u"\u6e05\u7406\u65e5\u5fd7", None))
        self.exitbtn.setText(QCoreApplication.translate("app", u"\u9000\u51fa", None))
    # retranslateUi

