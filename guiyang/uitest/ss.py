import sys
from PyQt5 import QtWidgets

#create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

#open qss file
File = open("Toolery.qss",'r')

with File:
	qss = File.read()
	app.setStyleSheet(qss)

#run 
window.show()
sys.exit(app.exec_())
	