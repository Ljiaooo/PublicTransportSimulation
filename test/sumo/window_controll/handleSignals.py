import globalVal
from PyQt5.QtWidgets import  QMainWindow
from mainwindow import Ui_SumoController
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtWidgets

class Widget(QMainWindow, Ui_SumoController):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


    def focus_line(self, line):
        if line  == -1:
            return
        else:
            globalVal.onfocus = line
    
        
    def global_focus(self):
        globalVal.onfocus = -1
    
    
    def track_signal(self):
        globalVal.track_status = not globalVal.track_status

    def line_choose(self):
        text = self.line_choose_input.text()
        if text.isdigit():
            line = int(text)
            globalVal.onfocus = line
        else:
            return 
    
    
    def refresh_table(self):
        index = self.statistics_combobox.currentIndex()
        if index == 1:
            self.global_0.setText(globalVal.data["overview"][0])
            self.global_1.setText(globalVal.data["overview"][1])
            self.global_2.setText(globalVal.data["overview"][2])
            self.global_3.setText(globalVal.data["overview"][3])
        
        if index == 2:
            cnt = 0
            maxLen = len(globalVal.data["waiting_num"])
            for i in range(5):
                for j in range(8):
                    if cnt<maxLen:
                        text = str(globalVal.data["waiting_num"][cnt])
                    else:
                        text = ' '
                    item = QTableWidgetItem(text)
                    self.tableWidget_2.setItem(i, j, item)
                    self.tableWidget_2.update()


        if index == 3:
            cnt = 0
            for i in range(5):
                for j in range(8):
                    if cnt<maxLen:
                        text = str(globalVal.data["waiting_time"][cnt])
                    else:
                        text = ' '
                    item = QTableWidgetItem(text)
                    self.tableWidget_3.setItem(i, j, item)
                    self.tableWidget_3.update()

    
    
    def changeStackedWidgetPage(self, index):
        self.stackedWidget.setCurrentPage(index)
