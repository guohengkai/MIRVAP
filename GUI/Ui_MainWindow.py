# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Python Programs\MIRVAP\GUI\MainWindow.ui'
#
# Created: Tue Feb 25 14:02:35 2014
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 571)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        self.mdiArea.setAutoFillBackground(False)
        self.mdiArea.setViewMode(QtGui.QMdiArea.TabbedView)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.mdiArea.setObjectName(_fromUtf8("mdiArea"))
        self.horizontalLayout.addWidget(self.mdiArea)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuLoad = QtGui.QMenu(self.menuFile)
        self.menuLoad.setObjectName(_fromUtf8("menuLoad"))
        self.menuStart = QtGui.QMenu(self.menubar)
        self.menuStart.setObjectName(_fromUtf8("menuStart"))
        self.menuRegister = QtGui.QMenu(self.menuStart)
        self.menuRegister.setObjectName(_fromUtf8("menuRegister"))
        self.menuPlugin = QtGui.QMenu(self.menuStart)
        self.menuPlugin.setObjectName(_fromUtf8("menuPlugin"))
        self.menuProcess = QtGui.QMenu(self.menuStart)
        self.menuProcess.setObjectName(_fromUtf8("menuProcess"))
        self.menuAnalysis = QtGui.QMenu(self.menuStart)
        self.menuAnalysis.setObjectName(_fromUtf8("menuAnalysis"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setStyleSheet(_fromUtf8("QStatusBar::item{border: 0px}"))
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.menuFile.addAction(self.menuLoad.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        self.menuStart.addAction(self.menuRegister.menuAction())
        self.menuStart.addAction(self.menuPlugin.menuAction())
        self.menuStart.addAction(self.menuProcess.menuAction())
        self.menuStart.addAction(self.menuAnalysis.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuStart.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Medical Image Registration Visualization and Analysis Platform", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuLoad.setTitle(_translate("MainWindow", "Load", None))
        self.menuStart.setTitle(_translate("MainWindow", "Start", None))
        self.menuRegister.setTitle(_translate("MainWindow", "Register", None))
        self.menuPlugin.setTitle(_translate("MainWindow", "Plugin", None))
        self.menuProcess.setTitle(_translate("MainWindow", "Process", None))
        self.menuAnalysis.setTitle(_translate("MainWindow", "Analysis", None))
        self.actionSave.setText(_translate("MainWindow", "Save...", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

