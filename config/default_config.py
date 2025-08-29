#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
廣告替換系統 - 預設內部設定檔
這是系統的預設設定，會被 ad_replacer_runner.py 複製並修改為 config.py
"""

# 基本設定 (會被 ad_replacer_runner.py 動態修改)
SCREENSHOT_COUNT = 10
BASE_URL = "https://example.com"
NEWS_COUNT = 20

# 系統設定 (固定不變)
MAX_ATTEMPTS = 50
PAGE_LOAD_TIMEOUT = 15
WAIT_TIME = 3
REPLACE_IMAGE_FOLDER = "replace_image"
DEFAULT_IMAGE = "mini.jpg"
MINI_IMAGE = "mini.jpg"

# 廣告尺寸設定
TARGET_AD_SIZES = [
    {"width": 970, "height": 90},   # 超級橫幅
    {"width": 986, "height": 106},  # 大型橫幅
    {"width": 728, "height": 90},   # 排行榜橫幅
    {"width": 300, "height": 250},  # 中矩形
    {"width": 336, "height": 280},  # 大矩形
    {"width": 320, "height": 50},   # 手機橫幅
    {"width": 160, "height": 600},  # 寬摩天大樓
    {"width": 300, "height": 600}   # 半頁廣告
]

# 圖片使用次數設定 (控制每種尺寸圖片的使用頻率)
IMAGE_USAGE_COUNT = {
    "img_970x90.jpg": 5,
    "img_986x106.jpg": 3,
    "img_728x90.jpg": 4,
    "img_300x250.jpg": 6,
    "img_336x280.jpg": 4,
    "img_320x50.jpg": 3,
    "img_160x600.jpg": 2,
    "img_300x600.jpg": 2
}

# 進階設定
MAX_CONSECUTIVE_FAILURES = 10
CLOSE_BUTTON_SIZE = {"width": 15, "height": 15}
INFO_BUTTON_SIZE = {"width": 15, "height": 15}
INFO_BUTTON_COLOR = "#00aecd"
INFO_BUTTON_OFFSET = 16
FULLSCREEN_MODE = True
DEBUG_MODE = True
SCREENSHOT_FOLDER = "screenshots"
BUTTON_STYLE = "dots"

# 瀏覽器設定
BROWSER_WINDOW_SIZE = {"width": 1920, "height": 1080}
SCROLL_PAUSE_TIME = 2
ELEMENT_WAIT_TIME = 10

# 圖片處理設定
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_QUALITY = 85

# 日誌設定
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/ad_replacer.log"