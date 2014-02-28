# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\Python Programs\MIRVAP\GUI\MdiChildRegistration.ui'
#
# Created: Mon Feb 24 10:35:02 2014
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

class Ui_MdiChildRegistration(object):
    def setupUi(self, MdiChildRegistration):
        MdiChildRegistration.setObjectName(_fromUtf8("MdiChildRegistration"))
        MdiChildRegistration.resize(800, 600)
        MdiChildRegistration.setWindowTitle(_fromUtf8(""))
        self.centralWidget = QtGui.QWidget(MdiChildRegistration)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.resultQvtkWidget = QVTKWidget(self.centralWidget)
        self.resultQvtkWidget.setObjectName(_fromUtf8("resultQvtkWidget"))
        self.gridLayout.addWidget(self.resultQvtkWidget, 0, 0, 1, 2)
        self.infoTextEdit = QtGui.QTextEdit(self.centralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoTextEdit.sizePolicy().hasHeightForWidth())
        self.infoTextEdit.setSizePolicy(sizePolicy)
        self.infoTextEdit.setObjectName(_fromUtf8("infoTextEdit"))
        self.gridLayout.addWidget(self.infoTextEdit, 2, 0, 1, 1)
        self.oriQvtkWidget = QVTKWidget(self.centralWidget)
        self.oriQvtkWidget.setObjectName(_fromUtf8("oriQvtkWidget"))
        self.gridLayout.addWidget(self.oriQvtkWidget, 2, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        MdiChildRegistration.setCentralWidget(self.centralWidget)

        self.retranslateUi(MdiChildRegistration)
        QtCore.QMetaObject.connectSlotsByName(MdiChildRegistration)

    def retranslateUi(self, MdiChildRegistration):
        pass

from vtk import QVTKWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MdiChildRegistration = QtGui.QMainWindow()
    ui = Ui_MdiChildRegistration()
    ui.setupUi(MdiChildRegistration)
    MdiChildRegistration.show()
    sys.exit(app.exec_())

