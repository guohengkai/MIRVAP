# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\GitHub\MIRVAP\VesselSegmentation\SegmentationMainWindow.ui'
#
# Created: Fri Apr 18 14:43:26 2014
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

class Ui_SegmentationMainWindow(object):
    def setupUi(self, SegmentationMainWindow):
        SegmentationMainWindow.setObjectName(_fromUtf8("SegmentationMainWindow"))
        SegmentationMainWindow.resize(800, 571)
        self.centralwidget = QtGui.QWidget(SegmentationMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.qvtkWidget = QVTKWidget(self.centralwidget)
        self.qvtkWidget.setObjectName(_fromUtf8("qvtkWidget"))
        self.horizontalLayout.addWidget(self.qvtkWidget)
        SegmentationMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(SegmentationMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        SegmentationMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(SegmentationMainWindow)
        self.statusbar.setStyleSheet(_fromUtf8("QStatusBar::item{border: 0px}"))
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        SegmentationMainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(SegmentationMainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionView = QtGui.QAction(SegmentationMainWindow)
        self.actionView.setObjectName(_fromUtf8("actionView"))
        self.actionNext = QtGui.QAction(SegmentationMainWindow)
        self.actionNext.setObjectName(_fromUtf8("actionNext"))
        self.menuFile.addAction(self.actionView)
        self.menuFile.addAction(self.actionNext)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SegmentationMainWindow)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), SegmentationMainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(SegmentationMainWindow)

    def retranslateUi(self, SegmentationMainWindow):
        SegmentationMainWindow.setWindowTitle(_translate("SegmentationMainWindow", "Vessel Segmentation Platform", None))
        self.menuFile.setTitle(_translate("SegmentationMainWindow", "File", None))
        self.actionExit.setText(_translate("SegmentationMainWindow", "Exit", None))
        self.actionView.setText(_translate("SegmentationMainWindow", "View", None))
        self.actionNext.setText(_translate("SegmentationMainWindow", "Save and Next", None))

from vtk import QVTKWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SegmentationMainWindow = QtGui.QMainWindow()
    ui = Ui_SegmentationMainWindow()
    ui.setupUi(SegmentationMainWindow)
    SegmentationMainWindow.show()
    sys.exit(app.exec_())

