import json
import os
from pathlib import Path
import sqlite3
import subprocess
import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from natsort import os_sorted
from core.HomeController import QTableWidgetItemCenter, pushNotification
from core.WidgetsSetup import setUpProfilesTable, setUpVideosTable
from ui import ui_home
from ui import ui_uploadSettingsWindow
from windows.AddUserWindow import AddUserWindow
from datetime import datetime, timedelta, date

from windows.BulkScheduleWindow import BulkScheduleWindow
from windows.QueueWindow import QueueWindow


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = ui_home.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.inProcessing.hide()
        self.ui.addOneAccount.clicked.connect(self.openAddOneAccountWindow)
        self.ui.clearTable.clicked.connect(
            lambda: self.ui.videosTable.setRowCount(0))
        self.ui.videosTable.setColumnWidth(5, 145)
        self.ui.videosTable.setColumnWidth(9, 300)
        self.ui.assetsTable.setColumnWidth(0, 355)
        self.ui.loadToTable.clicked.connect(self.loadFilesFromFolder)
        self.ui.choosePath.clicked.connect(self.openOptionsBeforeLoading)
        self.ui.openQueue.clicked.connect(self.openQueueWindow)
        self.ui.uploadSettingsBtn.triggered.connect(
            self.openUploadSettingsWindow)
        self.ui.bulkScheduleWindowBtn.clicked.connect(
            self.openBulkScheduleWindow)
        self.loadProfilesToTable()
        setUpProfilesTable(self.ui.profilesTable, self.ui.assetsTable)
        setUpVideosTable(self.ui.videosTable,
                         self.ui.profilesTable, self.changePrivacyOfThisRow)

    def openUploadSettingsWindow(self):
        def saveChanges(platform, val):
            with open('./data/settingPlatform.json', 'r+', encoding="utf-8") as f:
                json_data = json.load(f)
                json_data[platform] = val
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()

        self.uploadSettingsWindow = QMainWindow()
        self.uploadSettingsWindow.ui = ui_uploadSettingsWindow.Ui_MainWindow()
        self.uploadSettingsWindow.ui.setupUi(self.uploadSettingsWindow)
        self.uploadSettingsWindow.show()
        self.uploadSettingsWindow.ui.reels.clicked.connect(
            lambda: saveChanges('facebook', 'reels'))
        self.uploadSettingsWindow.ui.videos.clicked.connect(
            lambda: saveChanges('facebook', 'videos'))
        self.uploadSettingsWindow.ui.shorts.clicked.connect(
            lambda: saveChanges('youtube', 'shorts'))
        self.uploadSettingsWindow.ui.normal.clicked.connect(
            lambda: saveChanges('youtube', 'normal'))
        f = open('./data/settingPlatform.json', 'r')
        data = json.load(f)
        typeUpload = data['facebook']
        if typeUpload == 'reels':
            self.uploadSettingsWindow.ui.reels.setChecked(True)
            self.uploadSettingsWindow.ui.videos.setChecked(False)
        else:
            self.uploadSettingsWindow.ui.reels.setChecked(False)
            self.uploadSettingsWindow.ui.videos.setChecked(True)

        typeUpload = data['youtube']
        if typeUpload == 'shorts':
            self.uploadSettingsWindow.ui.shorts.setChecked(True)
            self.uploadSettingsWindow.ui.normal.setChecked(False)
        else:
            self.uploadSettingsWindow.ui.shorts.setChecked(False)
            self.uploadSettingsWindow.ui.normal.setChecked(True)

    def assignThisVideoToProfiles(self, indexOfVideoToUpload, assetsToUploadArray, queueWindow: QueueWindow):
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()

        for indexAsset, assetName in enumerate(assetsToUploadArray):
            assetName: str

            if '*FB' in assetName:
                cursor.execute(
                    "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*FB'),))
                record = cursor.fetchone()
                ownerid = record[2]

                cursor.execute(
                    "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
                record = cursor.fetchone()
                profileName = record[1]
                id_ixbrowser = record[9]
                queueWindow.addWorkerTitleToReport(
                    indexAsset, profileName, assetName.strip('*FB'), id_ixbrowser)
            if '*YT' in assetName:
                cursor.execute(
                    "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*YT'),))
                record = cursor.fetchone()
                ownerid = record[2]

                cursor.execute(
                    "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
                record = cursor.fetchone()
                profileName = record[1]
                queueWindow.addWorkerTitleToReport(
                    indexAsset, profileName, assetName.strip('*YT'), id_ixbrowser)

            if '*X' in assetName:
                queueWindow.addWorkerTitleToReport(
                    indexAsset, assetName.strip('*X'), assetName.strip('*X'), id_ixbrowser)

            if '*IST' in assetName:
                queueWindow.addWorkerTitleToReport(
                    indexAsset, assetName.strip('*IST'), assetName.strip('*IST'), id_ixbrowser)

            queueWindow.addNewVideoToGridContainsVideo(
                indexOfVideoToUpload, indexAsset)

        conn.close()
        return

    def assignAssetsLabelToQueue(self, index, assetName: str):
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()

        if '*FB' in assetName:
            cursor.execute(
                "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*FB'),))
            record = cursor.fetchone()

            ownerid = record[2]

            cursor.execute(
                "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
            record = cursor.fetchone()
            profileName = record[1]
            id_ixbrowser = record[9]
            self.queueWindow.addWorkerTitleToReport(
                index, profileName, assetName.strip('*FB'), id_ixbrowser)

        if '*YT' in assetName:
            cursor.execute(
                "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*YT'),))
            record = cursor.fetchone()
            ownerid = record[2]

            cursor.execute(
                "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
            record = cursor.fetchone()
            profileName = record[1]
            id_ixbrowser = record[9]
            self.queueWindow.addWorkerTitleToReport(
                index, profileName, assetName.strip('*YT'), id_ixbrowser)

        if '*X' in assetName:
            cursor.execute(
                "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*X'),))
            record = cursor.fetchone()
            ownerid = record[2]

            cursor.execute(
                "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
            record = cursor.fetchone()
            profileName = record[1]
            id_ixbrowser = record[9]
            self.queueWindow.addWorkerTitleToReport(
                index, profileName, assetName.strip('*X'), id_ixbrowser)

        if '*IST' in assetName:
            cursor.execute(
                "SELECT * FROM asset WHERE asset_name = ?", (assetName.strip('*IST'),))
            record = cursor.fetchone()
            ownerid = record[2]

            cursor.execute(
                "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
            record = cursor.fetchone()
            profileName = record[1]
            id_ixbrowser = record[9]
            self.queueWindow.addWorkerTitleToReport(
                index, profileName, assetName.strip('*IST'), id_ixbrowser)

        self.queueWindow.queueDict[index] = []
        return

    def openQueueWindow(self):
        try:
            if self.queueWindow != None:
                pushNotification('Bạn đang mở rồi')
                return
        except:
            pass
        self.browserQueue = {}
        self.queueWindow = QueueWindow(self)
        self.queueWindow.show()
        final = []
        for theIndex in range(0, self.ui.videosTable.rowCount()):

            profilesArrText = self.ui.videosTable.item(theIndex, 7)
            if profilesArrText is not None and profilesArrText.text() != '':
                string = profilesArrText.text().replace(
                    "[", "").replace("]", "")  # Loại bỏ các ký tự "[" và "]"
                array = string.split(",")
                final = list(set(final + array))

                # self.assignThisVideoToProfiles(
                #     theIndex, array, self.queueWindow)
                # notThing = False
        for theIndex, asset in enumerate(final):
            self.assignAssetsLabelToQueue(
                theIndex, asset)

        for theIndex, asset in enumerate(final):
            for theIndexVideo in range(0, self.ui.videosTable.rowCount()):
                profilesArrText = self.ui.videosTable.item(theIndexVideo, 7)
                if profilesArrText is not None and profilesArrText.text() != '':
                    if asset in profilesArrText.text():
                        self.queueWindow.addNewVideoToGridContainsVideo(
                            theIndexVideo, theIndex)
                        data = self.queueWindow.queueDict[theIndex]
                        data.append(theIndexVideo)
                        self.queueWindow.queueDict[theIndex] = data

        self.queueWindow.assetsInQueue = final

    def openAddOneAccountWindow(self):

        self.auw = AddUserWindow(
            self.ui.typeAddComboBox.currentText(), self.loadProfilesToTable)
        self.auw.show()

    def loadProfilesToTable(self):
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles")
        records = cursor.fetchall()
        conn.close()
        data = {
            1: 'Facebook',
            2: 'Youtube',
            3: 'X-Twitter',
            4: 'Instagram',
        }
        self.ui.profilesTable.setRowCount(0)
        for record in records:
            profileName = record[1]
            uore = record[2]
            row = self.ui.profilesTable.rowCount()
            self.ui.profilesTable.insertRow(row)
            self.ui.profilesTable.setItem(
                row, 0, QTableWidgetItemCenter(profileName))
            self.ui.profilesTable.setItem(row, 1, QTableWidgetItemCenter(uore))
            self.ui.profilesTable.setItem(
                row, 3, QTableWidgetItemCenter(data[record[5]]))
            self.ui.profilesTable.setItem(
                row, 4, QTableWidgetItemCenter(record[7]))
            if record[6]:
                self.ui.profilesTable.setItem(
                    row, 2, QTableWidgetItemCenter('Đã đăng nhập'))
            else:
                self.ui.profilesTable.setItem(
                    row, 2, QTableWidgetItemCenter('Chưa đăng nhập'))

    def openOptionsBeforeLoading(self):
        rs = QFileDialog.getExistingDirectory(
            QMainWindow(), caption='Select Location:')
        if rs != '':
            self.ui.folderPath.setText(rs)

    def loadFilesFromFolder(self):
        try:
            if self.loadFromFolderThread != None and self.loadFromFolderThread.isRunning():
                return
        except:
            pass
        if self.ui.folderPath.text() == '':
            pushNotification('Bạn chưa chọn đường dẫn!')
            return

        def convert_to_hms(seconds):
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        def loadToTheTable(title, outputDuration, absolute_file_path):

            numRow = self.ui.videosTable.rowCount()
            dropdownPrivacy = QComboBox()
            dropdownPrivacy.addItems(['Public', 'Schedule'])
            dropdownPrivacy.currentIndexChanged.connect(
                lambda selected_index, row=numRow: self.changePrivacyOfThisRow(row, selected_index))
            rspc = QProgressBar()
            rspc.setValue(100)

            self.ui.videosTable.insertRow(numRow)

            self.ui.videosTable.setItem(
                numRow, 0, QTableWidgetItemCenter(title))

            self.ui.videosTable.setItem(
                numRow, 1, QTableWidgetItemCenter(title))

            self.ui.videosTable.setItem(

                numRow, 2, QTableWidgetItemCenter(''))

            self.ui.videosTable.setItem(
                numRow, 3, QTableWidgetItemCenter(format(convert_to_hms(int(float(outputDuration))))))

            self.ui.videosTable.setCellWidget(
                numRow, 4, dropdownPrivacy)

            self.ui.videosTable.setCellWidget(
                numRow, 6, rspc)
            self.ui.videosTable.setItem(
                numRow, 8, QTableWidgetItem(absolute_file_path))

        uploadFolderPath = self.ui.folderPath.text()

        class loadToTable(QThread):
            pushErr = pyqtSignal(str)
            pushInfo = pyqtSignal(str, bytes, str)

            def __init__(self):
                super().__init__()

            def run(self):

                ext = [".flv", ".mp4", ".mkv", ".mov",
                       ".ts", ".jpg", ".jpeg", ".png"]
                for file in os_sorted(os.listdir(uploadFolderPath)):
                    full = os.path.join(uploadFolderPath, file)
                    absolute_file_path = str(Path.cwd() / full)
                    print(f"==>> absolute_file_path: {absolute_file_path}")
                    if '-RENDERED' in absolute_file_path:
                        continue
                    if not absolute_file_path.endswith(tuple(ext)):
                        continue
                    command = ['ffprobe', '-show_entries', 'format=duration', '-of',
                               'default=noprint_wrappers=1:nokey=1', absolute_file_path]
                    startupinfo = None
                    if os.name == 'nt':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    try:
                        output = subprocess.check_output(
                            command, startupinfo=startupinfo, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                    except:
                        print(traceback.format_exc())
                        output = 0

                    file_split = file.split('.')
                    title = file_split[0]
                    self.pushInfo.emit(title, output, absolute_file_path)

        self.ui.inProcessing.show()
        self.loadFromFolderThread = loadToTable()
        self.loadFromFolderThread.pushErr.connect(pushNotification)
        self.loadFromFolderThread.pushInfo.connect(loadToTheTable)
        self.loadFromFolderThread.start()
        while not self.loadFromFolderThread.isFinished():
            QApplication.processEvents()
        self.ui.inProcessing.hide()

    def changePrivacyOfThisRow(self, row, selected_index):
        valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

        if selected_index == 1:
            dateEdit = QDateTimeEdit(self.setGoodTimeAtStart(minutes=20))

            dateEdit.setDisplayFormat("dd/MM/yyyy hh:mm AP")
            dateEdit.editingFinished.connect(lambda: dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(
                dateEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute()))))))
            dateEdit.setMinimumDateTime(self.setGoodTimeAtStart(minutes=15))
            dateEdit.setMaximumDateTime(
                self.setGoodTimeAtStart(minutes=0, days=90))
            dateEdit.dateTimeChanged.connect(lambda: dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(
                dateEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute()))))))
            dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(dateEdit.dateTime().time(
            ).hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute())))))
            self.ui.videosTable.setCellWidget(row, 5, dateEdit)
        else:
            self.ui.videosTable.removeCellWidget(row, 5)

    def setGoodTimeAtStart(self, minutes, days=0):
        # lay time hien tai
        crt = datetime.now()
        goodTime = crt + timedelta(minutes=minutes, days=days)
        year = goodTime.year
        month = goodTime.month
        day = goodTime.day
        hour = goodTime.hour
        minute = goodTime.minute
        return QDateTime(year, month, day, hour, minute)

    def openBulkScheduleWindow(self):
        geo = self.geometry()
        self.bulkScheduleWindow = BulkScheduleWindow(self.ui.videosTable)
        self.bulkScheduleWindow.bulkPrivacyApplyFuncs = self.bulkPrivacyApply
        rs = self.bulkScheduleWindow.bulkScheduleWindowUI.importVideoFromMainTable(
            self.ui.videosTable)
        self.bulkScheduleWindow.bulkScheduleWindowUI.videoPerDay.setMaximum(
            self.ui.videosTable.rowCount())
        if rs:
            self.bulkScheduleWindow.move(geo.x()-81, geo.y()+75)
            self.bulkScheduleWindow.setWindowModality(Qt.ApplicationModal)
            self.bulkScheduleWindow.show()

    def bulkPrivacyApply(self, customCol=None):

        if self.ui.videosTable.rowCount() == 0:
            msg = QMessageBox()
            msg.setWindowTitle('Thông báo!')
            msg.setText('Bảng không có gì để áp dụng hàng loạt!')
            msg.exec_()
            return

        if customCol == 0:
            # thường dụng để gọi tất cả về public
            for row in range(self.ui.videosTable.rowCount()):
                self.ui.videosTable.removeCellWidget(row, 5)
                cbb = self.ui.videosTable.cellWidget(row, 4)
                cbb.setCurrentIndex(customCol)

        elif customCol == 1:
            self.setByBulk = True
            crt_schedule = self.dateTimeEdit.dateTime()
            self.crt_schedule_str = crt_schedule.toString(
                'dd.MM.yyyy hh:mm:ss.zzz')
            for row in range(self.videoTable.rowCount()):
                cbb = self.videoTable.cellWidget(row, 4)
                cbb.setCurrentIndex(0)

                cbb.setCurrentIndex(1)
            self.setByBulk = False
