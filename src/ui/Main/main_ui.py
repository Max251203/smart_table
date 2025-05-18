# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
import resources.resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(6, 6, 6, 6)
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.toolbarLayout.setContentsMargins(-1, 0, -1, 0)
        self.btnSmartSearch = QPushButton(self.centralwidget)
        self.btnSmartSearch.setObjectName(u"btnSmartSearch")
        icon = QIcon()
        icon.addFile(u":/icon/icons/arrow_down.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnSmartSearch.setIcon(icon)
        self.btnSmartSearch.setIconSize(QSize(24, 24))

        self.toolbarLayout.addWidget(self.btnSmartSearch)

        self.btnReset = QPushButton(self.centralwidget)
        self.btnReset.setObjectName(u"btnReset")
        icon1 = QIcon()
        icon1.addFile(u":/icon/icons/reset.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnReset.setIcon(icon1)
        self.btnReset.setIconSize(QSize(24, 24))

        self.toolbarLayout.addWidget(self.btnReset)

        self.btnAddRecord = QPushButton(self.centralwidget)
        self.btnAddRecord.setObjectName(u"btnAddRecord")
        icon2 = QIcon()
        icon2.addFile(u":/icon/icons/add.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnAddRecord.setIcon(icon2)
        self.btnAddRecord.setIconSize(QSize(24, 24))

        self.toolbarLayout.addWidget(self.btnAddRecord)

        self.btnLoad = QPushButton(self.centralwidget)
        self.btnLoad.setObjectName(u"btnLoad")
        icon3 = QIcon()
        icon3.addFile(u":/icon/icons/open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnLoad.setIcon(icon3)
        self.btnLoad.setIconSize(QSize(24, 24))

        self.toolbarLayout.addWidget(self.btnLoad)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)


        self.mainLayout.addLayout(self.toolbarLayout)

        self.searchPanelContainer = QWidget(self.centralwidget)
        self.searchPanelContainer.setObjectName(u"searchPanelContainer")
        self.searchPanelContainer.setMaximumSize(QSize(16777215, 60))
        self.searchPanelContainer.setVisible(False)
        self.searchPanelLayout = QHBoxLayout(self.searchPanelContainer)
        self.searchPanelLayout.setObjectName(u"searchPanelLayout")
        self.searchPanelLayout.setContentsMargins(0, 0, 0, 0)
        self.searchPanel = QFrame(self.searchPanelContainer)
        self.searchPanel.setObjectName(u"searchPanel")
        self.searchPanel.setFrameShape(QFrame.StyledPanel)
        self.searchPanel.setFrameShadow(QFrame.Raised)

        self.searchPanelLayout.addWidget(self.searchPanel)


        self.mainLayout.addWidget(self.searchPanelContainer)

        self.tableContainer = QWidget(self.centralwidget)
        self.tableContainer.setObjectName(u"tableContainer")
        self.tableLayout = QVBoxLayout(self.tableContainer)
        self.tableLayout.setObjectName(u"tableLayout")
        self.tableLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.tableContainer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0423\u043c\u043d\u0430\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u0430 \u0441 \u0444\u0438\u043b\u044c\u0442\u0440\u043e\u043c", None))
        self.btnSmartSearch.setText(QCoreApplication.translate("MainWindow", u"\u0423\u043c\u043d\u044b\u0439 \u043f\u043e\u0438\u0441\u043a", None))
        self.btnReset.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c", None))
        self.btnAddRecord.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u044c", None))
        self.btnLoad.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c Excel", None))
    # retranslateUi

