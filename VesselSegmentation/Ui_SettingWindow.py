# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\GitHub\MIRVAP\VesselSegmentation\SettingWindow.ui'
#
# Created: Fri Apr 18 14:43:27 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SettingWindow(object):
    def setupUi(self, SettingWindow):
        SettingWindow.setObjectName(_fromUtf8("SettingWindow"))
        SettingWindow.resize(800, 571)
        self.centralwidget = QtGui.QWidget(SettingWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.qvtkWidget = QVTKWidget(self.centralwidget)
        self.qvtkWidget.setObjectName(_fromUtf8("qvtkWidget"))
        self.horizontalLayout.addWidget(self.qvtkWidget)
        SettingWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(SettingWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        SettingWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(SettingWindow)
        self.statusbar.setStyleSheet(_fromUtf8("QStatusBar::item{border: 0px}"))
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        SettingWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(SettingWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionInit = QtGui.QAction(SettingWindow)
        self.actionInit.setObjectName(_fromUtf8("actionInit"))
        self.actionMean = QtGui.QAction(SettingWindow)
        self.actionMean.setObjectName(_fromUtf8("actionMean"))
        self.menuFile.addAction(self.actionInit)
        self.menuFile.addAction(self.actionMean)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SettingWindow)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), SettingWindow.close)
        QtCore.QMetaObject.connectSlotsByName(SettingWindow)

    def retranslateUi(self, SettingWindow):
        SettingWindow.setWindowTitle(_translate("SettingWindow", "Vessel Segmentation Platform Setting", None))
        self.menuFile.setTitle(_translate("SettingWindow", "File", None))
        self.actionExit.setText(_translate("SettingWindow", "Exit", None))
        self.actionInit.setText(_translate("SettingWindow", "Initialize the ini file", None))
        self.actionMean.setText(_translate("SettingWindow", "Get the mean contour", None))

from vtk import QVTKWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SettingWindow = QtGui.QMainWindow()
    ui = Ui_SettingWindow()
    ui.setupUi(SettingWindow)
    SettingWindow.show()
    sys.exit(app.exec_())

