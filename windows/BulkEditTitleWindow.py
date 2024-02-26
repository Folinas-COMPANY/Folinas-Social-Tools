import random
from core.HomeController import pushNotification
from ui import ui_bulkEditTitleWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class BulkEditTitleWindow(QMainWindow):
    def __init__(self, videoTable):
        super(BulkEditTitleWindow, self).__init__()
        self.ui = BulkEditTitleWindowUI(
            self, videoTable, videoTable.unique_arr)


class BulkEditTitleWindowUI(ui_bulkEditTitleWindow.Ui_MainWindow):
    def __init__(self, window, videoTable: QTableWidget, unique_arr):
        super(BulkEditTitleWindowUI, self).__init__()
        self.setupUi(window)
        self.undoAction.hide()
        self.videoTable = videoTable
        self.unique_arr = unique_arr
        self.keepOriginal.clicked.connect(lambda: self.pickType('original'))
        self.increaseNumber.clicked.connect(lambda: self.pickType('increase'))
        self.aboveSection.clicked.connect(
            lambda: self.oneForAll(self.aboveSection.isChecked()))
        self.belowSection.clicked.connect(
            lambda: self.multiple(self.belowSection.isChecked()))
        self.thirdSection.clicked.connect(
            lambda: self.targetPosition(self.thirdSection.isChecked()))
        self.fourthSection.clicked.connect(
            lambda: self.targetReplace(self.fourthSection.isChecked()))
        self.applyToTable.clicked.connect(self.applyToMainTable)
        self.clearAll.clicked.connect(self.clearAllTitle)
        self.undoAction.clicked.connect(self.undoLastTitle)
        target = ''
        for row in unique_arr:
            row = int(row) + 1
            target = target + str(row) + ' ,'
        target = target[:-2]
        self.whichIndex.setText(target)
        self.modes = [self.aboveSection, self.belowSection,
                      self.thirdSection, self.fourthSection]
        self.typeApply = ''
        self.undoTitle = []

    def pickType(self, mode):
        if mode == 'original':
            self.increaseSection.setEnabled(False)
        else:
            self.increaseSection.setEnabled(True)

    def oneForAll(self, val):
        if val:
            for mode in self.modes:
                mode.setChecked(False)
            self.aboveSection.setChecked(True)
            self.typeApply = 'ONEFORALL'
        else:
            self.typeApply = ''

    def multiple(self, val):
        if val:
            for mode in self.modes:
                mode.setChecked(False)
            self.belowSection.setChecked(True)
            self.typeApply = 'SCATTER'
        else:
            self.typeApply = ''

    def targetPosition(self, val):
        if val:
            for mode in self.modes:
                mode.setChecked(False)
            self.thirdSection.setChecked(True)
            self.typeApply = 'TARGETPOSITION'
        else:
            self.typeApply = ''

    def targetReplace(self, val):
        if val:
            for mode in self.modes:
                mode.setChecked(False)
            self.fourthSection.setChecked(True)
            self.typeApply = 'TARGETREPLACE'
        else:
            self.typeApply = ''

    def applyToMainTable(self):
        if self.toTitle.isChecked():
            col = 0
        elif self.toDescription.isChecked():
            col = 1
        elif self.toTags.isChecked():
            col = 2

        if self.typeApply == '':
            pushNotification('Bạn phải chọn 1 chế độ trước!')
            return

        if self.typeApply == 'ONEFORALL':
            title = self.oneTitle.text()
            if title == '':
                pushNotification('Bạn không được để trống trường này!')
                return
            fixedText = self.fixedText.text()
            startFrom = self.startFrom.value()
            self.undoTitle = []
            if self.keepOriginal.isChecked():
                for row in self.unique_arr:
                    originalTitle = self.videoTable.item(row, col).text()
                    self.undoTitle.append(originalTitle)
                    self.videoTable.setItem(row, col, QTableWidgetItem(title))

            if self.increaseNumber.isChecked():
                for row in self.unique_arr:
                    originalTitle = self.videoTable.item(row, col).text()
                    self.undoTitle.append(originalTitle)
                    self.videoTable.setItem(row, col, QTableWidgetItem(
                        f'{title}{fixedText}{startFrom}'))
                    startFrom += 1

        elif self.typeApply == 'SCATTER':
            text = self.plainTextEdit.toPlainText()
            text = text.split('\n')
            self.undoTitle = []
            if self.ordered.isChecked():
                for i, row in enumerate(self.unique_arr):
                    try:
                        originalTitle = self.videoTable.item(row, col).text()
                        self.undoTitle.append(originalTitle)
                        self.videoTable.setItem(
                            row, col, QTableWidgetItem(text[i]))
                    except IndexError:
                        break

            if self.random.isChecked():
                for row in self.unique_arr:
                    try:
                        originalTitle = self.videoTable.item(row, col).text()
                        self.undoTitle.append(originalTitle)
                        self.videoTable.setItem(
                            row, col, QTableWidgetItem(random.choice(text)))
                    except IndexError:
                        break

        elif self.typeApply == 'TARGETPOSITION':

            if not self.startOfTitle.isChecked() and not self.endOfTitle.isChecked():
                pushNotification('Bạn cần phải chọn 1 chế độ trước!')
                return

            title = self.textNeedToAdd.text()
            if title == '':
                pushNotification('Bạn không được để trống trường này!')
                return

            self.undoTitle = []
            for row in self.unique_arr:
                originalTitle = self.videoTable.item(row, col).text()
                self.undoTitle.append(originalTitle)
                if self.startOfTitle.isChecked():
                    newTitle = f'{title}{originalTitle}'

                if self.endOfTitle.isChecked():
                    newTitle = f'{originalTitle}{title}'

                self.videoTable.setItem(row, col, QTableWidgetItem(newTitle))

        elif self.typeApply == 'TARGETREPLACE':
            replaceThisText = self.replaceThisText.text()
            replaceToThis = self.replaceToThis.text()
            if replaceThisText == '':
                pushNotification('Bạn không được để trống trường này!')
                return
            self.undoTitle = []
            for row in self.unique_arr:
                originalTitle: str = self.videoTable.item(row, col).text()
                self.undoTitle.append(originalTitle)
                newTitle = originalTitle.replace(
                    replaceThisText, replaceToThis)
                self.videoTable.setItem(row, col, QTableWidgetItem(newTitle))

    def undoLastTitle(self):
        for i, row in enumerate(self.unique_arr):
            try:
                self.videoTable.setItem(
                    row, 0, QTableWidgetItem(self.undoTitle[i]))
            except:
                pass

    def clearAllTitle(self):
        if self.toTitle.isChecked():
            col = 0
        elif self.toDescription.isChecked():
            col = 1
        elif self.toTags.isChecked():
            col = 2
        self.undoTitle = []
        for row in self.unique_arr:
            originalTitle: str = self.videoTable.item(row, col).text()
            self.undoTitle.append(originalTitle)
            self.videoTable.setItem(row, col, QTableWidgetItem(''))
