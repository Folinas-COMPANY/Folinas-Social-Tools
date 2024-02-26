import time
import random
import string
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
import traceback
HTTP_CODE_FOR_SUCCESS = 200
RESULT_CODE_FOR_SUCCESS = 0
RESULT_CODE_FOR_PROXY_FAIL = 406
resolutions = [
    "1920,1080",
    "1366,768",
    "1280,800",
    "2560,1440",
    "3840,2160",
    "1024,768",
    "1280,1024",
    "1600,900",
    "1440,900",
    "1280,720",
    "1920,1200",
    "2560,1080",
    "3440,1440",
    "4096,2160",
    "1152,864",
    "1280,960",
    "1600,1200",
    "2048,1080",
    "2048,1536",
    "2560,1600",
    "3440,1600",
    "3840,1600",
    "4096,2304",
    "5120,2880",
    "7680,4320"
]
web_driver_path = None
debugging_address = None


def genANumber(stopwatch=None):
    a = [2, 4, 8, 16, 32, 48, 64]
    if stopwatch:
        while True:
            num = random.choice(a)
            if num <= stopwatch:
                return random.choice(a)
    return random.choice(a)


def generate_random_color_hex():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    color_hex = "#{:02X}{:02X}{:02X}".format(r, g, b)
    return color_hex


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def createBrowser(action: str, proxy, ua_info, webgl_info, location, project_id):
    location = location.split(',')
    proxy_ip = ''
    proxy_port = ''
    proxy_user = ''
    proxy_password = ''
    proxy_type = "direct"

    post_data = {

        "site_id": 22,
        "site_url": "",
        "color": "#CC9966",
        "name": f"SSMATool-{generate_random_string(6)}",
        "note": "",
        "group_id": 1,
        "username": "",
        "password": "",
        "cookie": "",
        "proxy_config": {
            "proxy_mode": 2,
            "proxy_id": "",
            "proxy_type": proxy_type,
            "proxy_ip": proxy_ip,
            "proxy_port": proxy_port,
            "proxy_user": proxy_user,
            "proxy_password": proxy_password,
            "ip_detection": "0",
            "traffic_package_ip_policy": False
        },
        "fingerprint_config": {
            "hardware_concurrency": f"{genANumber(48)}",
            "device_memory": f"{genANumber()}",
            "ua_type": 1,
            "platform": "Windows",
            "br_version": "",
            "ua_info": ua_info,
            "language_type": "1",
            "language": "us",
            "timezone_type": "1",
            "timezone": "",
            "location": "1",
            "location_type": "1",
            "longitude": float(location[0]),
            "latitude": float(location[1]),
            "accuracy": 1000,
            "resolving_power_type": "2",
            "resolving_power": f"{random.randint(1024,1600)},{random.randint(768,960)}",
            "fonts_type": "1",
            "fonts": [],
            "webrtc": "3",
            "webgl_image": "1",
            "canvas_type": "1",
            "webgl_data_type": "1",
            "webgl_factory": "Google Inc.",
            "webgl_info": "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)",
            "audio_context": "1",
            "media_equipment": "1",
            "client_rects": "1",
            "speech_voices": "1",
            "device_name_source": "1",
            "track": "1",
            "allow_scan_ports": "0",
            "allow_scan_ports_content": ""
        },
        "preference_config": {
            "cookies_backup": "0",
            "extra_tab_source": "0",
            "open_url": "",
            "block_image": "0",
            "block_audio": "0"
        }
    }

    print(f"==>> post_data: {post_data}")

    while True:
        try:
            response = requests.post(action, json=post_data)
            if response.status_code == HTTP_CODE_FOR_SUCCESS:
                result = response.json()
                print(f"==>> Create - result: {result}")
                if result['error']['code'] == RESULT_CODE_FOR_SUCCESS:
                    return result['data']
                elif result['error']['code'] == RESULT_CODE_FOR_PROXY_FAIL:
                    return "Thất bại khi tạo mới trình duyệt Undetected vì:<br>Proxy detection failed, try again!"
            else:
                return 'Thất bại khi tạo mới trình duyệt Undetected'
        except Exception as e:
            print(traceback.format_exc())
            if 'No connection could be made because the target machine actively refused it' in str(e):
                return 'Hình như bạn chưa khởi động và đăng nhập IXBrowser,vui lòng kiểm tra lại!'
            return str(e)


def updateBrowser(action: str, profile_id: int, mode, proxy_ip: str, proxy_port: str, proxy_user: str, proxy_password: str):
    post_data = {
        "profile_id": profile_id,
        "proxy_info": {
            "proxy_mode": 2,
            "proxy_type": mode,
            "proxy_ip": proxy_ip,
            "proxy_port": proxy_port,
            "proxy_user": proxy_user,
            "proxy_password": proxy_password
        }
    }

    try:
        response = requests.post(action, json=post_data)
        if response.status_code == HTTP_CODE_FOR_SUCCESS:
            result = response.json()
            print(f"==>> Update result: {result}")
            if result['error']['code'] == RESULT_CODE_FOR_SUCCESS:
                flag = True
            else:
                flag = False
                print('[error]', 'error_code=', result['error']
                      ['code'], result['error']['message'])
        else:
            flag = False
            print('[error]', 'status_code=', response.status_code)
    except Exception as e:
        flag = False
        print('[error] Exception desc:', str(e))

    # return flag


def openBrowser(action: str, profile_id: int, proxy, proxyMode, width=None, height=None, x=None, y=None, scale=None, mute=None, headless=None):
    print(f"==>> profile_id: {profile_id}")

    paras = {
        "profile_id": profile_id,  # Profile serial number
        "args": [
            "--disable-extension-welcome-page", f"--window-position={x},{30}", f"--window-size={random.randint(1200,1600)},{random.randint(768,960)}", f"--force-device-scale-factor={scale}"
        ],  # Enable parameters. Example "args": ["--disable-extensions", "--blink-settings=imagesEnabled=false" ] For more parameters, please refer to: https://peter.sh/experiments/chromium-command-line-switches（ You can try to use more parameters, but there is no guarantee that they will all work)
        "load_extensions": True,  # Whether to enable the extension
        "load_profile_info_page": False,  # Whether to load the profile information page
        "cookies_backup": False,  # Cloud backup cookie false: off true: on
        "cookie": ""  # cookie  json Format
    }

    if mute:
        paras = {
            "profile_id": profile_id,  # Profile serial number
            "args": [
                "--disable-extension-welcome-page", f"--window-position={x},{30}", "--mute-audio", f"--window-size={random.randint(1200,1600)},{random.randint(768,960)}", f"--force-device-scale-factor={scale}"
            ],  # Enable parameters. Example "args": ["--disable-extensions", "--blink-settings=imagesEnabled=false" ] For more parameters, please refer to: https://peter.sh/experiments/chromium-command-line-switches（ You can try to use more parameters, but there is no guarantee that they will all work)
            "load_extensions": True,  # Whether to enable the extension
            "load_profile_info_page": False,  # Whether to load the profile information page
            "cookies_backup": False,  # Cloud backup cookie false: off true: on
            "cookie": ""  # cookie  json Format
        }
    if proxy != '' and proxy != None:
        proxySplit = proxy.split(':')
        ip = proxySplit[0]
        port = proxySplit[1]
        try:
            usernameProxy = proxySplit[2]
            passwordProxy = proxySplit[3]
        except:
            usernameProxy = ''
            passwordProxy = ''
        API_ENDPOINT = 'http://127.0.0.1:53200/api/v2/'
        ACTION_UPDATE = API_ENDPOINT + 'profile-update-proxy-for-custom-proxy'
        updateBrowser(ACTION_UPDATE, profile_id, proxyMode,
                      ip, port, usernameProxy, passwordProxy)

    else:
        API_ENDPOINT = 'http://127.0.0.1:53200/api/v2/'
        ACTION_UPDATE = API_ENDPOINT + 'profile-update-proxy-for-custom-proxy'
        updateBrowser(ACTION_UPDATE, profile_id, 'direct', '', '', '', '')

    while True:
        try:
            response = requests.post(action, json=paras, timeout=20)

            if response.status_code == HTTP_CODE_FOR_SUCCESS:
                result = response.json()
                print(f"==>> Open - result: {result}")
                if result['error']['code'] == RESULT_CODE_FOR_SUCCESS:
                    web_driver_path = result['data']['webdriver']
                    debugging_address = result['data']['debugging_address']
                    pid = result['data']['pid']
                else:
                    return ['error', result['error']['message']]
            else:
                print('[error]', 'status_code22=', response.status_code)
                return ['error', 'Lỗi khi khởi tạo trình duyệt Undetected!']
            break

        except Exception as e:
            print(traceback.format_exc())

            return ['error', str(e)]

    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", debugging_address)

    # driver = uc.Chrome(options=chrome_options,driver_executable_path=web_driver_path,keep_alive=False)
    driver = Chrome(service=Service(web_driver_path), options=chrome_options)
    driver.browser_pid = pid
    driver.profile_id = profile_id
    return driver


def updateBrowserFingerprint(action: str, profile_id: int):
    paras = {
        "profile_id": profile_id,  # Profile serial number
    }
    while True:
        try:
            response = requests.post(action, json=paras, timeout=20)

            if response.status_code == HTTP_CODE_FOR_SUCCESS:
                result = response.json()
                print(f"==>> result: {result}")
                if result['error']['code'] == RESULT_CODE_FOR_SUCCESS:
                    return True
                else:
                    return 'Thất bại! Vui lòng kiểm tra xem đã tồn tại trình duyệt chưa!'

        except Exception as e:
            print(traceback.format_exc())
            if 'No connection could be made because the target machine actively refused it' in str(e):
                return 'Hình như bạn chưa khởi động và đăng nhập IXBrowser, vui lòng kiểm tra lại!'
            return str(e)


def closeBrowser(action: str, profile_id: int):
    paras = dict()
    paras['profile_id'] = profile_id

    try:
        response = requests.post(action, json=paras)
        if response.status_code == HTTP_CODE_FOR_SUCCESS:
            result = response.json()
            if result['error']['code'] == RESULT_CODE_FOR_SUCCESS:
                print('Closed browser for profile', profile_id)
                return True
            else:
                print('[error]', 'error_code=', result['error']
                      ['code'], result['error']['message'])
                return False
        else:
            print('[error]', 'status_code=', response.status_code)
            return False
    except Exception as e:
        print('[error] Exception desc:', str(e))
        return False
