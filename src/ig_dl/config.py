import requests
from famgz_utils import json_, Cookies
from pathlib import Path

_source_path = Path(__file__).resolve()
SOURCE_DIR = _source_path.parent
DATA_DIR = Path(SOURCE_DIR, 'data')
COOKIES_DIR = Path(SOURCE_DIR, 'cookies')
TEMP_DIR = Path(SOURCE_DIR, 'temp')
OUTPUT_DIR = 'C:\\INSTAGRAM'

_cookies_keys = [
    'ig_did',
    'mid',
    'datr',
    'ig_nrcb',
    'csrftoken',
    'ds_user_id',
    'shbid',
    'sessionid',
    'rur',
    'shbts',
]

cookies = Cookies(COOKIES_DIR).get_cookies()

headers = {
    'authority': 'www.instagram.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.instagram.com/',
    'sec-ch-ua': '"Brave";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'x-asbd-id': '129477',
    # 'x-csrftoken': '',
    'x-ig-app-id': '936619743392459',
    'x-ig-www-claim': '0',
    'x-requested-with': 'XMLHttpRequest',
}

session = requests.Session()
