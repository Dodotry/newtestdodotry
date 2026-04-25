# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_mainwind(object):
    def setupUi(self, mainwind: QWidget):
        if not mainwind.objectName():
            mainwind.setObjectName("mainwind")
        mainwind.resize(823, 510)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        mainwind.setWindowIcon(icon)
        self.mainlayout = QVBoxLayout(mainwind)
        self.mainlayout.setObjectName("mainlayout")
        self.toplayout = QHBoxLayout()
        self.toplayout.setObjectName("toplayout")
        self.srclabel = QLabel(mainwind)
        self.srclabel.setObjectName("srclabel")
        self.srclabel.setMinimumSize(QSize(60, 0))
        self.srclabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toplayout.addWidget(self.srclabel)

        self.src_dir = QLineEdit(mainwind)
        self.src_dir.setObjectName("src_dir")
        self.src_dir.setMinimumSize(QSize(0, 30))
        self.src_dir.setStyleSheet(
            "QLineEdit {\n"
            "                border: 1px solid #888;           /* \u8fb9\u6846\u5bbd\u5ea6\u3001\u989c\u8272 */\n"
            "                border-radius: 6px;               /* \u5706\u89d2 */\n"
            "                padding: 6px;                      /* \u5185\u8fb9\u8ddd */\n"
            "                background-color: #f5f5f5;         /* \u80cc\u666f\u8272 */\n"
            "                color: #333;                       /* \u6587\u5b57\u989c\u8272 */\n"
            "                selection-background-color: #298DFF; /* \u9009\u4e2d\u6587\u672c\u80cc\u666f\u8272 */\n"
            "                selection-color: white;            /* \u9009\u4e2d\u6587\u672c\u989c\u8272 */\n"
            "            }"
        )
        self.src_dir.setReadOnly(True)

        self.toplayout.addWidget(self.src_dir)

        self.srcbtn = QPushButton(mainwind)
        self.srcbtn.setObjectName("srcbtn")
        self.srcbtn.setEnabled(True)
        self.srcbtn.setMinimumSize(QSize(60, 30))
        self.srcbtn.setMaximumSize(QSize(81, 16777215))
        font = QFont()
        font.setFamilies(["Microsoft YaHei UI"])
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setKerning(True)
        self.srcbtn.setFont(font)
        self.srcbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.srcbtn.setStyleSheet(
            "QPushButton {\n"
            "background-color: rgb(85, 0, 255);\n"
            "color: white;\n"
            "border-radius: 5px;\n"
            "padding: 3px 10px;\n"
            "}\n"
            "QPushButton:hover {\n"
            "background-color: #d20e1e;\n"
            "}\n"
            ""
        )

        self.toplayout.addWidget(self.srcbtn)

        self.save_label = QLabel(mainwind)
        self.save_label.setObjectName("save_label")
        self.save_label.setMinimumSize(QSize(60, 0))
        self.save_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toplayout.addWidget(self.save_label)

        self.output_dir = QLineEdit(mainwind)
        self.output_dir.setObjectName("output_dir")
        self.output_dir.setStyleSheet(
            "QLineEdit {\n"
            "                border: 1px solid #888;           /* \u8fb9\u6846\u5bbd\u5ea6\u3001\u989c\u8272 */\n"
            "                border-radius: 6px;               /* \u5706\u89d2 */\n"
            "                padding: 6px;                      /* \u5185\u8fb9\u8ddd */\n"
            "                background-color: #f5f5f5;         /* \u80cc\u666f\u8272 */\n"
            "                color: #333;                       /* \u6587\u5b57\u989c\u8272 */\n"
            "                selection-background-color: #298DFF; /* \u9009\u4e2d\u6587\u672c\u80cc\u666f\u8272 */\n"
            "                selection-color: white;            /* \u9009\u4e2d\u6587\u672c\u989c\u8272 */\n"
            "            }"
        )
        self.output_dir.setReadOnly(True)

        self.toplayout.addWidget(self.output_dir)

        self.dstbtn = QPushButton(mainwind)
        self.dstbtn.setObjectName("dstbtn")
        self.dstbtn.setEnabled(True)
        self.dstbtn.setMinimumSize(QSize(60, 30))
        self.dstbtn.setMaximumSize(QSize(81, 16777215))
        self.dstbtn.setFont(font)
        self.dstbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.dstbtn.setStyleSheet(
            "QPushButton {\n"
            "background-color: rgb(85, 0, 255);\n"
            "color: white;\n"
            "border-radius: 5px;\n"
            "padding: 3px 10px;\n"
            "}\n"
            "QPushButton:hover {\n"
            "background-color: #d20e1e;\n"
            "}"
        )

        self.toplayout.addWidget(self.dstbtn)

        self.mainlayout.addLayout(self.toplayout)

        self.logpannel = QTextEdit(mainwind)
        self.logpannel.setObjectName("logpannel")
        self.logpannel.setEnabled(True)
        self.logpannel.setStyleSheet("background-color: rgb(246, 248, 250);")
        self.logpannel.setReadOnly(True)

        self.mainlayout.addWidget(self.logpannel)

        self.buttomlayout = QHBoxLayout()
        self.buttomlayout.setObjectName("buttomlayout")
        self.buttonspace = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.buttomlayout.addItem(self.buttonspace)

        self.startbtn = QPushButton(mainwind)
        self.startbtn.setObjectName("startbtn")
        self.startbtn.setEnabled(True)
        self.startbtn.setMinimumSize(QSize(60, 30))
        self.startbtn.setFont(font)
        self.startbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.startbtn.setStyleSheet(
            "QPushButton {\n"
            "background-color: rgb(85, 0, 255);\n"
            "color: white;\n"
            "border-radius: 5px;\n"
            "padding: 3px 10px;\n"
            "}\n"
            "QPushButton:hover {\n"
            "background-color: #d20e1e;\n"
            "}\n"
            "QPushButton:disabled {\n"
            "    background-color: #dcdde1; \n"
            "    color: #7f8c8d;       \n"
            "    border: 1px solid #bdc3c7;\n"
            "}"
        )

        self.buttomlayout.addWidget(self.startbtn)

        self.clearbtn = QPushButton(mainwind)
        self.clearbtn.setObjectName("clearbtn")
        self.clearbtn.setEnabled(True)
        self.clearbtn.setMinimumSize(QSize(60, 30))
        self.clearbtn.setFont(font)
        self.clearbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clearbtn.setStyleSheet(
            "QPushButton {\n"
            "background-color: rgb(85, 0, 255);\n"
            "color: white;\n"
            "border-radius: 5px;\n"
            "padding: 3px 10px;\n"
            "}\n"
            "QPushButton:hover {\n"
            "background-color: #d20e1e;\n"
            "}"
        )

        self.buttomlayout.addWidget(self.clearbtn)

        self.exitbtn = QPushButton(mainwind)
        self.exitbtn.setObjectName("exitbtn")
        self.exitbtn.setEnabled(True)
        self.exitbtn.setMinimumSize(QSize(60, 30))
        self.exitbtn.setFont(font)
        self.exitbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exitbtn.setStyleSheet(
            "QPushButton {\n"
            "background-color: rgb(85, 0, 255);\n"
            "color: white;\n"
            "border-radius: 5px;\n"
            "padding: 3px 10px;\n"
            "}\n"
            "QPushButton:hover {\n"
            "background-color: #d20e1e;\n"
            "}"
        )

        self.buttomlayout.addWidget(self.exitbtn)

        self.mainlayout.addLayout(self.buttomlayout)

        QWidget.setTabOrder(self.logpannel, self.srcbtn)

        self.retranslateUi(mainwind)
        self.exitbtn.clicked.connect(mainwind.close)
        self.clearbtn.clicked.connect(self.logpannel.clear)

        QMetaObject.connectSlotsByName(mainwind)

    # setupUi

    def retranslateUi(self, mainwind):
        mainwind.setWindowTitle(
            QCoreApplication.translate("mainwind", "CSV2XLSX", None)
        )
        self.srclabel.setText(
            QCoreApplication.translate("mainwind", "\u6e90\u6587\u4ef6", None)
        )
        self.src_dir.setProperty(
            "border", QCoreApplication.translate("mainwind", "2px solid #888;", None)
        )
        self.src_dir.setProperty(
            "border-radius", QCoreApplication.translate("mainwind", "6px;", None)
        )
        self.srcbtn.setText(
            QCoreApplication.translate("mainwind", "\u6d4f  \u89c8", None)
        )
        self.save_label.setText(
            QCoreApplication.translate("mainwind", "\u4fdd\u5b58", None)
        )
        # if QT_CONFIG(tooltip)
        self.output_dir.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.output_dir.setPlaceholderText(
            QCoreApplication.translate(
                "mainwind",
                "\u9ed8\u8ba4\u4e3a\u6e90\u6587\u4ef6\u540c\u4e00\u76ee\u5f55",
                None,
            )
        )
        self.output_dir.setProperty(
            "border", QCoreApplication.translate("mainwind", "2px solid #888;", None)
        )
        self.output_dir.setProperty(
            "border-radius", QCoreApplication.translate("mainwind", "6px;", None)
        )
        self.dstbtn.setText(
            QCoreApplication.translate("mainwind", "\u6d4f  \u89c8", None)
        )
        # if QT_CONFIG(tooltip)
        self.logpannel.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.logpannel.setProperty("2px solid #888;", "")
        self.logpannel.setProperty(
            "border", QCoreApplication.translate("mainwind", "2px solid #888;", None)
        )
        self.logpannel.setProperty(
            "border-radius", QCoreApplication.translate("mainwind", "6px", None)
        )
        self.startbtn.setText(
            QCoreApplication.translate("mainwind", "\u5f00  \u59cb", None)
        )
        self.clearbtn.setText(
            QCoreApplication.translate("mainwind", "\u6e05  \u7a7a", None)
        )
        self.exitbtn.setText(
            QCoreApplication.translate("mainwind", "\u9000  \u51fa", None)
        )

    # retranslateUi
