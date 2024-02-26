import os
import signal
import traceback
from typing import Optional
import requests
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium import webdriver
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver


class BrowserFunctions:
    def __init__(self, driver: undetected_chromedriver.Chrome | webdriver.Firefox):
        self.driver = driver

    def get(
        self,
        url: str,
        force: bool = False
    ) -> bool:
        if not force:
            to_remove = ['www.']

            clean_current = self.driver.current_url.split('://')[-1]
            clean_new = url.split('://')[-1]

            for _to_remove in to_remove:
                clean_current = clean_current.replace(_to_remove, '')
                clean_new = clean_new.replace(_to_remove, '')

            if clean_current.strip('/') == clean_new.strip('/'):
                return False

        self.driver.get(url)

        return True

    def find(
        self,
        by: By,
        key: str,
        timeout: int = 5
    ) -> Optional[WebElement]:

        try:
            e = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, key))
            )

            return e
        except:
            return None

    def find_all(
        self,
        by: By,
        key: str,
        timeout: int = 5
    ) -> Optional[WebElement]:

        try:
            es = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, key))
            )

            return es
        except:
            return []

    def scrollToElement(self, el):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior : 'smooth',block:'center'});", el)
        sleep(1)

    def scrollToBottomPage(self):
        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        sleep(1)

    def getOverlappingElement(self, element: WebElement) -> Optional[WebElement]:
        rect = element.rect
        result = self.driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);",
                                            rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2)
        if result == element:
            result = None
        return result

    def forceClick(self, el: WebElement):
        while True:
            try:
                el.click()
                return True
            except ElementClickInterceptedException:
                print(traceback.format_exc())
                self.driver.execute_script(
                    "arguments[0].remove();", self.getOverlappingElement(el))
            except Exception:
                print(traceback.format_exc())
                return False

    def quit(self):
        # self.driver.quit()
        print(f"==>> self.driver.profile_id: {self.driver.profile_id}")
        action = 'http://127.0.0.1:53200/api/v2/profile-close'
        paras = {
            "profile_id": self.driver.profile_id
        }
        requests.post(action, json=paras)
        # try:
        #     os.kill(self.driver.service.process.pid, signal.SIGTERM)
        #     print('kill thanh cong')
        #     return 1
        # except:
        #     return 0
