import os
import sqlite3
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ui import ui_readUpdateVideoWindow
from core.HomeController import FacebookLogin, InstagramLogin, QTableWidgetItemCenter, XLogin, YoutubeLogin, getAssetsFacebookThread, getAssetsInstaThread, getAssetsXThread, getAssetsYotubeThread, pushNotification, pushQuestionWithThreeOptionsBeforeDelete, pushYNQuestion, startBrowserFromUore
from windows.AddUserWindow import EditUserWindow
from windows.BulkEditTitleWindow import BulkEditTitleWindow
from windows.PickUploadAccountWindow import PickUploadAccountWindow, PickerProfilesTableWidget


def startLogginThisAccount(index, table: QTableWidget):
    def updateStateAccount(indexSuccess):
        print(f"==>> indexSuccess: {indexSuccess}")
        table.setItem(
            indexSuccess, 2, QTableWidgetItemCenter('Đã đăng nhập'))

    uore = table.item(index, 1).text()
    platform = table.item(index, 3).text()
    if platform == 'Facebook':
        table.loginThread = FacebookLogin(index, uore)
    if platform == 'Youtube':

        table.loginThread = YoutubeLogin(index, uore)

        def handleLoginSuccess():
            ret = pushYNQuestion('Bạn đã login thành công chưa?')
            table.loginThread.theAnswer = ret
        table.loginThread.askLoginSuccess.connect(
            handleLoginSuccess)

    if platform == 'X-Twitter':
        table.loginThread = XLogin(index, uore)
    if platform == 'Instagram':
        table.loginThread = InstagramLogin(index, uore)
    table.loginThread.pushErrors.connect(pushNotification)
    table.loginThread.changeState.connect(updateStateAccount)
    table.loginThread.start()


def editThisAccountWindow(index, table: QTableWidget):
    uore = table.item(index, 1).text()
    table.editUserWindow = EditUserWindow(index, uore, table)
    table.editUserWindow.show()


def openTheAccount(index, table: QTableWidget):
    uore = table.item(index, 1).text()
    startBrowserFromUore(
        uore, 900, 600, 50, 100, True, 1)


def deleteTheAccount(index, table: QTableWidget, noti=True):
    print(f"==>> index: {index}")
    if noti:
        ret = pushYNQuestion('Bạn có chắc chắn muốn xoá profile này không?')
        if not ret:
            return
    uore = table.item(index, 1).text()
    print(f"==>> uore: {uore}")
    conn = sqlite3.connect('./data/database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM profiles WHERE uore=?", (uore,))
    rs = cursor.fetchone()
    idd = rs[0]
    cursor.execute(f"DELETE FROM profiles WHERE uore=?", (uore,))
    cursor.execute(f"DELETE FROM asset WHERE owner_id=?", (idd,))
    conn.commit()
    conn.close()
    table.removeRow(index)
    if noti:
        pushNotification('Xoá thành công')


def on_select_row(table: QTableWidget):
    table.unique_arr = []
    selected_rows = [index.row() for index in table.selectedIndexes()]
    table.unique_arr = list(set(selected_rows))


def on_clicked_row(row, table: QTableWidget, assetsTable: QTableWidget):
    uore = table.item(row, 1).text()

    conn = sqlite3.connect('./data/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
    recordprofile = cursor.fetchone()
    cursor.execute("SELECT * FROM asset WHERE owner_id = ?",
                   (recordprofile[0],))
    records = cursor.fetchall()
    conn.close()
    assetsTable.setRowCount(0)
    for record in records:
        pagename = record[1]
        row = assetsTable.rowCount()
        assetsTable.insertRow(row)
        assetsTable.setItem(
            row, 0, QTableWidgetItemCenter(pagename))


def getAssetsInstagram(index, table: QTableWidget, assetsTable: QTableWidget):
    uore = table.item(index, 1).text()

    def processAsset(data):

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        record = cursor.fetchone()
        ownerid = record[0]
        cursor.execute("SELECT * FROM asset WHERE owner_id = ?", (ownerid,))
        assets = cursor.fetchall()
        originalAsset = []
        for asset in assets:
            assetName = asset[1]
            originalAsset.append(assetName)
        for pagename in data:
            if pagename in originalAsset:
                print('cos r')
                continue
            sql_query = '''INSERT INTO asset(asset_name,owner_id) 
                VALUES (?, ?)'''
            cursor.execute(sql_query, (pagename, ownerid,))
            row = assetsTable.rowCount()
            assetsTable.insertRow(row)
            assetsTable.setItem(row, 0, QTableWidgetItemCenter(pagename))

        conn.commit()
        conn.close()

    table.getAsset = getAssetsInstaThread(index, uore)
    table.getAsset.start()
    table.getAsset.sendAsset.connect(processAsset)


def getAssetsXTwitter(index, table: QTableWidget, assetsTable: QTableWidget):
    uore = table.item(index, 1).text()

    def processAsset(data):

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        record = cursor.fetchone()
        ownerid = record[0]
        cursor.execute("SELECT * FROM asset WHERE owner_id = ?", (ownerid,))
        assets = cursor.fetchall()
        originalAsset = []
        for asset in assets:
            assetName = asset[1]
            originalAsset.append(assetName)
        for pagename in data:
            if pagename in originalAsset:
                print('cos r')
                continue
            sql_query = '''INSERT INTO asset(asset_name,owner_id) 
                VALUES (?, ?)'''
            cursor.execute(sql_query, (pagename, ownerid,))
            row = assetsTable.rowCount()
            assetsTable.insertRow(row)
            assetsTable.setItem(row, 0, QTableWidgetItemCenter(pagename))

        conn.commit()
        conn.close()

    table.getAsset = getAssetsXThread(index, uore)
    table.getAsset.start()
    table.getAsset.sendAsset.connect(processAsset)


def getAssetsYoutube(index, table: QTableWidget, assetsTable: QTableWidget):
    uore = table.item(index, 1).text()

    def processAsset(data):

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        record = cursor.fetchone()
        ownerid = record[0]
        cursor.execute("SELECT * FROM asset WHERE owner_id = ?", (ownerid,))
        assets = cursor.fetchall()
        originalAsset = []
        for asset in assets:
            assetName = asset[1]
            originalAsset.append(assetName)
        print(f"==>> originalAsset: {originalAsset}")
        for pagename in data:
            if pagename in originalAsset:
                print('cos r')
                continue
            sql_query = '''INSERT INTO asset(asset_name,owner_id) 
                VALUES (?, ?)'''
            cursor.execute(sql_query, (pagename, ownerid,))
            row = assetsTable.rowCount()
            assetsTable.insertRow(row)
            assetsTable.setItem(row, 0, QTableWidgetItemCenter(pagename))

        conn.commit()
        conn.close()

    table.getAsset = getAssetsYotubeThread(index, uore)
    table.getAsset.start()
    table.getAsset.sendAsset.connect(processAsset)


def getAssetsFacebook(index, table: QTableWidget, assetsTable: QTableWidget):
    uore = table.item(index, 1).text()

    def processAsset(data):

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        record = cursor.fetchone()
        ownerid = record[0]
        cursor.execute("SELECT * FROM asset WHERE owner_id = ?", (ownerid,))
        assets = cursor.fetchall()
        originalAsset = []
        for asset in assets:
            assetName = asset[1]
            originalAsset.append(assetName)
        for pagename in data:
            if pagename in originalAsset:
                print('cos r')
                continue
            sql_query = '''INSERT INTO asset(asset_name,owner_id) 
                VALUES (?, ?)'''
            cursor.execute(sql_query, (pagename, ownerid,))
            row = assetsTable.rowCount()
            assetsTable.insertRow(row)
            assetsTable.setItem(row, 0, QTableWidgetItemCenter(pagename))

        conn.commit()
        conn.close()

    table.getAsset = getAssetsFacebookThread(index, uore)
    table.getAsset.start()
    table.getAsset.sendAsset.connect(processAsset)


def openEditBulkAccount(table: QTableWidget):
    table.ebaWindow = BulkEditTitleWindow(table)
    table.ebaWindow.show()


def customMenu(event, table: QTableWidget, assetsTable: QTableWidget):
    menu = QMenu()
    index = table.indexAt(event.pos())

    if index.isValid() and len(table.unique_arr) == 1:
        # Menu cho việc chọn 1 dòng
        editThisAccount = menu.addAction('Sửa tài khoản này')
        openBrowserThisAccount = menu.addAction('Mở trình duyệt tài khoản này')
        loginThisAccount = menu.addAction('Đăng nhập tài khoản này')
        platform = table.item(index.row(), 3).text()
        if platform == 'Facebook':
            getAssetsFb = menu.addAction('Scan và lấy tài sản(page) nick này')
        if platform == 'Youtube':
            getAssetsYt = menu.addAction('Scan và lấy tài sản(kênh) nick này')
        if platform == 'X-Twitter':
            getAssetsX = menu.addAction('Scan và lấy tài sản(kênh X) nick này')
        if platform == 'Instagram':
            getAssetsInst = menu.addAction(
                'Scan và lấy tài sản(kênh Instagram) nick này')
        deleteThisAccount = menu.addAction('Xoá tài khoản này')

        res = menu.exec_(event.globalPos())
        if res == loginThisAccount:
            startLogginThisAccount(index.row(), table)
        elif res == editThisAccount:
            editThisAccountWindow(index.row(), table)
        elif res == deleteThisAccount:
            deleteTheAccount(index.row(), table)
        elif res == openBrowserThisAccount:
            openTheAccount(index.row(), table)
        try:
            if res == getAssetsFb:
                getAssetsFacebook(index.row(), table, assetsTable)
        except:
            pass
        try:

            if res == getAssetsYt:
                getAssetsYoutube(index.row(), table, assetsTable)
        except:
            pass

        try:

            if res == getAssetsX:
                getAssetsXTwitter(index.row(), table, assetsTable)
        except:
            pass

        try:

            if res == getAssetsInst:
                getAssetsInstagram(index.row(), table, assetsTable)
        except:
            pass

    elif index.isValid() and len(table.unique_arr) > 1:

        deleteBulkAccounts = menu.addAction('Xoá loạt tài khoản này')
        res = menu.exec_(event.globalPos())
        if res == deleteBulkAccounts:
            ret = pushYNQuestion('Bạn có chắc chắn muốn xoá không?')
            if not ret:
                return
            for index in reversed(sorted(table.unique_arr)):
                deleteTheAccount(index, table, False)


def setUpProfilesTable(table: QTableWidget, assetsTable: QTableWidget):
    table.itemSelectionChanged.connect(lambda: on_select_row(table))

    table.cellClicked.connect(
        lambda row: on_clicked_row(row, table, assetsTable))
    table.contextMenuEvent = lambda event: customMenu(
        event, table, assetsTable)
# ===========================================================================================


def editThisVideo(index, table: QTableWidget):

    class ReadUpdateVideoWindow(QMainWindow):
        def __init__(self):
            super(ReadUpdateVideoWindow, self).__init__()
            self.ui = ui_readUpdateVideoWindow.Ui_MainWindow()
            self.ui.setupUi(self)
            self.ui.titleLine.setText(table.item(index, 0).text())
            self.ui.description.setPlainText(table.item(index, 1).text())
            self.ui.tags.setPlainText(table.item(index, 2).text())
            self.ui.saveChanges.clicked.connect(self.saveChanges)

        def saveChanges(self):
            title = self.ui.titleLine.text()
            des = self.ui.description.toPlainText()
            tags = self.ui.tags.toPlainText()
            table.setItem(index, 0, QTableWidgetItemCenter(title))
            table.setItem(index, 1, QTableWidgetItemCenter(des))
            table.setItem(index, 2, QTableWidgetItemCenter(tags))
            self.close()

    table.editWindow = ReadUpdateVideoWindow()
    table.editWindow.show()


def editBulkInfoVideo(table: QTableWidget):
    table.editWindow = BulkEditTitleWindow(table)
    table.editWindow.show()


def bulkPickAccountAction(table: QTableWidget):
    pass


def chooseUploadTo(table: QTableWidget, profilesTable, index, multipleRow=None):
    table.pickWindow = PickUploadAccountWindow(
        table, profilesTable, index, multipleRow)
    table.pickWindow.tableWidget = PickerProfilesTableWidget()
    table.pickWindow.tableWidget.setObjectName("pickAccountTableWidget")
    table.pickWindow.ui.verticalLayoutForTable.addWidget(
        table.pickWindow.tableWidget)
    table.pickWindow.loadProfilesToTable()

    # table.pickWindow.ui.loadProfilesToTable(project_id)
    # table.pickWindow.ui.tableWidget.cellDoubleClicked.connect(
    #     table.on_click_item)
    table.pickWindow.show()


def deleteTheRow(index, table: QTableWidget, changePrivacyOfThisRow):
    def deleteThisRow():
        file = table.item(index, 8)
        if file != None and file.text() != "":

            try:
                os.remove(file.text())
            except:
                pass

        table.removeRow(index)

    ret = pushQuestionWithThreeOptionsBeforeDelete()
    if ret == 'Yes':
        deleteThisRow()
    elif ret == 'No':
        table.removeRow(index)

    for row in range(0, table.rowCount()):
        dropdownPrivacy = table.cellWidget(row, 4)
        dropdownPrivacy.currentIndexChanged.disconnect()
        dropdownPrivacy.currentIndexChanged.connect(
            lambda selected_index, row=row: changePrivacyOfThisRow(row, selected_index))


def customMenuVideos(event, table: QTableWidget, profilesTable: QTableWidget, changePrivacyOfThisRow):
    menu = QMenu()
    index = table.indexAt(event.pos())

    if index.isValid() and len(table.unique_arr) == 1:
        # Menu cho việc chọn 1 dòng
        editThisRow = menu.addAction('Sửa dòng này')
        chooseUploadAccount = menu.addAction('Chọn tài khoản upload')

        # openFile = menu.addAction('Mở file')
        deleteThisRow = menu.addAction('Xoá dòng này')

        res = menu.exec_(event.globalPos())
        if res == editThisRow:
            editThisVideo(index.row(), table)
        elif res == chooseUploadAccount:
            chooseUploadTo(table, profilesTable, index.row())
        # elif res == openFile:
        #     video
        #     openTheAccount(index.row(), table)
        elif res == deleteThisRow:
            deleteTheRow(index.row(), table, changePrivacyOfThisRow)

    elif index.isValid() and len(table.unique_arr) > 1:
        Bulk_EditAction = menu.addAction(
            'Sửa thông tin hàng loạt cho các video này')
        Bulk_pickAccountAction = menu.addAction(
            'Chọn tài khoản Upload cho các video này')

        res = menu.exec_(event.globalPos())
        if res == Bulk_EditAction:
            editBulkInfoVideo(table)
        elif res == Bulk_pickAccountAction:
            chooseUploadTo(table, profilesTable, None, table.unique_arr)


def setUpVideosTable(table: QTableWidget, profilesTable: QTableWidget, changePrivacyOfThisRow):
    table.itemSelectionChanged.connect(lambda: on_select_row(table))

    table.contextMenuEvent = lambda event: customMenuVideos(
        event, table, profilesTable, changePrivacyOfThisRow)

# ===========================================================================================


def setUpAssetsTable(table: QTableWidget):
    pass
