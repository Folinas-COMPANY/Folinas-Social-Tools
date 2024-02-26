import sqlite3
from core.HomeController import pushNotification
from ui import ui_PickUploadAccountWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class PickerProfilesTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(
            ['Run', 'Tên tài sản', 'Tài khoản sở hữu', 'Platform'])
        self.setStyleSheet("""
            
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
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setColumnWidth(0, 30)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.itemSelectionChanged.connect(self.on_select_row)

        self.unique_arr = []

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
                action1 = menu.addAction('Tick các profile đã chọn')
                action2 = menu.addAction('Untick các profile đã chọn')
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


class PickUploadAccountWindow(QMainWindow):
    def __init__(self, table, profilesTable, oneRow, multipleRow):
        super(PickUploadAccountWindow, self).__init__()
        self.bigMainTable = table
        self.ui = ui_PickUploadAccountWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        # self.move(mainWd.window.x()+50, mainWd.window.y()+100)

        self.ui.tickAllBtn.clicked.connect(self.tickAll)
        self.ui.untickAllBtn.clicked.connect(self.unTickAll)
        self.ui.doIt.clicked.connect(self.saveChanges)
        self.ui.clearAllUploader.clicked.connect(self.clearUploader)

        self.tableWidget = None

        self.oneRow = oneRow
        self.multipleRow = multipleRow
        # self.updateAllOneRow = updateAllOneRow

        text = ''
        if self.oneRow != None and self.multipleRow == None:
            self.ui.whichIndex.setText(str(int(oneRow)+1))
        elif self.oneRow == None and self.multipleRow != None:
            self.multipleRow.sort()
            for indexText in self.multipleRow:
                item = str(int(indexText) + 1)
                text = text+item+','
            text = text[:-1]
            self.ui.whichIndex.setText(text)

    def clearUploader(self):

        for row in range(self.bigMainTable.rowCount()):
            self.bigMainTable.setItem(row, 7, QTableWidgetItem())

    def saveChanges(self):

        if self.oneRow != None and self.multipleRow == None:
            arr = []
            for row in range(0, self.tableWidget.rowCount()):
                _item_parent = self.tableWidget.cellWidget(row, 0)
                _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                if not _item_cb.isChecked():
                    continue

                _item_asset = self.tableWidget.item(row, 1)
                _item_platform = self.tableWidget.item(row, 3).text()
                if _item_platform == 'Facebook':
                    arr.append(f'{_item_asset.text()}*FB')
                elif _item_platform == 'Youtube':
                    arr.append(f'{_item_asset.text()}*YT')
                elif _item_platform == 'X-Twitter':
                    arr.append(f'{_item_asset.text()}*X')
                elif _item_platform == 'Instagram':
                    arr.append(f'{_item_asset.text()}*IST')

            if len(arr) == 0:
                self.bigMainTable.setItem(
                    self.oneRow, 7, QTableWidgetItem(""))
            else:
                separator = ','  # Ký tự phân tách mỗi phần tử
                result = '[' + separator.join(str(x) for x in arr) + ']'
                self.bigMainTable.setItem(
                    self.oneRow, 7, QTableWidgetItem(result))

        elif self.oneRow == None and self.multipleRow != None:

            for index in self.multipleRow:

                arr = []
                for row in range(0, self.tableWidget.rowCount()):
                    _item_parent = self.tableWidget.cellWidget(row, 0)
                    _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
                    if not _item_cb.isChecked():
                        continue
                    _item_asset = self.tableWidget.item(row, 1)
                    _item_platform = self.tableWidget.item(row, 3).text()
                    if _item_platform == 'Facebook':
                        arr.append(f'{_item_asset.text()}*FB')
                    elif _item_platform == 'Youtube':
                        arr.append(f'{_item_asset.text()}*YT')
                    elif _item_platform == 'X-Twitter':
                        arr.append(f'{_item_asset.text()}*X')
                    elif _item_platform == 'Instagram':
                        arr.append(f'{_item_asset.text()}*IST')

                separator = ','  # Ký tự phân tách mỗi phần tử
                result = '[' + separator.join(str(x) for x in arr) + ']'
                print(f"==>> result: {result}")
                if len(arr) == 0:
                    self.bigMainTable.setItem(
                        index, 7, QTableWidgetItem(""))
                else:
                    self.bigMainTable.setItem(
                        index, 7, QTableWidgetItem(result))

        self.close()

    def tickAll(self):
        for row in range(0, self.tableWidget.rowCount()):
            _item_parent = self.tableWidget.cellWidget(row, 0)
            _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
            if not _item_cb.isChecked():
                _item_cb.setChecked(True)

    def unTickAll(self):
        for row in range(0, self.tableWidget.rowCount()):
            _item_parent = self.tableWidget.cellWidget(row, 0)
            _item_cb = _item_parent.findChild(QCheckBox, "cbToRun")
            if _item_cb.isChecked():
                _item_cb.setChecked(False)

    def loadProfilesToTable(self):
        data = {
            1: 'Facebook',
            2: 'Youtube',
            3: 'X-Twitter',
            4: 'Instagram',
        }
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        # Thực hiện truy vấn để lấy tất cả các bản ghi trong bảng profilesTable
        sql_query = "SELECT * FROM profiles"
        cursor.execute(sql_query)

        # Lấy tất cả các bản ghi và lưu chúng vào một danh sách (list)
        records = cursor.fetchall()

        self.tableWidget.setRowCount(0)
        # In ra các bản ghi
        for i, record in enumerate(records):
            checkbox = QCheckBox()
            checkbox.setObjectName("cbToRun")
            # checkbox.setChecked(True)
            checkbox_h_box = QHBoxLayout()
            checkbox_h_box.addWidget(checkbox, 0, Qt.AlignCenter)
            checkbox_widget = QWidget()
            checkbox_widget.setLayout(checkbox_h_box)
            profileName = record[1]

            state = record[6]
            if state != '1':
                continue
            platform = record[5]

            cursor.execute("SELECT * FROM asset WHERE owner_id = ?",
                           (record[0],))

            theAssets = cursor.fetchall()

            for asset in theAssets:
                checkbox = QCheckBox()
                checkbox.setObjectName("cbToRun")
                # checkbox.setChecked(True)
                checkbox_h_box = QHBoxLayout()
                checkbox_h_box.addWidget(checkbox, 0, Qt.AlignCenter)
                checkbox_widget = QWidget()
                checkbox_widget.setLayout(checkbox_h_box)
                # Lấy tất cả các bản ghi và lưu chúng vào một danh sách (list)
                num = self.tableWidget.rowCount()
                self.tableWidget.insertRow(num)
                self.tableWidget.setCellWidget(
                    num, 0, checkbox_widget)

                self.tableWidget.setItem(
                    num, 1, QTableWidgetItem(asset[1]))
                self.tableWidget.setItem(
                    num, 2, QTableWidgetItem(profileName))
                self.tableWidget.setItem(
                    num, 3, QTableWidgetItem(data[platform]))

        conn.close()
