from core.HomeController import pushNotification
from ui import ui_BulkScheduleWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from datetime import datetime, timedelta, date


class BulkScheduleWindow(QMainWindow):
    def __init__(self, videoTable):
        super(BulkScheduleWindow, self).__init__()
        self.bulkScheduleWindowUI = BulkScheduleWindowUI(self, videoTable)
        self.bulkPrivacyApplyFuncs = None


class BulkScheduleWindowUI(ui_BulkScheduleWindow.Ui_MainWindow):
    def __init__(self, window, videoTable: QTableWidget):
        super(BulkScheduleWindowUI, self).__init__()
        self.setupUi(window)
        self.window = window
        self.bigVideoTable = videoTable
        self.type = None
        self.videoTable = VideosTableWidget()
        self.videoTable.setColumnWidth(0, 30)
        self.videoTable.setColumnWidth(1, 239)
        self.videoTable.setColumnWidth(5, 150)
        self.videoTable.itemDoubleClicked.connect(lambda: self.on_click_item())
        self.videoTable.setObjectName('scheduleTable')
        self.videoTable.setStyleSheet("""
        QTableWidget{
        border: 1px solid #a4b0be; 
        
        background-color:#EEEEEE;
        }

        
        QCheckBox::indicator{
            border-top:3px solid #586E72;
            border-bottom:3px solid #586E72;
            border: 1px solid #586E72;
            border-radius:6px;
            subcontrol-position: center center;
        }
        
        QCheckBox::indicator:checked {
            
            border: 2px solid #FFC85B;
            background-color: #FFC85B;
        }

        """)
        self.layoutForVideosPerdayWg.setHidden(True)
        self.layoutForVideosPerdayWg.setStyleSheet(
            """
            QWidget#layoutForVideosPerdayWg{
                border: 1px solid #a4b0be; 
                border-radius: 3px;
                margin-top:9px;
                margin-bottom:12px;
            }    
        """
        )
        self.verticalLayoutForTable.addWidget(self.videoTable)
        self.leftSchedule.clicked.connect(self.leftChecked)
        self.rightSchedule.clicked.connect(self.rightChecked)
        self.videoPerDay.valueChanged.connect(self.onChangeVideoPerDay)

        self.applyToMainTable.clicked.connect(self.applyToMainTableFuncs)
        self.makeMainTablePublic.clicked.connect(
            lambda: self.makeMainTablePublicFuncs(0))
        self.tickAllBtn.clicked.connect(self.tickAll)
        self.unTickAllBtn.clicked.connect(self.unTickAll)
        self.randomBtn.clicked.connect(self.randomChoice)
        valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        self.dateTimeEdit.setDisplayFormat("dd/MM/yyyy hh:mm AP")
        self.dateTimeEdit.setDateTime(self.setGoodTimeAtStart(minutes=20))
        self.dateTimeEdit.editingFinished.connect(lambda: self.dateTimeEdit.setDateTime(QDateTime(self.dateTimeEdit.dateTime().date(), QTime(
            self.dateTimeEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - self.dateTimeEdit.dateTime().time().minute()))))))
        self.dateTimeEdit.dateTimeChanged.connect(lambda: self.dateTimeEdit.setDateTime(QDateTime(self.dateTimeEdit.dateTime().date(), QTime(
            self.dateTimeEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - self.dateTimeEdit.dateTime().time().minute()))))))
        self.dateTimeEdit.setMinimumDateTime(
            self.setGoodTimeAtStart(minutes=15))
        self.dateTimeEdit.setMaximumDateTime(
            self.setGoodTimeAtStart(minutes=0, days=11))
        self.dateTimeEdit.setDateTime(QDateTime(self.dateTimeEdit.dateTime().date(), QTime(self.dateTimeEdit.dateTime(
        ).time().hour(), min(valid_minutes, key=lambda x: abs(x - self.dateTimeEdit.dateTime().time().minute())))))

        self.dayStart.setMinimumDateTime(
            (self.setGoodTimeAtStart(minutes=0, days=1)))
        self.dayStart.setMaximumDateTime(
            (self.setGoodTimeAtStart(minutes=0, days=11)))

    def on_click_item(self, item: QTableWidgetItem):
        print(item.row())

    def tickAll(self):
        for row in range(0, self.videoTable.rowCount()):
            _item_parent = self.videoTable.cellWidget(row, 0)
            _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
            if not _item_cb.isChecked():
                _item_cb.setChecked(True)

    def unTickAll(self):
        for row in range(0, self.videoTable.rowCount()):
            _item_parent = self.videoTable.cellWidget(row, 0)
            _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
            if _item_cb.isChecked():
                _item_cb.setChecked(False)

    def randomChoice(self):
        import random
        self.unTickAll()
        numbers = random.sample(range(self.videoTable.rowCount()), random.randint(
            1, self.videoTable.rowCount()))
        for index in numbers:
            _item_parent = self.videoTable.cellWidget(index, 0)
            _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
            _item_cb.setChecked(True)

    def applyToMainTableFuncs(self):
        if not self.type:
            pushNotification('Bạn chưa chọn kiểu lên lịch!!')
            return

        self.applyToThem(self.type)

    def applyToThem(self, type):
        valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        if type == 'left':
            # code xử lý cho lên lịch theo khoảng cách
            crt_schedule = self.dateTimeEdit.dateTime()
            crt_schedule_str = crt_schedule.toString(
                'dd.MM.yyyy hh:mm:ss.zzz')
            count = 0
            for row in range(0, self.videoTable.rowCount()):

                # cbb = self.bigVideoTable.cellWidget(row,4)
                # cbb.setCurrentIndex(0)
                _item_parent = self.videoTable.cellWidget(row, 0)
                _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                if _item_cb.isChecked():
                    print(f"==>> row: {row}")
                    cbb = self.bigVideoTable.cellWidget(row, 4)

                    cbb.setCurrentIndex(1)
                    self.bigVideoTable.removeCellWidget(row, 5)
                    offsetT = self.offsetTime.value()
                    plus_m = count*offsetT
                    dateEdit = QDateTimeEdit(
                        self.setBulkTimeFull(crt_schedule_str, plus_m))
                    dateEdit.setDisplayFormat("dd/MM/yyyy hh:mm AP")
                    dateEdit.editingFinished.connect(lambda: dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(
                        dateEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute()))))))
                    dateEdit.dateTimeChanged.connect(lambda: dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(
                        dateEdit.dateTime().time().hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute()))))))
                    dateEdit.setMinimumDateTime(
                        self.setGoodTimeAtStart(minutes=15))
                    dateEdit.setMaximumDateTime(
                        self.setGoodTimeAtStart(minutes=0, days=11))
                    dateEdit.setDateTime(QDateTime(dateEdit.dateTime().date(), QTime(dateEdit.dateTime().time(
                    ).hour(), min(valid_minutes, key=lambda x: abs(x - dateEdit.dateTime().time().minute())))))
                    self.bigVideoTable.setCellWidget(row, 5, dateEdit)
                    count += 1

        elif type == 'right':
            # code xử lý cho lên lịch theo ngày
            countVpd = self.videoPerDay.value()
            rowCount = []
            for row in range(0, self.videoTable.rowCount()):
                # cbb = self.bigVideoTable.cellWidget(row,4)
                # cbb.setCurrentIndex(0)
                _item_parent = self.videoTable.cellWidget(row, 0)
                _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                if _item_cb.isChecked():
                    rowCount.append(row)

            structureTime = []
            listHbox = self.layoutForVideosPerday.children()
            for layout in listHbox:
                items = (layout.itemAt(i) for i in range(layout.count()))
                arr = []
                for widget in items:
                    arr.append(widget)

                datetime = arr[1].widget()
                datetime = datetime.time()
                hour = datetime.hour()
                minute = datetime.minute()
                structureTime.append([hour, minute])
            if len(rowCount) <= len(structureTime):
                # nếu số video chọn ít hơn số lượng lên lịch trong ngày
                for i, rowIndex in enumerate(rowCount):
                    theTime = structureTime[i]
                    dateEdit = QDateTimeEdit(self.giveMeTheTimeIWant(
                        days=0, hour=theTime[0], minute=theTime[1]))
                    cbb = self.bigVideoTable.cellWidget(rowIndex, 4)
                    cbb.setCurrentIndex(1)
                    self.bigVideoTable.removeCellWidget(rowIndex, 5)
                    self.bigVideoTable.setCellWidget(rowIndex, 5, dateEdit)
            elif len(rowCount) > len(structureTime):
                # nếu số video chọn nhiều hơn số lượng lên lịch trong ngày
                stt = 0
                day = 0
                for rowIndex in rowCount:
                    try:
                        theTime = structureTime[stt]
                    except:
                        stt = 0
                        day += 1
                        theTime = structureTime[stt]
                    dateEdit = QDateTimeEdit(self.giveMeTheTimeIWant(
                        days=day, hour=theTime[0], minute=theTime[1]))
                    cbb = self.bigVideoTable.cellWidget(rowIndex, 4)
                    cbb.setCurrentIndex(1)
                    self.bigVideoTable.removeCellWidget(rowIndex, 5)
                    self.bigVideoTable.setCellWidget(rowIndex, 5, dateEdit)
                    stt += 1
                pass

            # countRowInLoop = 0
            # for row in rowCount:
            #     # while countVpd:
            #     for j in range(len(structureTime)):
            #         timee = structureTime[j]
            #         dateEdit = QDateTimeEdit(self.giveMeTheTimeIWant(days=i,hour=timee[0], minute=timee[1]))
            #         # dateEdit.setMinimumDateTime(self.setGoodTimeAtStart(minutes=30))
            #         self.bigVideoTable.setCellWidget(countRowInLoop, 5, dateEdit)
            #         countRowInLoop = countRowInLoop + 1

    def makeMainTablePublicFuncs(self, num):
        self.window.bulkPrivacyApplyFuncs(num)

    def giveMeTheTimeIWant(self, days, hour, minute):

        date_time = self.dayStart.dateTime()
        date_s = date_time.date()
        year = date_s.year()
        month = date_s.month()
        day = date_s.day()

        dateModal = date(year, month, day)
        newDate = dateModal + timedelta(days=days)
        Newyear = newDate.year
        Newmonth = newDate.month
        Newday = newDate.day

        return QDateTime(Newyear, Newmonth, Newday, hour, minute)

    def setBulkTimeFull(self, crt_schedule_str, plus_m):
        given_time = datetime.strptime(
            crt_schedule_str, '%d.%m.%Y %H:%M:%S.%f')
        goodTime = given_time + timedelta(minutes=plus_m)
        year = goodTime.year
        month = goodTime.month
        day = goodTime.day
        hour = goodTime.hour
        minute = goodTime.minute
        return QDateTime(year, month, day, hour, minute)

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

    def onChangeVideoPerDay(self):

        val = self.videoPerDay.value()
        if self.layoutForVideosPerday.count() > 0:
            while self.layoutForVideosPerday.count():
                item = self.layoutForVideosPerday.takeAt(0)
                while item.count():
                    subItem = item.takeAt(0)
                    wg = subItem.widget()
                    if wg is not None:
                        wg.deleteLater()
                    else:
                        self.layoutForVideosPerday.removeItem(item)
                    self.layoutForVideosPerday.removeItem(item)
        valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        for i in range(val):
            vhbox = QHBoxLayout()
            title = QLabel(f'video {i+1}')
            vhbox.addWidget(title)
            timeSchedule = RoundedTimeEdit()
            timeSchedule.setMinimumHeight(22)

            vhbox.addWidget(timeSchedule)
            self.layoutForVideosPerday.addLayout(vhbox)

    def round_minute(self):
        # Lấy giá trị phút hiện tại
        valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        current_minute = self.time().minute()

        # Tìm giá trị phút gần nhất trong danh sách các giá trị phút hợp lệ
        nearest_minute = min(self.valid_minutes,
                             key=lambda x: abs(x - current_minute))

        # Thiết lập giá trị phút mới
        self.setTime(QTime(self.time().hour(), nearest_minute))

    def leftChecked(self, val):
        if val:
            self.type = 'left'
            self.leftSchedule.setChecked(val)
            self.dateTimeEdit.setEnabled(val)
            self.offsetTime.setEnabled(val)
            self.rightSchedule.setChecked(False)
        else:
            self.type = None
        self.layoutForVideosPerdayWg.setHidden(True)

    def rightChecked(self, val):
        if val:
            self.type = 'right'
            self.rightSchedule.setChecked(val)
            self.videoPerDay.setEnabled(val)
            self.dayStart.setEnabled(val)
            self.leftSchedule.setChecked(False)
            self.layoutForVideosPerdayWg.setHidden(False)

        else:
            self.type = None
            self.layoutForVideosPerdayWg.setHidden(True)

    def importVideoFromMainTable(self, mainVideoTable):
        # print(mainVideoTable)
        if mainVideoTable.rowCount() == 0:
            pushNotification(
                'Bảng rỗng!!!\nVui lòng load thêm video từ mạng xã hội hoặc load từ trong folder!')
            return False
        demo = 0
        for row in range(0, mainVideoTable.rowCount()):
            title = mainVideoTable.item(row, 0).text()

            view = mainVideoTable.item(row, 1).text()

            like = mainVideoTable.item(row, 2).text()

            duration = mainVideoTable.item(row, 3).text()

            # self.videoTable.setItem(row,0,title)
            self.videoTable.insertRow(self.videoTable.rowCount())
            checkbox = QCheckBox()
            checkbox.setObjectName("cbToRun")
            if demo == 0:
                checkbox.setChecked(True)
                demo = 1
            checkbox_h_box = QHBoxLayout()
            checkbox_h_box.addWidget(checkbox, 0, Qt.AlignCenter)
            checkbox_widget = QWidget()
            checkbox_widget.setLayout(checkbox_h_box)

            self.videoTable.setCellWidget(row, 0, checkbox_widget)
            self.videoTable.setItem(row, 1, QTableWidgetItem(title))
            # item = QTableWidgetItem(view)
            # item.setTextAlignment(Qt.AlignCenter)
            # self.videoTable.setItem(row, 2, item)
            # item = QTableWidgetItem(like)
            # item.setTextAlignment(Qt.AlignCenter)
            # self.videoTable.setItem(row, 3, item)
            # item = QTableWidgetItem(duration)
            # item.setTextAlignment(Qt.AlignCenter)
            # self.videoTable.setItem(row, 4, item)
            uploadTo = mainVideoTable.item(row, 7)
            if uploadTo:
                self.videoTable.setItem(
                    row, 5, QTableWidgetItem(uploadTo.text()))

        return True


class VideosTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Run',
                                        'Tiêu đề',
                                        'Lượt view',
                                        'Lượt like',
                                        'Duration',
                                        'Upload To',
                                        ])
        self.setStyleSheet("background:rgb(193, 193, 193);")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)

        self.setColumnWidth(0, 30)
        self.hideColumn(2)
        self.hideColumn(3)
        # self.setColumnWidth(5, 123)
        # self.setColumnWidth(6, 223)
        # self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.itemSelectionChanged.connect(self.on_select_row)

    def on_select_row(self):
        self.unique_arr = []
        selected_rows = [index.row() for index in self.selectedIndexes()]
        self.unique_arr = list(set(selected_rows))

    def contextMenuEvent(self, event):
        menu = QMenu()
        index = self.indexAt(event.pos())
        if index.isValid():
            if len(self.unique_arr) > 1:
                # Menu cho việc chọn nhiều dòng
                action1 = menu.addAction('Tick các video đã chọn')
                action2 = menu.addAction('Untick các video đã chọn')
                res = menu.exec_(event.globalPos())
                if res == action1:
                    for row in self.unique_arr:
                        _item_parent = self.cellWidget(row, 0)
                        _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                        if not _item_cb.isChecked():
                            _item_cb.setChecked(True)
                elif res == action2:
                    for row in self.unique_arr:
                        _item_parent = self.cellWidget(row, 0)
                        _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                        if _item_cb.isChecked():
                            _item_cb.setChecked(False)

        else:
            noAction = menu.addAction('Không có dòng nào được chọn')
            noAction.setText('Không có dòng nào được chọn')
            noAction.setEnabled(False)
            res = menu.exec_(event.globalPos())


class RoundedTimeEdit(QTimeEdit):
    def __init__(self, parent=None):
        super(RoundedTimeEdit, self).__init__(parent)
        self.setDisplayFormat("hh:mm")

        # Danh sách các giá trị phút hợp lệ
        self.valid_minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

        # Kết nối sự kiện editingFinished để làm tròn giá trị phút
        self.editingFinished.connect(self.round_minute)

    def round_minute(self):
        # Lấy giá trị phút hiện tại
        current_minute = self.time().minute()

        # Tìm giá trị phút gần nhất trong danh sách các giá trị phút hợp lệ
        nearest_minute = min(self.valid_minutes,
                             key=lambda x: abs(x - current_minute))

        # Thiết lập giá trị phút mới
        self.setTime(QTime(self.time().hour(), nearest_minute))
