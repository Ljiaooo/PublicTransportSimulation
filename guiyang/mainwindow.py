# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SumoController(object):
    def setupUi(self, SumoController):
        SumoController.setObjectName("SumoController")
        SumoController.resize(618, 403)
        self.centralwidget = QtWidgets.QWidget(SumoController)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 0, 111, 331))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        self.comboBox = QtWidgets.QComboBox(self.frame)
        self.comboBox.setGeometry(QtCore.QRect(10, 130, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setBold(False)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(10, 30, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 80, 91, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.comboBox_2 = QtWidgets.QComboBox(self.frame)
        self.comboBox_2.setGeometry(QtCore.QRect(10, 180, 91, 31))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(130, 0, 481, 331))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.textEdit = QtWidgets.QTextEdit(self.page)
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 481, 331))
        self.textEdit.setObjectName("textEdit")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.frame_2 = QtWidgets.QFrame(self.page_2)
        self.frame_2.setGeometry(QtCore.QRect(9, 9, 461, 321))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(20, 145, 63, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(20, 195, 63, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(133, 90, 63, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(235, 90, 63, 20))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setGeometry(QtCore.QRect(336, 90, 63, 20))
        self.label_5.setObjectName("label_5")
        self.tableWidget = QtWidgets.QTableWidget(self.frame_2)
        self.tableWidget.setGeometry(QtCore.QRect(95, 120, 311, 101))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(2)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setColumnWidth(0,97)
        self.tableWidget.setColumnWidth(1,97)
        self.tableWidget.setColumnWidth(2,97)
        self.tableWidget.setRowHeight(0,40)
        self.tableWidget.setRowHeight(1,40)
        self.tableWidget.setVerticalScrollBarPolicy(1)
        self.tableWidget.setHorizontalScrollBarPolicy(1)
        self.stackedWidget.addWidget(self.page_2)
        SumoController.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SumoController)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 618, 21))
        self.menubar.setObjectName("menubar")
        SumoController.setMenuBar(self.menubar)

        self.retranslateUi(SumoController)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(SumoController)

    def retranslateUi(self, SumoController):
        _translate = QtCore.QCoreApplication.translate
        SumoController.setWindowTitle(_translate("SumoController", "SumoController"))
        self.comboBox.setItemText(0, _translate("SumoController", "线路选择"))
        self.comboBox.setItemText(1, _translate("SumoController", "47路"))
        self.comboBox.setItemText(2, _translate("SumoController", "48路"))
        self.comboBox.setItemText(3, _translate("SumoController", "263路"))
        self.pushButton.setText(_translate("SumoController", "全局展示"))
        self.pushButton_2.setText(_translate("SumoController", "车辆追踪"))
        self.comboBox_2.setItemText(0, _translate("SumoController", "统计信息"))
        self.comboBox_2.setItemText(1, _translate("SumoController", "时间&人数"))
        self.comboBox_2.setItemText(2, _translate("SumoController", "统计图(示例)"))
        self.textEdit.setHtml(_translate("SumoController", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"</style></head><body style=\" font-family:\'Segoe UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                                                                                                           </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:36pt;\">SUMO CONTROLLER</span></p></body></html>"))
        self.label.setText(_translate("SumoController", "等待人数"))
        self.label_2.setText(_translate("SumoController", "等待时间"))
        self.label_3.setText(_translate("SumoController", "47路"))
        self.label_4.setText(_translate("SumoController", "48路"))
        self.label_5.setText(_translate("SumoController", "263路"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("SumoController", "新建行"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("SumoController", "新建行"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SumoController", "新建列"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SumoController", "新建列"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SumoController", "新建列"))
