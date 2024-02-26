
import sqlite3
import traceback
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from core.HomeController import QTableWidgetItemCenter, pushNotification


from ui import ui_addUserWindow


class AddUserWindow(QMainWindow):
    def __init__(self, typeAdd, loadProfilesToTableFunc):
        super(AddUserWindow, self).__init__()
        self.ui = ui_addUserWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadProfilesToTableFunc = loadProfilesToTableFunc
        if typeAdd == 'Facebook':
            self.ui.labelImg.setPixmap(QPixmap(":/images/facebook.jpg"))
            self.typeAdd = 1
        if typeAdd == 'Youtube':
            self.ui.labelImg.setPixmap(QPixmap(":/images/youtube.jpg"))
            self.typeAdd = 2
        if typeAdd == 'X - Twitter':
            self.ui.labelImg.setPixmap(QPixmap(":/images/X.jpg"))
            self.typeAdd = 3
        if typeAdd == 'Instagram':
            self.ui.labelImg.setPixmap(QPixmap(":/images/instagram.jpg"))
            self.typeAdd = 4

        self.ui.addToDb.clicked.connect(self.startAddingToDB)

    def startAddingToDB(self):
        profileName = self.ui.profileName.text()
        if profileName == '':
            pushNotification('Bạn cần nhập tên Username')
            return

        uore = self.ui.uore.text()
        if uore == '':
            pushNotification('Bạn cần nhập email hoặc username')
            return
        password = self.ui.password.text()
        if password == '':
            pushNotification('Bạn cần nhập mật khẩu')
            return
        cookie = self.ui.cookie.toPlainText()
        proxy = self.ui.proxy.text()
        facode = self.ui.facode.text()
        if self.ui.http.isChecked():
            proxyMode = 'http'
        if self.ui.socks5.isChecked():
            proxyMode = 'socks5'

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        sql_query = '''INSERT INTO profiles(profile_name,uore,password,cookie,platform_id,proxy,proxy_mode,facode) 
               VALUES (?, ?, ?, ?, ?, ? , ?,?)'''
        try:
            cursor.execute(sql_query, (profileName, uore,
                                       password, cookie, self.typeAdd, proxy, proxyMode, facode))
            conn.commit()
        except:
            pushNotification(traceback.format_exc())
            conn.close()
            return
        conn.close()
        self.loadProfilesToTableFunc()
        pushNotification('Thêm thành công!')
        self.close()


class EditUserWindow(QMainWindow):
    def __init__(self, index, uore, table: QTableWidget):
        super(EditUserWindow, self).__init__()
        self.ui = ui_addUserWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.addToDb.setText('Lưu thay đổi')
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        result = cursor.fetchone()
        typeAdd = result[5]
        profileName = result[1]
        password = result[3]
        cookie = result[4]
        self.olduore = uore
        self.table = table
        self.index = index
        proxy = result[7]
        proxyMode = result[8]
        facode = result[10]

        self.ui.profileName.setText(profileName)
        self.ui.uore.setText(uore)
        self.ui.password.setText(password)
        self.ui.cookie.setPlainText(cookie)
        self.ui.proxy.setText(proxy)
        self.ui.facode.setText(facode)
        if proxyMode == 'http':
            self.ui.http.setChecked(True)

        if proxyMode == 'socks5':
            self.ui.socks5.setChecked(True)

        if typeAdd == 1:
            self.ui.labelImg.setPixmap(QPixmap(":/images/facebook.jpg"))
            self.typeAdd = 1
        if typeAdd == 2:
            self.ui.labelImg.setPixmap(QPixmap(":/images/youtube.jpg"))
            self.typeAdd = 2
        if typeAdd == 3:
            self.ui.labelImg.setPixmap(QPixmap(":/images/X.jpg"))
            self.typeAdd = 3
        if typeAdd == 4:
            self.ui.labelImg.setPixmap(QPixmap(":/images/instagram.jpg"))
            self.typeAdd = 4

        self.ui.addToDb.clicked.connect(self.saveChanges)

    def saveChanges(self):
        profileName = self.ui.profileName.text()
        if profileName == '':
            pushNotification('Bạn cần nhập tên Username')
            return

        uore = self.ui.uore.text()
        if uore == '':
            pushNotification('Bạn cần nhập email hoặc username')
            return
        password = self.ui.password.text()
        if password == '':
            pushNotification('Bạn cần nhập mật khẩu')
            return
        cookie = self.ui.cookie.toPlainText()
        proxy = self.ui.proxy.text()
        facode = self.ui.facode.text()
        if self.ui.http.isChecked():
            proxyMode = 'http'
        if self.ui.socks5.isChecked():
            proxyMode = 'socks5'

        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        sql_query = '''UPDATE profiles 
                SET profile_name = ?, password = ?, cookie = ?, proxy = ?, proxy_mode = ?, facode = ?, uore = ? WHERE uore = ?'''

        try:
            cursor.execute(sql_query, (profileName, password,
                           cookie, proxy, proxyMode, facode, uore, self.olduore))
            conn.commit()
        except:

            pushNotification(traceback.format_exc())
            conn.close()
            return
        conn.close()
        self.table.setItem(self.index, 0, QTableWidgetItemCenter(profileName))
        self.table.setItem(self.index, 1, QTableWidgetItemCenter(uore))
        self.table.setItem(self.index, 4, QTableWidgetItemCenter(proxy))

        pushNotification('Sửa thành công!')
        self.close()
