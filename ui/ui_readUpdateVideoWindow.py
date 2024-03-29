# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Folinas Socials Tool\ui\readUpdateVideoWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(516, 390)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo/icon-sw.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.updateDetailsVideoFrame = QtWidgets.QFrame(self.centralwidget)
        self.updateDetailsVideoFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.updateDetailsVideoFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.updateDetailsVideoFrame.setObjectName("updateDetailsVideoFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.updateDetailsVideoFrame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.updateDetailsVideoFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.titleLine = QtWidgets.QLineEdit(self.updateDetailsVideoFrame)
        self.titleLine.setObjectName("titleLine")
        self.verticalLayout_2.addWidget(self.titleLine)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.updateDetailsVideoFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.description = QtWidgets.QPlainTextEdit(self.updateDetailsVideoFrame)
        self.description.setEnabled(True)
        self.description.setMinimumSize(QtCore.QSize(0, 100))
        self.description.setPlaceholderText("")
        self.description.setObjectName("description")
        self.verticalLayout_3.addWidget(self.description)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.updateDetailsVideoFrame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.tags = QtWidgets.QPlainTextEdit(self.updateDetailsVideoFrame)
        self.tags.setEnabled(True)
        self.tags.setMinimumSize(QtCore.QSize(0, 100))
        self.tags.setPlaceholderText("")
        self.tags.setObjectName("tags")
        self.verticalLayout_4.addWidget(self.tags)
        self.verticalLayout.addLayout(self.verticalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveChanges = QtWidgets.QPushButton(self.updateDetailsVideoFrame)
        self.saveChanges.setObjectName("saveChanges")
        self.horizontalLayout.addWidget(self.saveChanges)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addWidget(self.updateDetailsVideoFrame, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "Tiêu đề"))
        self.label_3.setText(_translate("MainWindow", "Mô tả"))
        self.label_4.setText(_translate("MainWindow", "Thẻ tags"))
        self.saveChanges.setText(_translate("MainWindow", "Lưu thay đổi"))
import resource_rc
