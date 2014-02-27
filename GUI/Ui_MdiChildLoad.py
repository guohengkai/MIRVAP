# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Python Programs\MIRVAP\GUI\MdiChildLoad.ui'
#
# Created: Sun Feb 09 18:17:53 2014
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

class Ui_MdiChildLoad(object):
    def setupUi(self, MdiChildLoad):
        MdiChildLoad.setObjectName(_fromUtf8("MdiChildLoad"))
        MdiChildLoad.resize(800, 600)
        MdiChildLoad.setWindowTitle(_fromUtf8(""))
        self.centralWidget = QtGui.QWidget(MdiChildLoad)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.qvtkWidget = QVTKWidget(self.centralWidget)
        self.qvtkWidget.setObjectName(_fromUtf8("qvtkWidget"))
        self.verticalLayout.addWidget(self.qvtkWidget)
        MdiChildLoad.setCentralWidget(self.centralWidget)

        self.retranslateUi(MdiChildLoad)
        QtCore.QMetaObject.connectSlotsByName(MdiChildLoad)

    def retranslateUi(self, MdiChildLoad):
        pass

from vtk import QVTKWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MdiChildLoad = QtGui.QMainWindow()
    ui = Ui_MdiChildLoad()
    ui.setupUi(MdiChildLoad)
    MdiChildLoad.show()
    sys.exit(app.exec_())

