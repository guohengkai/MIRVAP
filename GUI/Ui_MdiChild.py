# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\GitHub\MIRVAP\GUI\MdiChild.ui'
#
# Created: Sun Mar 02 00:13:12 2014
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

class Ui_MdiChild(object):
    def setupUi(self, MdiChild):
        MdiChild.setObjectName(_fromUtf8("MdiChild"))
        MdiChild.resize(800, 600)
        MdiChild.setWindowTitle(_fromUtf8(""))
        self.centralWidget = QtGui.QWidget(MdiChild)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.qvtkWidget = QVTKWidget(self.centralWidget)
        self.qvtkWidget.setObjectName(_fromUtf8("qvtkWidget"))
        self.verticalLayout.addWidget(self.qvtkWidget)
        MdiChild.setCentralWidget(self.centralWidget)

        self.retranslateUi(MdiChild)
        QtCore.QMetaObject.connectSlotsByName(MdiChild)

    def retranslateUi(self, MdiChild):
        pass

from vtk import QVTKWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MdiChild = QtGui.QMainWindow()
    ui = Ui_MdiChild()
    ui.setupUi(MdiChild)
    MdiChild.show()
    sys.exit(app.exec_())

