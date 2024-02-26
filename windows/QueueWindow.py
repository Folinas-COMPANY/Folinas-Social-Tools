import json
import os
import re
import sqlite3
import traceback
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import *
import requests
from core.HomeController import QTableWidgetItemCenter, StaffUpload, pushNotification
from ui import ui_reportWorkerStickWindow
from time import sleep
import win32api
import win32gui
import win32process


class QueueWindow(QMainWindow):
    def __init__(self, homeWd):
        super(QueueWindow, self).__init__()
        self.ui = ui_reportWorkerStickWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.videosTable = homeWd.ui.videosTable
        self.homeWd = homeWd
        self.browserQueue = homeWd.browserQueue
        self.queueDict = {}
        self.assetsInQueue = []
        self.browsersInQueue = {}
        self.waitThread = {}
        if not os.path.isfile('./data/settingPlatform.json'):
            last_location = {
                "facebook": "reels",
                "youtube": "shorts"
            }
            json_object = json.dumps(last_location)
            file1 = open('./data/settingPlatform.json', "w", encoding="utf-8")
            file1.write(json_object)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.deleteLater()
        self.homeWd.queueWindow = None

    def stopThisWorkerNow(self, indexAsset, startWorker, waitForThread, id_ixbrowser):
        try:
            staffUpload: StaffUpload = self.threadsUpload[indexAsset]
            staffUpload.stopNow()
        except:
            return
        action = 'http://127.0.0.1:53200/api/v2/profile-close'
        paras = {
            "profile_id": id_ixbrowser

        }
        try:
            requests.post(action, json=paras)
        except:
            pass
        self.clearACell(indexAsset)
        # staffUpload: StaffUpload = self.threadsUpload[indexAsset]
        startWorker.show()
        waitForThread.hide()
        try:
            del self.browsersInQueue[id_ixbrowser]
        except KeyError:
            pass

    def clearACell(self, index):

        def add_video_to_grid(grid_layout, buttonVideo):
            count = grid_layout.count()
            row = count // 2
            col = count % 2

            if col == 2:  # đạt giới hạn 5 cột
                row += 1
                col = 0

            grid_layout.addWidget(buttonVideo, row, col)

        layout = self.ui.gridLayoutForScreen
        buttons = []
        while layout.count():
            try:
                wg = layout.takeAt(0).widget()
                wgname = wg.objectName()
                if wgname == f'theLayout{index}':
                    wg.deleteLater()
                else:
                    buttons.append(wg)
            except:
                pass

        for btn in buttons:
            add_video_to_grid(layout, btn)

    def updateDoneColorToVideoInWorkerReport(self, indexVideo, indexProfile):
        # màu vàng xanh green
        try:
            vbox = self.ui.verticalLayoutForWorker.findChild(
                QVBoxLayout, f'Worker{indexProfile}')
            gridContainsVideo = vbox.findChild(
                QGridLayout, 'gridContainsVideo')
            box = gridContainsVideo.findChild(
                QHBoxLayout, f'Video{str(int(indexVideo)+1)}')
            button = box.itemAt(0).widget()
            combo_style = """
                QPushButton {
                    background-color: #85C88A;
                    border:0px;
                }
            """
            button.setStyleSheet(combo_style)
            # self.window.parentWindow.saveThisProject(True,self.window.theId)
            # QApplication.processEvents()
            return

        except:
            print(traceback.format_exc())

    def updateSlashStateWorker(self, profileIndex, text):
        try:
            qlb = self.ui.gridWidgetForScreen.findChild(
                QLabel, f'slashState{profileIndex}')
            qlb.setText(text)
        except RuntimeError:
            print('Bị tắt đột ngột cửa sổ, bỏ qua!')
        except AttributeError:
            pass

    def startThisWorkerNow(self, indexAsset, startWorker, waitForThread, id_ixbrowser):

        thisQueue = self

        class waitForIt(QThread):
            waitNow = pyqtSignal()

            def run(self):
                try:

                    while True:
                        data = thisQueue.browsersInQueue[id_ixbrowser]
                        self.waitNow.emit()
                        sleep(1)

                except:
                    pass

        self.waitThread[indexAsset] = waitForIt()
        wait: waitForIt = self.waitThread[indexAsset]
        wait.waitNow.connect(waitForThread.show)
        wait.start()
        while not wait.isFinished():
            QApplication.processEvents()

        startWorker.hide()

        indexVideos = self.queueDict[indexAsset]
        assetName = self.assetsInQueue[indexAsset]
        # Danh sách các chuỗi cần tìm và xóa
        strings_to_remove = ["\*FB", "\*YT", "\*X", "\*IST"]

        # Sử dụng re.sub để tìm và xóa các chuỗi
        for s in strings_to_remove:
            assetName = re.sub(s, '', assetName)

        self.threadsUpload = {}
        uploadTask = StaffUpload(
            indexVideos, assetName, indexAsset, self.browsersInQueue, self.videosTable)
        self.threadsUpload[indexAsset] = uploadTask
        uploadTask.update_hwndBrowser_signal.connect(
            self.addNewBrowserToGridScreen)
        uploadTask.update_slashState_signal.connect(
            self.updateSlashStateWorker)
        uploadTask.update_colorDone_signal.connect(
            self.updateDoneColorToVideoInWorkerReport)
        uploadTask.clear_cell_signal.connect(self.clearACell)
        uploadTask.start()
        while not uploadTask.isFinished():
            QApplication.processEvents()

    def addNewBrowserToGridScreen(self, processId, profileInfomation):
        print(f"==>> processId: {processId}")
        # self.browsersId.append(processId)

        def showThisFromPid():
            def get_hwnds_for_pid(pid):
                def callback(hwnd, hwnds):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                        _, found_pid = win32process.GetWindowThreadProcessId(
                            hwnd)
                        if found_pid == pid:
                            hwnds.append(hwnd)
                    return True

                hwnds = []
                win32gui.EnumWindows(callback, hwnds)
                return hwnds

            hwnd_pointer = get_hwnds_for_pid(processId)
            if len(hwnd_pointer) == 0:
                pushNotification('Cửa sổ không tồn tại hoặc đã bị đóng!')
                return
            try:

                hwnd = hwnd_pointer[1]
            except:
                hwnd = hwnd_pointer[0]
            win32gui.SetForegroundWindow(hwnd)

        def get_hwnds_for_pid(pid):
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        hwnds.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            return hwnds

        hwnd_pointer = get_hwnds_for_pid(processId)
        try:
            hwnd = hwnd_pointer[1]
        except:
            hwnd = hwnd_pointer[0]
        try:

            count = self.ui.gridLayoutForScreen.count()
            row = count // 2
            col = count % 2

            if col == 2:  # đạt giới hạn 5 cột
                row += 1
                col = 0

            # style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            # exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

            widget = QWidget.createWindowContainer(QWindow.fromWinId(hwnd))
            widget.setMinimumHeight(400)

            # widget.hwnd = hwnd
            # widget.style = style
            # widget.exstyle = exstyle

            workerName = QLabel()

            workerName.setText(f'Tài sản: {profileInfomation[1]}: ')
            workerName.setStyleSheet("""
                border: 1px solid #a4b0be;
                border-left:0;
                border-right:0;
                border-bottom:0;
                padding-top:5px;
            """)
            workerName.setObjectName('workerName')
            slash = QLabel(widget)
            slash.setText('trạng thái')
            slash.setObjectName(f'slashState{profileInfomation[0]}')
            slash.setStyleSheet("""
                padding-left:1px;
            """)
            theLayout = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(widget)
            layout.addWidget(workerName)
            layout.addWidget(slash)
            # Thêm vertical spacer vào layout
            spacer = QSpacerItem(
                20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layout.addItem(spacer)
            theLayout.setLayout(layout)
            theLayout.setObjectName(f'theLayout{profileInfomation[0]}')

            self.ui.gridLayoutForScreen.addWidget(theLayout, row, col)
            # self.gridLayoutForScreen.addWidget(layout, row, col)
            # self.gridLayoutForScreen.addLayout(layout)
        except Exception as e:
            print(traceback.format_exc())

    def addNewVideoToGridContainsVideo(self, indexVideo, indexOfAsset, style=None):
        print(f"==>> indexVideo: {indexVideo}")
        print(f"==>> indexOfAsset: {indexOfAsset}")

        def add_video_to_grid(grid_layout, buttonVideo):
            count = grid_layout.count()
            row = count // 5
            col = count % 5

            if col == 5:  # đạt giới hạn 5 cột
                row += 1
                col = 0

            grid_layout.addLayout(buttonVideo, row, col)

        def remove_and_rearrange(layout: QGridLayout, buttonLayout: QHBoxLayout, buttonVideo: QPushButton, indexVideo):
            # xoá button khỏi layou
            layout.removeItem(buttonLayout)
            layout.removeWidget(buttonVideo)
            buttonVideo.deleteLater()
            buttonLayout.deleteLater()
            listVideo: list = self.window.staffs[indexOfAsset]
            listVideo.remove(indexVideo)
            self.window.staffs[indexOfAsset] = listVideo
            buttons = []
            while layout.count():
                try:
                    layoutH = layout.takeAt(0).layout()
                    buttons.append(layoutH)
                except:
                    pass

            for btn in buttons:
                add_video_to_grid(layout, btn)

        def showContextMenu(gridLayout, buttonLayout, buttonVideo, indexVideo):
            menu = QMenu()

            discard = QAction('Loại khỏi hàng chờ')
            discard.triggered.connect(lambda: remove_and_rearrange(
                gridLayout, buttonLayout, buttonVideo, indexVideo))
            menu.addAction(discard)

            widget_pos = self.window.mapFromGlobal(QCursor.pos())
            menu.exec_(self.window.mapToGlobal(widget_pos))

        vbox = self.ui.verticalLayoutForWorker.findChild(

            QVBoxLayout, f'Worker{indexOfAsset}')

        gridContainsVideo = vbox.findChild(QGridLayout, 'gridContainsVideo')

        btn = gridContainsVideo.findChild(
            QHBoxLayout, f'Video{str(int(indexVideo)+1)}')

        if btn is not None:
            print('Đã thêm vào rồi')
            return

        # listVideo = self.window.staffs[indexOfAsset]
        # listVideo.append(indexVideo)
        # self.window.staffs[indexOfAsset] = listVideo

        buttonLayout = QHBoxLayout()
        buttonLayout.setObjectName(f'Video{str(int(indexVideo)+1)}')
        buttonVideo = QPushButton(f'Video {str(int(indexVideo)+1)}')
        buttonVideo.setContextMenuPolicy(Qt.CustomContextMenu)
        # buttonVideo.customContextMenuRequested.connect(lambda: showContextMenu(
        #     gridContainsVideo, buttonLayout, buttonVideo, indexVideo))

        combo_style = """
            QPushButton {
                background-color: #E8D5C4;
                border:0px solid black;
            }
            QPushButton:hover {
                background-color: #F0A04B;
                color:black;
                border:0px solid black;
                
            }
        """

        buttonVideo.setStyleSheet(combo_style)
        if style:
            buttonVideo.setStyleSheet(style)

        buttonLayout.addWidget(buttonVideo)
        add_video_to_grid(gridContainsVideo, buttonLayout)

    def addWorkerTitleToReport(self, indexAsset, profileName, assetName, id_ixbrowser):
        # tiến hành đưa các profile phải làm lên bảng
        try:
            vboxxx = self.ui.verticalLayoutForWorker.findChild(
                QVBoxLayout, f'Worker{indexAsset}')
            if vboxxx is not None:
                print('Đã khởi tạo rồi')
                return
        except:
            vboxxx = None

        # self.window.staffs[indexOfProfile] = []
        # self.window.staffsUore[indexOfProfile] = uore
        # self.window.staffsName[indexOfProfile] = profileName
        # tạo 1 khung dọc và set nó tên là f'Worker{indexAndProfile[0]}'
        vbox = QVBoxLayout()
        vbox.setObjectName(f'Worker{indexAsset}')
        hbox = QHBoxLayout()
        label = QLabel(
            f'<html><head/><body><p><span style=" font-weight:600;">Kênh: {profileName} - {assetName}</span></p></body></html>')
        label.setMaximumWidth(250)

        hbox.addWidget(label)
        hbox.addStretch()
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbox.addItem(spacer)
        waitForThread = QLabel('Đang chờ')
        waitForThread.setStyleSheet('color:red')
        waitForThread.hide()
        startWorker = QPushButton('Chạy')
        startWorker.setObjectName(f'startWorker{indexAsset}')
        startWorker.clicked.connect(
            lambda: self.startThisWorkerNow(indexAsset, startWorker, waitForThread, id_ixbrowser))
        startWorker.setStyleSheet("""
            QPushButton{
    
                border: 0px solid #a4b0be;
                border-radius: 3px;
                color: #2f3542;
                background: white;
                padding: 3px 9px;
            }


            QPushButton:hover
            {
                color: white;
                background-color: #FF7D7D;
            }
        """)
        stopWorker = QPushButton('Dừng')
        stopWorker.clicked.connect(
            lambda: self.stopThisWorkerNow(indexAsset, startWorker, waitForThread, id_ixbrowser))
        stopWorker.setStyleSheet("""
            QPushButton{
    
                border: 0px solid #a4b0be;
                border-radius: 3px;
                color: #2f3542;
                background: white;
                padding: 3px 9px;
            }


            QPushButton:hover
            {
                color: white;
                background-color: #FF7D7D;
            }
        """)

        hbox.addWidget(startWorker)
        hbox.addWidget(stopWorker)

        # thêm 1 QLabel vào khung dọc đó
        vbox.addLayout(hbox)

        # # thêm tiếp nút dừng toàn bộ
        # stopBtn = QPushButton('Dừng luồng này')
        # vbox.addWidget(stopBtn)

        # tạo và thêm luôn 1 Grid có tên là gridContainsVideo vào khung dọc, nó sẽ nằm bên dưới
        gridLayoutVideo = QGridLayout()
        gridLayoutVideo.setObjectName('gridContainsVideo')
        vbox.addLayout(gridLayoutVideo)

        # bước cuối, nhét 1 đối tượng up này vào khung dọc
        self.ui.verticalLayoutForWorker.addLayout(vbox)
