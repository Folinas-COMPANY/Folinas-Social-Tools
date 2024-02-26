import json
from pathlib import Path
import re
import sqlite3
import threading
import traceback
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import psutil
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from core.ControlBrowser import createBrowser, openBrowser, updateBrowserFingerprint
from core.SeleniumFunctions import BrowserFunctions
from time import sleep
from threading import Condition


class StaffUpload(QThread):
    update_ERRORS_signal = pyqtSignal(str)
    update_hwndBrowser_signal = pyqtSignal(int, tuple)
    update_slashState_signal = pyqtSignal(int, str)
    update_colorPublic_signal = pyqtSignal(int, int)
    update_colorDone_signal = pyqtSignal(int, int)
    update_colorFailFile_signal = pyqtSignal(int, int)
    update_killBrowser_signal = pyqtSignal(int, BrowserFunctions)
    update_toggle_signal = pyqtSignal(bool, int)
    clear_cell_signal = pyqtSignal(int)

    def __init__(self, indexVideos, assetName, indexAsset, browsersInQueue, videosTable: QTableWidget):
        super().__init__()
        print(f"==>> assetName: {assetName}")
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM asset WHERE asset_name = ?", (assetName,))
        record = cursor.fetchone()
        ownerid = record[2]
        cursor.execute(
            "SELECT * FROM profiles WHERE ID = ?", (ownerid,))
        record = cursor.fetchone()
        conn.close()
        self.username = record[2]
        self.id_profile = record[9]
        self.platform = record[5]
        self.index = indexAsset
        self.assetName = assetName
        self.indexVideos = indexVideos
        self.browsersInQueue = browsersInQueue
        self.videosTable = videosTable
        self.isForceStop = False
        self.cond = Condition()

    def run(self):
        # self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        while not self.isForceStop:
            self.browsersInQueue[self.id_profile] = 'opening'

            driver = startBrowserFromUore(
                self.username, 900, 600, 50, 100, True, 0.5)
            if isinstance(driver, str):
                self.error = True
                self.errorString = driver
                return
            process = driver.browser_pid
            self.browsersInQueue[self.id_profile] = driver.browser_pid
            self.update_hwndBrowser_signal.emit(
                process, (self.index, self.assetName))

            self.browserId = driver.browser_pid
            self.update_slashState_signal.emit(self.index,
                                               f'Khởi tạo trình duyệt thành công..')
            browser = BrowserFunctions(driver)

            if self.platform == 1:
                self.uploadFacebook(browser)

            if self.platform == 2:
                self.uploadYoutube(browser)

            if self.platform == 3:
                self.uploadTwitter(browser)

            if self.platform == 4:
                self.uploadInstagram(browser)

            # with self.cond:
            #     self.cond.wait(15)

            break
        print('dừng rồi')

    def getInfoVideoFromTable(self, indexVideo):
        try:
            title = self.videosTable.item(indexVideo, 0).text()
        except:
            title = ''
        try:
            des = self.videosTable.item(indexVideo, 1).text()
        except:
            des = ''

        try:
            tags = self.videosTable.item(indexVideo, 2).text()
        except:
            tags = ''
        try:
            schedule_time = []
            date_time = self.videosTable.cellWidget(indexVideo, 5)
            date_s = date_time.date()
            time_s = date_time.time()
            year = date_s.year()
            month = date_s.month()
            day = date_s.day()
            hour = time_s.hour()
            minute = time_s.minute()
            schedule_time.append(
                f'{month}/{day}/{year}')
            if self.platform == 1:
                schedule_time.append(
                    self.convertHours(hour, minute))

            if self.platform == 3:
                schedule_time.append(
                    self.convertHoursTwitter(hour, minute))

            if self.platform == 2:
                schedule_time.append([hour, minute])

        except:
            schedule_time = None
        video_path = self.videosTable.item(indexVideo, 8).text()
        return title, des, tags, schedule_time, video_path

    def convertHoursTwitter(self, hour, minute):
        a_or_p = 'AM'
        if hour >= 12:
            hour = hour - 12
            a_or_p = 'PM'
        if hour < 10:
            hour = f'{hour}'
        if minute < 10:
            minute = f'0{minute}'
        return [hour, minute, a_or_p]

    def convertHours(self, hour, minute):
        a_or_p = 'A'
        if hour >= 12:
            hour = hour - 12
            a_or_p = 'P'
        if hour < 10:
            hour = f'0{hour}'
        if minute < 10:
            minute = f'0{minute}'
        return [hour, minute, a_or_p]

    def __videosFacebook(self, browser: BrowserFunctions, indexVideo):
        asset_id = self.get_asset_id(browser.driver.current_url)
        if asset_id:
            browser.get(
                f"https://business.facebook.com/latest/composer?asset_id={asset_id}")
        else:
            create = browser.find(
                By.XPATH, "//div[contains(text(), 'Create post')]")
            create.click()

        browser.driver.execute_script("""
            (function() {
                var oldCreate = document.createElement;

                var create = function(type) {
                    if (type == 'input') {
                        console.log("Creating: " + type);
                        elem = oldCreate.call(document, type);
                        
                        elem.dataset.friend = 'new'
                        
                        document.body.appendChild(elem)
                        return elem
                    }
                    return oldCreate.call(document, type);
                }  
                document.createElement = create;
            }());
            """)

        inp: WebElement = browser.find(
            By.XPATH, '//input[@data-friend="new" and @accept="video/*" and @type="file"]', timeout=5)

        if not inp:
            self.update_slashState_signal.emit(self.index,
                                               f'EJ thất bại, đang thử upload lại.')
            return False
        data = self.getInfoVideoFromTable(indexVideo)
        videoPath = data[4]
        self.update_slashState_signal.emit(self.index,
                                           f'Bắt đầu tải video lên..')
        self.wait(2)
        inp.send_keys(videoPath)

        addParent = browser.find(
            By.XPATH, '//div[@aria-label="Select adding a video."]')
        addParent.click()
        self.wait(2)
        user_thread = threading.Thread(
            target=self.listenToTheDialogOnceNew, args=(False,))
        user_thread.start()
        addBtn = browser.find(
            By.XPATH, '//div[@data-testid="ContextualLayerRoot"]/div/div/div/div[1]/div/div/div[1]')
        addBtn.click()
        user_thread.join()

        threedot = '.'
        while True:
            uploadSection = browser.find(
                By.XPATH, "//div[@data-pagelet='BusinessComposerFullScreenPostPreview']//div[@role='article' and @aria-posinset='0']", timeout=1)
            if uploadSection:
                self.update_slashState_signal.emit(self.index, 'Upload xong..')
                break
            else:
                self.update_slashState_signal.emit(self.index,
                                                   f'Đang upload{threedot}')
                threedot += threedot
                if threedot == '....':
                    threedot = '.'
                self.wait(1)

        # upThumb = False
        # if upThumb:
        #     print('tìm và click vfo nút thumb')
        #     btn = browser.find(
        #         By.XPATH, "//div[contains(text(), 'Upload image')]")
        #     if btn:
        #         browser.scrollToElement(btn)
        #         btn.click()
        #         self.wait(1)
        #         inp: WebElement = self.browser.find(
        #             By.CSS_SELECTOR, 'input[data-friend="new"][type="file"][accept="image/*"]', timeout=10)
        #         inp.send_keys(r'')
        #         self.wait(1000)
        #     else:
        #         print('không tìm thấy nó thôi bỏ qua')
        #         pass
        self.update_slashState_signal.emit(self.index,
                                           f'Tìm phần điền mô tả..')
        print('tìm phần điền mô tả')
        descPlain = browser.find(
            By.XPATH, "//div[@contenteditable='true']")
        if not descPlain:
            self.update_slashState_signal.emit(self.index,
                                               f'Không tìm thấy phần điền mô tả ở profile, đang thử upload lại..')
            return False
        print('điền nội dung vào mô tả')
        browser.scrollToElement(descPlain)
        self.wait(1)
        browser.forceClick(descPlain)
        self.wait(2)
        desc = data[1]
        self.paste_content(browser.driver, descPlain, desc)
        self.wait(3)

        schedule_time = data[3]
        # neu video dang len lich
        if schedule_time != None:
            schedule_switch = browser.find(
                By.XPATH, '//input[@aria-label="Set date and time" and @role="switch"]')
            isChecked = schedule_switch.get_attribute('aria-checked')
            if isChecked != 'true':
                schedule_switch.click()
                self.wait(2)
            schedule_day = schedule_time[0]
            schedule_time_at = schedule_time[1]
            h = schedule_time_at[0]
            m = schedule_time_at[1]
            aorp = schedule_time_at[2]

            desired1 = 'mm/dd/yyyy'
            desired2 = 'dd/mm/yyyy'
            inputDay1 = browser.find(
                By.XPATH, f"//input[@placeholder='{desired1}']")
            if not inputDay1:
                inputDay2 = browser.find(
                    By.XPATH, f"//input[@placeholder='{desired2}']")
                if not inputDay2:
                    self.update_slashState_signal.emit(self.index,
                                                       f'Không tìm được nút inputDay ở profile, đang thử upload lại..')
                    return False
                schedule_day_split = schedule_day.split('/')
                schedule_day = f'{schedule_day_split[1]}/{schedule_day_split[0]}/{schedule_day_split[2]}'
                inputDay = inputDay2
            else:
                inputDay = inputDay1

            self.update_slashState_signal.emit(self.index,
                                               f'Bắt đầu điền ngày..')
            # overlay = self.browser.find(By.XPATH,"//div[@class='xh8yej3']//div[@class='x78zum5 xdt5ytf x1iyjqo2']/div/div/div[2]",timeout=5)
            # if overlay:
            #     self.browser.driver.execute_script("""var element = arguments[0]; element.parentNode.removeChild(element);""", overlay)
            #     print('đã xoá phần tử overlay')
            print('click truờng nhập date')
            # inputDay.click()
            browser.forceClick(inputDay)
            self.wait(2)
            inputDay.send_keys(Keys.CONTROL+'a')
            self.wait(2)
            inputDay.send_keys(schedule_day)
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Đã điền xong phần ngày tháng, tìm khối giờ..')

            hourBtn = browser.find(
                By.XPATH, "//input[@aria-label='hours' and @role='spinbutton']")
            minutesBtn = browser.find(
                By.XPATH, "//input[@aria-label='minutes' and @role='spinbutton']")
            meridiemBtn = browser.find(
                By.XPATH, "//input[@aria-label='meridiem' and @role='spinbutton']")
            if not hourBtn or not minutesBtn or not meridiemBtn:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm thấy đủ nút cần thiết khi lên lịch ở profile, đang thử upload lại...')
                return False

            print('điền tiếp phần giờ')
            browser.forceClick(hourBtn)
            self.wait(2)
            hourBtn.send_keys(h)
            self.wait(2)

            print('điền tiếp phần phút')
            browser.forceClick(minutesBtn)
            self.wait(2)
            minutesBtn.send_keys(m)
            self.wait(2)

            print('đièn tiếp phần buổi')
            browser.forceClick(meridiemBtn)
            self.wait(2)
            meridiemBtn.send_keys(aorp)
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Đã điền xong , lên lịch video..')
            print('thành công task điền')
            print('lên lịch video')
            self.wait(2)
            while True:
                hbtn = browser.find(
                    By.XPATH, """//div[@data-pagelet="BusinessComposerNonVideoFooterCard"]//div[contains(text(), 'Schedule')]/ancestor::div[@aria-busy='false']""")
                try:
                    rs = hbtn.get_attribute('aria-disabled')
                    if rs != 'true':
                        break
                    else:
                        print('đợi hoàn thành')
                        self.wait(2)
                except:
                    break
            browser.scrollToElement(hbtn)
            self.wait(1)
            hbtn.click()
            self.wait(2)
            print('Đăng thành công!!')

        else:
            self.wait(2)
            publicBtn = browser.find(
                By.XPATH, """//div[@data-pagelet="BusinessComposerNonVideoFooterCard"]//div[contains(text(), 'Publish')]""", timeout=5)
            if not publicBtn:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm được nút publicBtn ở profile, đang thử upload lại.')

                return False
            print('chọn đăng ngay')
            browser.scrollToElement(publicBtn)
            self.wait(1)
            publicBtn.click()
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Bắt đầu công khai video..')

            # self.wait(2)
            # while True:
            #     hbtn = browser.find(
            #         By.XPATH, "//div[@class='x3nfvp2 x193iq5w xxymvpz' and @role='none']//div[contains(text(), 'Share')]/ancestor::div[@aria-busy='false']")
            #     try:
            #         rs = hbtn.get_attribute('aria-disabled')
            #         if rs != 'true':
            #             break
            #         else:
            #             print('đợi hoàn thành')
            #             self.wait(2)
            #     except:
            #         break
            # print('bấm đăng')
            # browser.scrollToElement(hbtn)
            # self.wait(1)
            # hbtn.click()
            self.wait(9)
            print('Đăng thành công!!')

        self.update_slashState_signal.emit(self.index,
                                           f'Đăng thành công video..')
        self.update_colorDone_signal.emit(indexVideo, self.index)
        return True

    def __reelsFacebook(self, browser: BrowserFunctions, indexVideo):
        # post reels functions
        asset_id = self.get_asset_id(browser.driver.current_url)
        if asset_id:
            browser.get(
                f"https://business.facebook.com/latest/reels_composer?asset_id={asset_id}")
        else:
            create = browser.find(
                By.XPATH, "//div[contains(text(), 'Create reel')]")
            create.click()

        browser.driver.execute_script("""
            (function() {
                var oldCreate = document.createElement;

                var create = function(type) {
                    if (type == 'input') {
                        console.log("Creating: " + type);
                        elem = oldCreate.call(document, type);
                        
                        elem.dataset.friend = 'new'
                        
                        document.body.appendChild(elem)
                        return elem
                    }
                    return oldCreate.call(document, type);
                }  
                document.createElement = create;
            }());
            """)

        inp: WebElement = browser.find(
            By.XPATH, '//input[@data-friend="new" and @accept="video/*, video/x-m4v, video/webm, video/x-ms-wmv, video/x-msvideo, video/3gpp, video/flv, video/x-flv, video/mp4, video/quicktime, video/mpeg, video/ogv, .ts, .mkv" and @type="file"]', timeout=5)

        if not inp:
            self.update_slashState_signal.emit(self.index,
                                               f'EJ thất bại, đang thử upload lại.')
            return False
        data = self.getInfoVideoFromTable(indexVideo)
        videoPath = data[4]
        self.update_slashState_signal.emit(self.index,
                                           f'Bắt đầu tải video lên..')
        inp.send_keys(videoPath)
        print('bắt đầu tải video lên')
        self.wait(2)
        uploadSection = browser.find(
            By.XPATH, "//div[@role='progressbar']", timeout=12)
        if not uploadSection:
            self.update_slashState_signal.emit(self.index,
                                               f'Không tìm thấy khối tải lên, đang thử upload lại...')
            return False

        threedot = '.'
        while True:
            percent = browser.find(
                By.XPATH, "//span[@class='xmi5d70 xw23nyj xo1l8bm x63nzvj xbsr9hj xq9mrsl x1h4wwuj xeuugli xsgj6o6']")
            if percent != None and percent.text == '100%':
                self.update_slashState_signal.emit(self.index, 'Upload xong..')
                break
            elif percent is None:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm thấy khối % tải lên, đang thử upload lại..')
                return False
            else:
                self.update_slashState_signal.emit(self.index,
                                                   f'Đang upload{threedot}')
                threedot += threedot
                if threedot == '....':
                    threedot = '.'
                self.wait(1)

        # upThumb = False
        # if upThumb:
        #     print('tìm và click vfo nút thumb')
        #     btn = browser.find(
        #         By.XPATH, "//div[contains(text(), 'Upload image')]")
        #     if btn:
        #         browser.scrollToElement(btn)
        #         btn.click()
        #         self.wait(1)
        #         inp: WebElement = self.browser.find(
        #             By.CSS_SELECTOR, 'input[data-friend="new"][type="file"][accept="image/*"]', timeout=10)
        #         inp.send_keys(r'')
        #         self.wait(1000)
        #     else:
        #         print('không tìm thấy nó thôi bỏ qua')
        #         pass
        self.update_slashState_signal.emit(self.index,
                                           f'Tìm phần điền mô tả..')
        print('tìm phần điền mô tả')
        descPlain = browser.find(
            By.XPATH, "//div[@contenteditable='true']")
        if not descPlain:
            self.update_slashState_signal.emit(self.index,
                                               f'Không tìm thấy phần điền mô tả ở profile, đang thử upload lại..')
            return False
        print('điền nội dung vào mô tả')
        browser.scrollToElement(descPlain)
        self.wait(1)
        browser.forceClick(descPlain)
        self.wait(2)
        desc = data[1]
        self.paste_content(browser.driver, descPlain, desc)
        self.wait(3)
        self.update_slashState_signal.emit(self.index,
                                           f'Tìm các nút options..')
        print('tìm các nút options')
        options = browser.find_all(
            By.XPATH, "//div[@class='x3ct3a4 x1n2onr6 xthy2uy']")
        if len(options) == 0:
            self.update_slashState_signal.emit(self.index,
                                               f'Không tìm thấy các options ở profile, đang thử upload lại.')
            return False

        self.update_slashState_signal.emit(self.index,
                                           f'Lấy ra phần tử cuối và click..')
        print('lấy ra phần tử cuối và click')
        last_element: WebElement = options[-1]
        # có lỗi xoá phần tử ở đây, kiểm tra lại
        browser.scrollToElement(last_element)
        self.wait(1)
        browser.forceClick(last_element)
        self.wait(3)
        print('đang ở phần cuối')
        self.update_slashState_signal.emit(self.index,
                                           f'Đang ở phần cuối..')
        schedule_time = data[3]
        # neu video dang len lich
        if schedule_time != None:

            schedule_day = schedule_time[0]
            schedule_time_at = schedule_time[1]
            h = schedule_time_at[0]
            m = schedule_time_at[1]
            aorp = schedule_time_at[2]

            # tim va bam nut schedule
            scheduleBtn = browser.find(
                By.XPATH, "//div[@role='group']//div[contains(text(), 'Schedule')]", timeout=5)
            if not scheduleBtn:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm được nút schedule ở profile, đang thử upload lại.')
                return False
            browser.forceClick(scheduleBtn)
            print('mở phần lên lịch thành công')

            desired1 = 'mm/dd/yyyy'
            desired2 = 'dd/mm/yyyy'
            inputDay1 = browser.find(
                By.XPATH, f"//input[@placeholder='{desired1}']")
            if not inputDay1:
                inputDay2 = browser.find(
                    By.XPATH, f"//input[@placeholder='{desired2}']")
                if not inputDay2:
                    self.update_slashState_signal.emit(self.index,
                                                       f'Không tìm được nút inputDay ở profile, đang thử upload lại..')
                    return False
                schedule_day_split = schedule_day.split('/')
                schedule_day = f'{schedule_day_split[1]}/{schedule_day_split[0]}/{schedule_day_split[2]}'
                inputDay = inputDay2
            else:
                inputDay = inputDay1

            self.update_slashState_signal.emit(self.index,
                                               f'Bắt đầu điền ngày..')
            # overlay = self.browser.find(By.XPATH,"//div[@class='xh8yej3']//div[@class='x78zum5 xdt5ytf x1iyjqo2']/div/div/div[2]",timeout=5)
            # if overlay:
            #     self.browser.driver.execute_script("""var element = arguments[0]; element.parentNode.removeChild(element);""", overlay)
            #     print('đã xoá phần tử overlay')
            print('click truờng nhập date')
            # inputDay.click()
            browser.forceClick(inputDay)
            self.wait(2)
            inputDay.send_keys(Keys.CONTROL+'a')
            self.wait(2)
            inputDay.send_keys(schedule_day)
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Đã điền xong phần ngày tháng, tìm khối giờ..')

            hourBtn = browser.find(
                By.XPATH, "//input[@aria-label='hours' and @role='spinbutton']")
            minutesBtn = browser.find(
                By.XPATH, "//input[@aria-label='minutes' and @role='spinbutton']")
            meridiemBtn = browser.find(
                By.XPATH, "//input[@aria-label='meridiem' and @role='spinbutton']")
            if not hourBtn or not minutesBtn or not meridiemBtn:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm thấy đủ nút cần thiết khi lên lịch ở profile, đang thử upload lại...')
                return False

            print('điền tiếp phần giờ')
            browser.forceClick(hourBtn)
            self.wait(2)
            hourBtn.send_keys(h)
            self.wait(2)

            print('điền tiếp phần phút')
            browser.forceClick(minutesBtn)
            self.wait(2)
            minutesBtn.send_keys(m)
            self.wait(2)

            print('đièn tiếp phần buổi')
            browser.forceClick(meridiemBtn)
            self.wait(2)
            meridiemBtn.send_keys(aorp)
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Đã điền xong , lên lịch video..')
            print('thành công task điền')
            print('lên lịch video')
            self.wait(2)
            while True:
                hbtn = browser.find(
                    By.XPATH, "//div[@class='x3nfvp2 x193iq5w xxymvpz' and @role='none']//div[contains(text(), 'Schedule')]/ancestor::div[@aria-busy='false']")
                try:
                    rs = hbtn.get_attribute('aria-disabled')
                    if rs != 'true':
                        break
                    else:
                        print('đợi hoàn thành')
                        self.wait(2)
                except:
                    break
            browser.scrollToElement(hbtn)
            self.wait(1)
            hbtn.click()
            self.wait(2)
            print('Đăng thành công!!')

        else:
            self.wait(2)
            publicBtn = browser.find(
                By.XPATH, "//div[@role='group']//div[contains(text(), 'Share')]", timeout=5)
            if not publicBtn:
                self.update_slashState_signal.emit(self.index,
                                                   f'Không tìm được nút publicBtn ở profile, đang thử upload lại.')

                return False
            print('chọn đăng ngay')
            browser.scrollToElement(publicBtn)
            self.wait(1)
            publicBtn.click()
            self.wait(2)

            self.update_slashState_signal.emit(self.index,
                                               f'Bắt đầu công khai video..')

            self.wait(2)
            while True:
                hbtn = browser.find(
                    By.XPATH, "//div[@class='x3nfvp2 x193iq5w xxymvpz' and @role='none']//div[contains(text(), 'Share')]/ancestor::div[@aria-busy='false']")
                try:
                    rs = hbtn.get_attribute('aria-disabled')
                    if rs != 'true':
                        break
                    else:
                        print('đợi hoàn thành')
                        self.wait(2)
                except:
                    break
            print('bấm đăng')
            browser.scrollToElement(hbtn)
            self.wait(1)
            hbtn.click()
            self.wait(9)
            print('Đăng thành công!!')

        self.update_slashState_signal.emit(self.index,
                                           f'Đăng thành công video..')
        self.update_colorDone_signal.emit(indexVideo, self.index)
        return True

    def paste_content(self, driver, el, content):
        # danh cho chrome
        driver.execute_script(
            f'''
        const text = `{content}`;
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text', text);
        const event = new ClipboardEvent('paste', {{
        clipboardData: dataTransfer,
        bubbles: true
        }});
        arguments[0].dispatchEvent(event)
        ''',
            el)
        # time.sleep(2)

        # danh cho firefox
        # driver.execute_script(
        #     f'''
        #     const text = `{content}`;
        #     const event = new ClipboardEvent('paste', {{
        #         dataType: 'text/plain',
        #         data: text,
        #         bubbles: true
        #     }});
        #     arguments[0].dispatchEvent(event)
        #     ''',
        #     el)

    def uploadFacebook(self, browser: BrowserFunctions):

        f = open('./data/settingPlatform.json', 'r')
        data = json.load(f)
        typeUpload = data['facebook']

        browser.get('https://business.facebook.com/latest/home')
        self.wait(3)
        self.update_slashState_signal.emit(self.index,
                                           f'Tìm bizKitPresenceSelector..')
        bizKitPresenceSelector = browser.find(
            By.XPATH, "//div[@data-pagelet='BizKitPresenceSelector']")
        if not bizKitPresenceSelector:
            self.update_slashState_signal.emit(self.index,
                                               f'không tìm thấy nút mở modal, đang thử upload lại...')
            return False
        browser.forceClick(bizKitPresenceSelector)

        # go to page function
        self.update_slashState_signal.emit(self.index,
                                           f'Tìm modal chọn trang..')

        print('tìm modal chọn trang')
        modal = browser.find(
            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']")
        if not modal:
            self.update_slashState_signal.emit(self.index,
                                               f'không tìm thấy nút mở modal, đang thử lại...')
            return False

        seeAllBtn = browser.find(
            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'See all')]")
        if seeAllBtn:
            self.wait(2)
            browser.forceClick(seeAllBtn)

        self.update_slashState_signal.emit(self.index,
                                           f'tìm kho chứa page...')
        print('tìm kho chứa page')
        # section:WebElement = self.browser.find(By.XPATH,"//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[@class='x12nagc']//span[contains(text(), 'Your account') and contains(@aria-level, '4')]/ancestor::div[contains(@class, 'xeuugli x6s0dn4 x78zum5 xsgj6o6 x1xmf6yo x21xpn4')]")
        pages: WebElement = browser.find_all(
            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[contains(text(), 'Facebook Page')]/preceding-sibling::div")
        if len(pages) == 0:
            print('không tìm được pages nào')
            pages: WebElement = browser.find_all(
                By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'Facebook Page')]/preceding-sibling::span")
            if len(pages) == 0:
                print('không tìm được pages nào')
                return False
        self.update_slashState_signal.emit(self.index,
                                           f'tìm thành công kho chứa page...')

        for a_page in pages:
            a_page: WebElement
            if a_page.text == self.assetName:
                self.update_slashState_signal.emit(self.index,
                                                   f'tìm thành công page, click vào page...')
                print('bắt đầu cuộn tới phần tử')
                browser.scrollToElement(a_page)
                self.wait(1)
                print('đã cuộn tới phần tử')
                print('click vào phần tử')
                browser.forceClick(a_page)
                break
        self.wait(3)
        # go to page function
        self.update_slashState_signal.emit(self.index,
                                           f'di chuyển sang phần đăng bài...')
        for indexVideo in self.indexVideos:
            if typeUpload == 'reels':
                self.__reelsFacebook(browser, indexVideo)
            else:
                self.__videosFacebook(browser, indexVideo)
        browser.quit()
        self.clear_cell_signal.emit(self.index)

    def __videoYT(self, browser: BrowserFunctions, indexVideo):
        browser.get('https://youtube.com/upload')

    def __shortsYT(self, browser: BrowserFunctions, indexVideo):
        browser.get('https://youtube.com/upload')

        createchannel = browser.find(
            By.XPATH, '//ytd-button-renderer[@id="create-channel-button"]')
        if createchannel:
            createchannel.click()
            self.wait(12)

        data = self.getInfoVideoFromTable(indexVideo)
        videoPath = data[4]
        browser.find(By.XPATH, "//input[@type='file']").send_keys(
            videoPath)
        sleep(4)
        title_textbox = browser.find(
            By.XPATH, "//ytcp-social-suggestions-textbox[@id='title-textarea']//div[@id='textbox']")
        browser.scrollToElement(title_textbox)
        title_textbox.send_keys(Keys.CONTROL + 'a')
        self.wait(1)
        self.paste_content(browser.driver, title_textbox, data[0])
        self.wait(1)
        desc_textbox = browser.find(
            By.XPATH, "//ytcp-social-suggestions-textbox[@id='description-textarea']//div[@id='textbox']")
        browser.scrollToElement(desc_textbox)
        self.wait(1)
        desc_textbox.send_keys(Keys.CONTROL + 'a')
        self.paste_content(browser.driver, desc_textbox, data[1])
        self.wait(1)
        # print(f"==>> thumb_path: {thumb_path}")
        thumb_path = None
        if thumb_path != None:
            print('có thumb')
            thumb_path = str(Path.cwd() / thumb_path)

            browser.find(By.XPATH, "//input[@id='file-loader']").send_keys(
                thumb_path)
            change_display = "document.getElementById('file-loader').style = 'display: block! important'"
            browser.driver.execute_script(change_display)

        kids_section = browser.find(
            By.NAME, "VIDEO_MADE_FOR_KIDS_NOT_MFK")
        browser.scrollToElement(kids_section)
        self.wait(1)
        kids_section.click()
        self.wait(1)
        moreBtn = browser.find(
            By.XPATH, "//ytcp-button[@id='toggle-button']")
        browser.forceClick(moreBtn)
        self.wait(1)
        tags_container = browser.find(
            By.XPATH, '//div[@id="child-input"]//input')
        browser.scrollToElement(tags_container)
        self.wait(1)
        self.paste_content(browser.driver, tags_container, data[2])
        tags_container.send_keys(Keys.ENTER)
        sleep(1)
        visibliyBtn = browser.find(By.XPATH, "//div[@id='step-title-3']")
        browser.scrollToElement(visibliyBtn)
        self.wait(1)
        browser.forceClick(visibliyBtn)
        sleep(1)
        privacy_stt = self.videosTable.cellWidget(indexVideo, 4)
        privacy_stt = privacy_stt.currentText()

        if privacy_stt == 'Unlisted':
            btn = browser.find(
                By.XPATH, "//tp-yt-paper-radio-button[@name='UNLISTED']")
            browser.forceClick(btn)
        elif privacy_stt == 'Public':
            btn = browser.find(
                By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']")
            browser.forceClick(btn)
        else:
            btn = browser.find(
                By.XPATH, '//ytcp-icon-button[@id="second-container-expand-button"]')
            browser.forceClick(btn)
            sleep(1)
            dropdown_date_button = browser.find(
                By.ID, 'datepicker-trigger')
            browser.forceClick(dropdown_date_button)
            sleep(1)
            schedule_time = data[3]
            date_s = schedule_time[0]
            print(f"==>> date_s: {date_s}")
            time_s = schedule_time[1]
            print(f"==>> time_s: {time_s}")
            self.wait(1)
            scheduleDate_field = browser.find(
                By.XPATH, "//ytcp-date-picker//div[@id='labelAndInputContainer']//input", timeout=3)
            scheduleDate_field.send_keys(Keys.CONTROL + 'a')
            self.wait(1)
            date_s = date_s.split('/')
            date_s = f'{date_s[1]}/{date_s[0]}/{date_s[2]}'
            scheduleDate_field.send_keys(date_s)
            self.wait(1)
            scheduleDate_field.send_keys(Keys.ENTER)
            sleep(1)

            scheduleTime_field = browser.find(
                By.XPATH, "//ytcp-form-input-container[@id='time-of-day-container']//input", timeout=3)
            scheduleTime_field.send_keys(Keys.CONTROL + 'a')
            self.wait(1)
            scheduleTime_field.send_keys(f'{time_s[0]}:{time_s[1]}')
            self.wait(1)

            scheduleTime_field.send_keys(Keys.ENTER)
            self.wait(3)

        status_container = browser.find(
            By.XPATH, "//ytcp-video-upload-progress/span")
        while True:
            in_process = status_container.text.find("Uploading") != -1
            if in_process:
                sleep(1)
            else:
                break
        sleep(1)
        try:
            done_button = browser.find(By.ID, "done-button")
            done_button.click()
        except:
            return 'channelGotProblem'
        try:
            doneUploading = browser.find(
                By.XPATH, "//ytcp-button[@id='close-button']", timeout=30)
            if doneUploading:
                sleep(2)
        except:
            return 'channelGotProblem'
        self.update_colorDone_signal.emit(indexVideo, self.index)
        return True

    def uploadYoutube(self, browser: BrowserFunctions):
        f = open('./data/settingPlatform.json', 'r')
        data = json.load(f)
        typeUpload = data['youtube']
        browser.get('https://www.youtube.com/channel_switcher')

        channels = browser.find_all(
            By.XPATH, '//yt-formatted-string[@id="channel-title"]')

        for channel in channels:
            if channel.text == self.assetName:
                channel.click()
                break
        self.wait(3)
        for indexVideo in self.indexVideos:
            self.__shortsYT(browser, indexVideo)
            continue
            if typeUpload == 'shorts':
                self.__shortsYT(browser, indexVideo)
            else:
                self.__videoYT(browser, indexVideo)
        browser.quit()
        self.clear_cell_signal.emit(self.index)

    def __twitter(self, browser: BrowserFunctions, indexVideo):
        browser.get('https://twitter.com/home')
        inp = browser.find(
            By.XPATH, '//input[@accept="image/jpeg,image/png,image/webp,image/gif,video/mp4,video/quicktime"]')
        data = self.getInfoVideoFromTable(indexVideo)
        inp.send_keys(data[4])
        caption = browser.find(By.XPATH, '//div[@contenteditable="true"]')
        caption.click()
        self.wait(1)
        self.paste_content(browser.driver, caption, data[0])
        self.wait(2)
        schedule_time = data[3]
        if schedule_time:
            date_s = schedule_time[0]
            time_s = schedule_time[1]
            browser.find(
                By.XPATH, '//div[@aria-label="Schedule post"]').click()
            self.wait(2)
            date_s = date_s.split('/')
            monthPicker = browser.find(
                By.XPATH, '//div[@aria-label="Date"]/div[1]')
            dayPicker = browser.find(
                By.XPATH, '//div[@aria-label="Date"]/div[2]')
            yearPicker = browser.find(
                By.XPATH, '//div[@aria-label="Date"]/div[3]')

            monthPicker.click()
            months = browser.find_all(
                By.XPATH, '//div[@aria-label="Date"]/div[1]//option')
            for month in months:
                if month.text == self.getMonth(int(date_s[0])):

                    browser.scrollToElement(month)
                    self.wait(2)
                    month.click()
                    break
            self.wait(2)

            dayPicker.click()
            days = browser.find_all(
                By.XPATH, '//div[@aria-label="Date"]/div[2]//option')
            for day in days:
                if day.text == date_s[1]:
                    browser.scrollToElement(day)
                    self.wait(2)
                    day.click()
                    break
            self.wait(2)

            yearPicker.click()
            years = browser.find_all(
                By.XPATH, '//div[@aria-label="Date"]/div[3]//option')
            for year in years:
                if year.text == date_s[2]:
                    browser.scrollToElement(year)
                    self.wait(2)
                    year.click()
                    break
            self.wait(2)

            hourPicker = browser.find(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[1]')
            timePicker = browser.find(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[2]')
            aopPicker = browser.find(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[3]')

            hourPicker.click()
            hours = browser.find_all(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[1]//option')

            for hour in hours:
                if hour.text == time_s[0]:

                    browser.scrollToElement(hour)
                    self.wait(2)
                    hour.click()
                    break
            self.wait(2)

            timePicker.click()
            minutes = browser.find_all(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[2]//option')
            for minute in minutes:
                if minute.text == str(time_s[1]):
                    browser.scrollToElement(minute)
                    self.wait(2)
                    minute.click()
                    break
            self.wait(2)

            aopPicker.click()
            aops = browser.find_all(
                By.XPATH, '//div[@aria-label="Time"]/div[2]/div[3]//option')
            for aop in aops:
                if aop.text == time_s[2]:
                    browser.scrollToElement(aop)
                    self.wait(2)
                    aop.click()
                    break
            self.wait(2)
            browser.find(
                By.XPATH, '//div[@data-testid="scheduledConfirmationPrimaryAction"]').click()
        while True:
            percent = browser.find(
                By.XPATH, '//div[@aria-live="polite"]/div/div/div[1]/span')
            if 'Uploaded (100%)' in percent.text:
                break
        postBtn = browser.find(
            By.XPATH, '//div[@data-testid="tweetButtonInline"]')
        postBtn.click()

        self.wait(10)
        self.update_colorDone_signal.emit(indexVideo, self.index)

    def __instagram(self, browser: BrowserFunctions, indexVideo):
        browser.get('https://instagram.com/', force=True)
        create = browser.find(
            By.XPATH, "//*[local-name()='svg' and @aria-label='New post']")
        create.click()

        inp = browser.find(
            By.XPATH, '//input[@accept="image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime"]')
        data = self.getInfoVideoFromTable(indexVideo)
        inp.send_keys(data[4])
        nextBtn = browser.find(
            By.XPATH, "//div[@role='dialog']//div[contains(text(), 'Next')]")
        nextBtn.click()
        self.wait(6)
        nextBtn = browser.find(
            By.XPATH, "//div[@role='dialog']//div[contains(text(), 'Next')]")
        nextBtn.click()
        self.wait(3)

        field = browser.find(
            By.XPATH, '//div[@role="dialog"]//div[@contenteditable="true"]')
        field.click()
        self.wait(2)
        self.paste_content(browser.driver, field, data[0])
        self.wait(3)
        browser.find(
            By.XPATH, "//div[@role='dialog']//div[contains(text(), 'Share')]").click()
        self.wait(10)
        self.update_colorDone_signal.emit(indexVideo, self.index)

    def listenToTheDialogOnceNew(self, isDone):
        import ctypes
        import win32con
        import win32gui
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        ketqua = []

        def foreach_window(hwnd, lParam):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            # if IsWindowVisible(hwnd):
            # This is the window label

            # Get the class name of the window
            class_name = ctypes.create_unicode_buffer(
                256)  # Adjust the length for your needs
            ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)

            if (class_name.value == '#32770' and buff.value == 'Open'):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                # print('có')
                ketqua.append(True)
                return True

            # PostMessage(GetDlgItem(hwnd, 1148),
            #             0x0100, 0x0D, 0)

            return True

        while len(ketqua) == 0:
            win32gui.EnumWindows(foreach_window, None)
            # EnumWindows(EnumWindowsProc(foreach_window), 0)

    def getMonth(self, month):
        data = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December',
        }
        return data[month]

    def uploadTwitter(self, browser: BrowserFunctions):
        for indexVideo in self.indexVideos:
            self.__twitter(browser, indexVideo)
        browser.quit()
        self.clear_cell_signal.emit(self.index)

    def uploadInstagram(self, browser: BrowserFunctions):

        for indexVideo in self.indexVideos:
            self.__instagram(browser, indexVideo)

        browser.quit()
        self.clear_cell_signal.emit(self.index)

    def chuyen_dinh_dang_ngay(self, chuoi_ngay, dinh_dang_muon_chuyen):
        # Cố gắng chuyển chuỗi ngày sang định dạng "mm/dd/yyyy"
        from datetime import datetime

        try:
            date_obj = datetime.strptime(chuoi_ngay, "mm/dd/yyyy")
        except ValueError:
            # Nếu không thành công, chuyển định dạng sang "dd/mm/yyyy"
            date_obj = datetime.strptime(chuoi_ngay, "dd/mm/yyyy")

        # Chuyển định dạng của datetime thành chuỗi mới
        chuoi_ngay_moi = date_obj.strftime(dinh_dang_muon_chuyen)

        return chuoi_ngay_moi

    def get_asset_id(self, url):
        regex = r"asset_id=(\d+)"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        else:
            return None

    def wait(self, val):
        with self.cond:
            self.cond.wait(val)

    def stopNow(self):
        with self.cond:
            self.isForceStop = True
            self.cond.notify()


class QTableWidgetItemCenter(QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)
        self.setTextAlignment(Qt.AlignCenter)


class TemplateThread(QThread):
    stateAccount = pyqtSignal(int, str)
    changeState = pyqtSignal(int)
    pushErrors = pyqtSignal(str)

    def __init__(self, index, uore):
        super().__init__()
        self.index = index
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
        record = cursor.fetchone()
        conn.close()
        self.username = uore
        self.password = record[3]
        self.cookie = record[4]
        self.facode = record[10]
        self.error = False
        self.errorString = ''
        self.forceStop = False
        self.finished.connect(self.handle_finished)

    def handle_finished(self):

        if self.errorString != '':
            self.pushErrors.emit(self.errorString)
        else:
            self.pushErrors.emit('Hoàn thành tác vụ!')

        self.deleteLater()


class getAssetsInstaThread(TemplateThread):
    sendAsset = pyqtSignal(list)

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        browser = BrowserFunctions(driver)
        browser.get('https://instagram.com/')

        atag = browser.find(
            By.XPATH, '//span[@aria-describedby=":r9:"]//a')
        userlink = atag.get_attribute('href')

        match = re.search(
            r'https://www\.instagram\.com/([a-zA-Z0-9_]+)', userlink)

        self.sendAsset.emit([match.group(1)])
        browser.quit()


class getAssetsXThread(TemplateThread):
    sendAsset = pyqtSignal(list)

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        browser = BrowserFunctions(driver)
        browser.get('https://twitter.com/home')

        iduser = browser.find(
            By.XPATH, '//div[@aria-label="Account menu"]/div[2]/div/div/div/div/span/span[1]')
        final = [iduser.text]

        self.sendAsset.emit(final)
        browser.quit()


class getAssetsYotubeThread(TemplateThread):
    sendAsset = pyqtSignal(list)

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        browser = BrowserFunctions(driver)
        browser.get('https://www.youtube.com/')
        browser.get('https://www.youtube.com/channel_switcher')

        channels = browser.find_all(
            By.XPATH, '//yt-formatted-string[@id="channel-title"]')
        final = []
        for channel in channels:
            final.append(channel.text)
        self.sendAsset.emit(final)
        print(f"==>> final: {final}")
        browser.quit()
        # # go to page function
        # print('tìm modal chọn trang')
        # modal = browser.find(
        #     By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']")
        # if not modal:
        #     print(
        #         f'không tìm thấy modal ở profile đang thử upload lại.')
        #     return

        # sleep(3)
        # print('tìm kho chứa page')
        # final = []
        # pages = browser.find_all(

        #     By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[contains(text(), 'Facebook Page')]/preceding-sibling::div")
        # print(f"==>> pages: {pages}")
        # if len(pages) == 0:
        #     print('không tìm được pages nào')
        #     pages = browser.find_all(
        #         By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'Facebook Page')]/preceding-sibling::span")
        #     if len(pages) == 0:
        #         print('không tìm được pages nào')
        #         return
        # for page in pages:
        #     if page.text not in final:
        #         final.append(page.text)

        # seeAllBtn = browser.find(
        #     By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'See all')]")
        # if seeAllBtn:
        #     browser.forceClick(seeAllBtn)
        #     sleep(2)
        #     pages = browser.find_all(
        #         By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[contains(text(), 'Facebook Page')]/preceding-sibling::div")
        #     if len(pages) == 0:
        #         print('không tìm được pages nào')
        #         pages = browser.find_all(
        #             By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'Facebook Page')]/preceding-sibling::span")
        #         if len(pages) == 0:
        #             print('không tìm được pages nào')
        #             return
        #     for page in pages:
        #         if page.text not in final:
        #             final.append(page.text)
        # self.sendAsset.emit(final)


class getAssetsFacebookThread(TemplateThread):
    sendAsset = pyqtSignal(list)

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        browser = BrowserFunctions(driver)
        browser.get('https://business.facebook.com/latest/home')
        bizKitPresenceSelector = browser.find(
            By.XPATH, "//div[@data-pagelet='BizKitPresenceSelector']")
        if not bizKitPresenceSelector:
            print(
                f'không tìm thấy nút mở modal ở profile đang thử upload lại.')
            return
        browser.forceClick(bizKitPresenceSelector)

        # go to page function
        print('tìm modal chọn trang')
        modal = browser.find(
            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']")
        if not modal:
            print(
                f'không tìm thấy modal ở profile đang thử upload lại.')
            return

        sleep(3)
        print('tìm kho chứa page')
        final = []
        pages = browser.find_all(

            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[contains(text(), 'Facebook Page')]/preceding-sibling::div")
        print(f"==>> pages: {pages}")
        if len(pages) == 0:
            print('không tìm được pages nào')
            pages = browser.find_all(
                By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'Facebook Page')]/preceding-sibling::span")
            if len(pages) == 0:
                print('không tìm được pages nào')
                return
        for page in pages:
            if page.text not in final:
                final.append(page.text)

        seeAllBtn = browser.find(
            By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'See all')]")
        if seeAllBtn:
            browser.forceClick(seeAllBtn)
            sleep(2)
            pages = browser.find_all(
                By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//div[contains(text(), 'Facebook Page')]/preceding-sibling::div")
            if len(pages) == 0:
                print('không tìm được pages nào')
                pages = browser.find_all(
                    By.XPATH, "//div[@class='uiContextualLayer uiContextualLayerBelowLeft']//span[contains(text(), 'Facebook Page')]/preceding-sibling::span")
                if len(pages) == 0:
                    print('không tìm được pages nào')
                    return
            for page in pages:
                if page.text not in final:
                    final.append(page.text)
        self.sendAsset.emit(final)
        browser.quit()


class FacebookLogin(TemplateThread):

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        self.stateAccount.emit(self.index,
                               'Khởi tạo trình duyệt thành công, bắt đầu đăng nhập')
        browser = BrowserFunctions(driver)
        if self.cookie != '' and self.cookie != None:
            self.stateAccount.emit(self.index, 'Tiến hành login bằng cookie')
            rs = self.loginByCookie(browser)
            if rs:
                return
        self.stateAccount.emit(
            self.index, 'Không có cookie, login thông thường')
        self.loginNormal(browser)

    def loginByCookie(self, browser: BrowserFunctions):
        while not self.forceStop:
            browser.get('https://www.facebook.com/')
            url = r"https://www.facebook.com/"
            script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ";domain=.facebook.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' + self.cookie + '"); location.href = "'+url+'"; })();'

            browser.driver.execute_script(script)
            self.stateAccount.emit(self.index, 'Check tình trạng đăng nhập')
            accountControl = browser.find(
                By.XPATH, '//div[@aria-label="Account controls and settings" or @aria-label="Account Controls and Settings"]', timeout=60)
            if not accountControl:
                self.errorString = 'Đăng nhập thất bại! Có điều gì đó đã xảy ra..'
                browser.quit()
                return
            conn = sqlite3.connect('./data/database.db')
            cursor = conn.cursor()
            sql_query = '''UPDATE profiles 
                SET status = ? WHERE uore = ?'''
            cursor.execute(sql_query, (1, self.username))
            conn.commit()
            conn.close()
            self.changeState.emit(self.index)
            browser.quit()
            break

    def loginNormal(self, browser: BrowserFunctions):
        while not self.forceStop:
            browser.get('https://www.facebook.com/')

            accountControl = browser.find(
                By.XPATH, '//div[@aria-label="Account controls and settings" or @aria-label="Account Controls and Settings"]')
            if accountControl:
                conn = sqlite3.connect('./data/database.db')
                cursor = conn.cursor()
                sql_query = '''UPDATE profiles 
                    SET status = ? WHERE uore = ?'''
                cursor.execute(sql_query, (1, self.username))
                conn.commit()
                conn.close()
                self.changeState.emit(self.index)
                browser.quit()
                # self.pushErrors.emit('Tài khoản đã được đăng nhập')
                return
            # điền email
            inputEmail = browser.find(
                By.XPATH, '//input[@name="email" and @id="email"]')
            inputEmail.send_keys(self.username)
            sleep(2)

            # điền password
            inputPassword = browser.find(
                By.XPATH, '//input[@name="pass" and @id="pass"]')
            inputPassword.send_keys(self.password)
            sleep(2)

            loginBtn = browser.find(By.XPATH, "//button[@name='login']")
            loginBtn.click()
            accountControl = browser.find(
                By.XPATH, '//div[@aria-label="Account controls and settings" or @aria-label="Account Controls and Settings"]', timeout=30)
            if accountControl:

                conn = sqlite3.connect('./data/database.db')
                cursor = conn.cursor()
                sql_query = '''UPDATE profiles 
                    SET status = ? WHERE uore = ?'''
                cursor.execute(sql_query, (1, self.username))
                conn.commit()
                conn.close()
                self.changeState.emit(self.index)
                browser.get('https://www.facebook.com/watch/?ref=tab')
                sleep(6)
                browser.quit()
                return

            input2fa = browser.find(
                By.XPATH, '//input[@id="approvals_code"]', timeout=10)
            if input2fa:
                code = get2FA(self.facode)
                print(f"==>> code: {code}")
                input2fa.send_keys(code)
                sleep(2)
                browser.find(
                    By.XPATH, '//button[@id="checkpointSubmitButton"]').click()
            continueBtn = browser.find(
                By.XPATH, '//button[@id="checkpointSubmitButton"]', timeout=10)
            if continueBtn:
                continueBtn.click()
            accountControl = browser.find(
                By.XPATH, '//div[@aria-label="Account controls and settings" or @aria-label="Account Controls and Settings"]', timeout=30)
            if not accountControl:
                self.errorString = 'Đăng nhập thất bại! Có điều gì đó đã xảy ra..'
                browser.quit()
                return
            conn = sqlite3.connect('./data/database.db')
            cursor = conn.cursor()
            sql_query = '''UPDATE profiles 
                SET status = ? WHERE uore = ?'''
            cursor.execute(sql_query, (1, self.username))
            conn.commit()
            conn.close()
            self.changeState.emit(self.index)
            browser.get('https://www.facebook.com/watch/?ref=tab')
            sleep(6)
            browser.quit()
            break


class YoutubeLogin(TemplateThread):
    askLoginSuccess = pyqtSignal()
    theAnswer = None

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        self.stateAccount.emit(self.index,
                               'Khởi tạo trình duyệt thành công, bắt đầu đăng nhập')
        browser = BrowserFunctions(driver)
        self.pushErrors.emit(
            'Trình duyệt đã được mở!<br>Hãy login tài khoản và TẮT TRÌNH DUYỆT sau khi login xong!')
        while True:
            handle = browser.driver.browser_pid
            if psutil.pid_exists(handle):
                # print(f"==>> đang mở: {handle}")
                sleep(1)
            else:
                break

        self.askLoginSuccess.emit()
        while self.theAnswer == None:
            sleep(1)
            print('ngủ')

        if self.theAnswer == True:
            conn = sqlite3.connect('./data/database.db')
            cursor = conn.cursor()
            sql_query = '''UPDATE profiles 
                SET status = ? WHERE uore = ?'''
            cursor.execute(sql_query, (1, self.username))
            conn.commit()
            conn.close()
            self.changeState.emit(self.index)


class XLogin(TemplateThread):

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        self.stateAccount.emit(self.index,
                               'Khởi tạo trình duyệt thành công, bắt đầu đăng nhập')
        browser = BrowserFunctions(driver)
        browser.get('https://twitter.com/')
        accountControl = browser.find(
            By.XPATH, '//div[@aria-label="Account menu"]')
        if accountControl:
            conn = sqlite3.connect('./data/database.db')
            cursor = conn.cursor()
            sql_query = '''UPDATE profiles 
                SET status = ? WHERE uore = ?'''
            cursor.execute(sql_query, (1, self.username))
            conn.commit()
            conn.close()
            self.changeState.emit(self.index)
            browser.quit()
            # self.pushErrors.emit('Tài khoản đã được đăng nhập')
            return

        signinBtn = browser.find(By.XPATH, '//a[@href="/login"]')
        signinBtn.click()
        sleep(3)
        usernameInput = browser.find(
            By.XPATH, '//input[@autocomplete="username"]')
        usernameInput.send_keys(self.username)
        sleep(1)
        usernameInput.send_keys(Keys.ENTER)
        sleep(1)
        passwordInput = browser.find(
            By.XPATH, '//input[@autocomplete="current-password"]')
        passwordInput.send_keys(self.password)
        sleep(2)
        loginBtn = browser.find(
            By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]')
        loginBtn.click()
        sleep(1000)

        accountControl = browser.find(
            By.XPATH, '//div[@aria-label="Account menu"]')
        if not accountControl:
            self.errorString = 'Đăng nhập thất bại! Có điều gì đó đã xảy ra..'
            browser.quit()
            return
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        sql_query = '''UPDATE profiles 
            SET status = ? WHERE uore = ?'''
        cursor.execute(sql_query, (1, self.username))
        conn.commit()
        conn.close()
        self.changeState.emit(self.index)
        sleep(6)
        browser.quit()


class InstagramLogin(TemplateThread):

    def run(self):
        self.stateAccount.emit(self.index, 'Khởi tạo trình duyệt')
        driver = startBrowserFromUore(
            self.username, 900, 600, 50, 100, True, 1)
        if isinstance(driver, str):
            self.error = True
            self.errorString = driver
            return
        browser = BrowserFunctions(driver)
        browser.get('https://www.instagram.com/')
        accountControl = browser.find(
            By.XPATH, '//span[@aria-describedby=":r9:"]')
        if accountControl:
            conn = sqlite3.connect('./data/database.db')
            cursor = conn.cursor()
            sql_query = '''UPDATE profiles 
                SET status = ? WHERE uore = ?'''
            cursor.execute(sql_query, (1, self.username))
            conn.commit()
            conn.close()
            self.changeState.emit(self.index)
            browser.quit()
            # self.pushErrors.emit('Tài khoản đã được đăng nhập')
            return

        inputBtn = browser.find(By.XPATH, '//input[@name="username"]')
        passwordBtn = browser.find(By.XPATH, '//input[@name="password"]')
        inputBtn.send_keys(self.username)
        sleep(2)
        passwordBtn.send_keys(self.password)
        sleep(2)
        browser.find(By.XPATH, '//button[@type="submit"]').click()

        wrongpass = browser.find(
            By.XPATH, '//div[text()="Sorry, your password was incorrect. Please double-check your password."]')
        if wrongpass:
            self.errorString = 'Sai mật khẩu, hãy kiểm tra lại..'
            browser.quit()
            return
        accountControl = browser.find(
            By.XPATH, '//span[@aria-describedby=":r9:"]')
        if not accountControl:
            self.errorString = 'Đăng nhập thất bại! Có điều gì đó đã xảy ra..'
            browser.quit()
            return
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        sql_query = '''UPDATE profiles 
            SET status = ? WHERE uore = ?'''
        cursor.execute(sql_query, (1, self.username))
        conn.commit()
        conn.close()
        try:
            browser.find(
                By.XPATH, "//button[@class=' _acan _acap _acas _aj1- _ap30']").click()
        except:
            print('không có nút save')
        self.changeState.emit(self.index)
        sleep(3)
        browser.quit()
        # self.pushErrors.emit('Tài khoản đã được đăng nhập')
        return


def pushQuestionWithThreeOptionsBeforeDelete():

    msgBox = QMessageBox()
    icon = QIcon()
    icon.addPixmap(QPixmap(":/logo/icon-sw.png"), QIcon.Normal, QIcon.Off)
    msgBox.setWindowIcon(icon)
    msgBox.setText(
        f'Khoan đã! Bạn có muốn xoá luôn file video đã load không?')
    button1 = msgBox.addButton(
        'Có! Dọp dẹp giúp tôi nhé.', QMessageBox.YesRole)
    button2 = msgBox.addButton(
        'Không! Đừng xoá video đã tải xuống.', QMessageBox.NoRole)
    button3 = msgBox.addButton('Huỷ', QMessageBox.RejectRole)
    msgBox.setWindowTitle('Khoan đã!')

    msgBox.exec_()

    if msgBox.clickedButton() == button1:
        return 'Yes'
    elif msgBox.clickedButton() == button2:
        return 'No'
    elif msgBox.clickedButton() == button3:
        return 'Cancel'


def get2FA(code):
    response = requests.get(
        f'https://2fa.live/tok/{code}')
    return response.json()['token']


def startBrowserFromUore(uore, width, height, x, y, mute=False, scale: float = 1, headless=False, original=False):

    conn = sqlite3.connect('./data/database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles WHERE uore = ?", (uore,))
    record = cursor.fetchone()
    proxy = record[7]
    proxyMode = record[8]
    id_browser = record[9]

    API_ENDPOINT = 'http://127.0.0.1:53200/api/v2/'
    ACTION_FOR_BROWSER_CREATE = API_ENDPOINT + 'profile-create'
    ACTION_FOR_BROWSER_OPEN = API_ENDPOINT + 'profile-open'

    if not id_browser:
        print('k có, cần tạo thêm')
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        webgl_vendor = "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)"
        longla = "105.853882,21.028280"
        rest = createBrowser(
            ACTION_FOR_BROWSER_CREATE, proxy, user_agent, webgl_vendor, longla, 1)
        try:
            rest = int(rest)
        except:
            return rest

        sql_query = '''UPDATE profiles
                    SET id_ixbrowser = ? WHERE uore = ?'''
        cursor.execute(sql_query, (rest, uore))
        conn.commit()

        id_browser = rest

    driver = openBrowser(ACTION_FOR_BROWSER_OPEN, int(
        id_browser), proxy, proxyMode, width, height, x, y, scale, mute, headless)

    try:
        err = driver[1]
        if 'Proxy detection failed' in err:
            return 'Bạn cần kiểm tra lại vì proxy của bạn có vấn đề!'

        if 'Lỗi khi khởi tạo trình duyệt Undetected!' in err:
            return 'Lỗi khi khởi tạo trình duyệt Undetected!'

        if 'No connection could be made because the target machine actively refused it' in err:
            return 'Hình như bạn chưa khởi động và đăng nhập IXBrowser, vui lòng kiểm tra lại!'

        if 'Profile does not exist' in err:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            webgl_vendor = "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)"
            longla = "105.853882,21.028280"
            rest = createBrowser(
                ACTION_FOR_BROWSER_CREATE, proxy, user_agent, webgl_vendor, longla, 1)
            try:
                rest = int(rest)
            except:
                return rest

            sql_query = '''UPDATE profiles
                        SET id_ixbrowser = ? WHERE uore = ?'''
            cursor.execute(sql_query, (rest, uore))
            conn.commit()

            id_browser = rest
            driver = openBrowser(ACTION_FOR_BROWSER_OPEN, int(
                id_browser), proxy, proxyMode, width, height, x, y, scale, mute, headless)
        else:
            return err

    except:
        pass
    if original:
        API_ENDPOINT = 'http://127.0.0.1:53200/api/v2/'
        ACTION_UPDATE = API_ENDPOINT + 'profile-random-fingerprint-configuration'
        updateBrowserFingerprint(ACTION_UPDATE, id_browser)
    conn.close()
    return driver


def pushNotification(title):
    if title == '':
        return
    msg = QMessageBox()
    icon = QIcon()
    icon.addPixmap(QPixmap(":/logo/icon-sw.png"), QIcon.Normal, QIcon.Off)
    msg.setWindowIcon(icon)
    msg.setWindowTitle('Thông báo!')
    msg.setTextFormat(Qt.RichText)
    msg.setText(title)
    # msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
    # QTimer.singleShot(0, msg.raise_)
    msg.activateWindow()
    msg.exec_()
    return


def pushYNQuestion(msg):

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Thông báo")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    # Set the icon of the dialog
    msg_box.setWindowIcon(QIcon(":/logo/icon-sw.png"))

    button_reply = msg_box.exec_()

    if button_reply == QMessageBox.Yes:
        return True
    else:
        return False
