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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QTableView, QVBoxLayout, QWidget)
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
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.labelColumn = QLabel(self.centralwidget)
        self.labelColumn.setObjectName(u"labelColumn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelColumn.sizePolicy().hasHeightForWidth())
        self.labelColumn.setSizePolicy(sizePolicy)
        self.labelColumn.setMinimumSize(QSize(70, 0))
        self.labelColumn.setMaximumSize(QSize(90, 16777215))

        self.toolbarLayout.addWidget(self.labelColumn)

        self.comboColumns = QComboBox(self.centralwidget)
        self.comboColumns.setObjectName(u"comboColumns")

        self.toolbarLayout.addWidget(self.comboColumns)

        self.labelKeyword = QLabel(self.centralwidget)
        self.labelKeyword.setObjectName(u"labelKeyword")
        sizePolicy.setHeightForWidth(self.labelKeyword.sizePolicy().hasHeightForWidth())
        self.labelKeyword.setSizePolicy(sizePolicy)
        self.labelKeyword.setMinimumSize(QSize(120, 0))
        self.labelKeyword.setMaximumSize(QSize(150, 16777215))

        self.toolbarLayout.addWidget(self.labelKeyword)

        self.comboKeywords = QComboBox(self.centralwidget)
        self.comboKeywords.setObjectName(u"comboKeywords")

        self.toolbarLayout.addWidget(self.comboKeywords)

        self.btnSearch = QPushButton(self.centralwidget)
        self.btnSearch.setObjectName(u"btnSearch")
        icon = QIcon()
        icon.addFile(u":/icon/icons/search.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnSearch.setIcon(icon)

        self.toolbarLayout.addWidget(self.btnSearch)

        self.btnReset = QPushButton(self.centralwidget)
        self.btnReset.setObjectName(u"btnReset")
        icon1 = QIcon()
        icon1.addFile(u":/icon/icons/reset.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnReset.setIcon(icon1)

        self.toolbarLayout.addWidget(self.btnReset)

        self.btnLoad = QPushButton(self.centralwidget)
        self.btnLoad.setObjectName(u"btnLoad")
        icon2 = QIcon()
        icon2.addFile(u":/icon/icons/open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnLoad.setIcon(icon2)

        self.toolbarLayout.addWidget(self.btnLoad)


        self.mainLayout.addLayout(self.toolbarLayout)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")

        self.mainLayout.addWidget(self.tableView)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0423\u043c\u043d\u0430\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u0430 \u0441 \u0444\u0438\u043b\u044c\u0442\u0440\u043e\u043c", None))
        self.labelColumn.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043b\u043e\u043d\u043a\u0430:", None))
        self.labelKeyword.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0441\u043b\u043e\u0432\u0430:", None))
        self.btnSearch.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0439\u0442\u0438", None))
        self.btnReset.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c", None))
        self.btnLoad.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c Excel", None))
    # retranslateUi

