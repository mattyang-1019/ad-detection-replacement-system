#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用模板 - 廣告偵測與替換系統

🔧 使用者自訂指南：
如果程式無法偵測到您網站的廣告，請搜尋以下關鍵字並修改對應的選擇器：

🔍 搜尋關鍵字：
1. "🔧 使用者可修改：廣告容器選擇器" - 修改廣告元素選擇器
2. "🔧 使用者可修改：廣告關鍵字" - 修改廣告關鍵字列表  
3. "🔧 使用者必須修改：根據目標網站修改這些選擇器" - 修改文章連結選擇器
4. "🔧 使用者可修改：全螢幕廣告選擇器" - 修改彈出廣告選擇器
5. "🔧 使用者自訂區域" - 添加您網站特有的選擇器

💡 詳細說明請參考 README.md 中的「使用者自訂指南」章節
"""

import time
import os
import base64
import random
import re
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# 載入設定檔
try:
    from config import *
    print("成功載入 config.py 設定檔")
    print(f"SCREENSHOT_COUNT 設定: {SCREENSHOT_COUNT}")
    print(f"NEWS_COUNT 設定: {NEWS_COUNT}")
    print(f"IMAGE_USAGE_COUNT 設定: {IMAGE_USAGE_COUNT}")
except ImportError:
    print("找不到 config.py，使用預設設定")
    # 預設設定
    SCREENSHOT_COUNT = 10
    MAX_ATTEMPTS = 50
    PAGE_LOAD_TIMEOUT = 15
    WAIT_TIME = 3
    REPLACE_IMAGE_FOLDER = "replace_image"
    DEFAULT_IMAGE = "mini.jpg"
    MINI_IMAGE = "mini.jpg"
    BASE_URL = "https://example.com"
    
    NEWS_COUNT = 20
    TARGET_AD_SIZES = [{"width": 970, "height": 90}, {"width": 986, "height": 106}]
    IMAGE_USAGE_COUNT = {"img_970x90.jpg": 5, "img_986x106.jpg": 3}
    MAX_CONSECUTIVE_FAILURES = 10
    CLOSE_BUTTON_SIZE = {"width": 15, "height": 15}
    INFO_BUTTON_SIZE = {"width": 15, "height": 15}
    INFO_BUTTON_COLOR = "#00aecd"
    INFO_BUTTON_OFFSET = 16
    FULLSCREEN_MODE = True
    DEBUG_MODE = True
    SCREENSHOT_FOLDER = "screenshots"

class ScreenManager:
    """螢幕管理器，用於偵測和管理多螢幕"""
    
    @staticmethod
    def detect_screens():
        """偵測可用的螢幕數量和資訊"""
        system = platform.system()
        screens = []
        
        try:
            if system == "Darwin":  # macOS
                # 使用 system_profiler 獲取顯示器資訊
                cmd = "system_profiler SPDisplaysDataType | grep -A 2 'Resolution:'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    screen_count = 0
                    for line in lines:
                        if 'Resolution:' in line:
                            screen_count += 1
                            resolution = line.split('Resolution:')[1].strip()
                            screens.append({
                                'id': screen_count,
                                'resolution': resolution,
                                'primary': screen_count == 1
                            })
                
                # 如果無法獲取詳細資訊，使用 AppleScript 獲取螢幕數量
                if not screens:
                    applescript = '''
                    tell application "Finder"
                        set screenCount to count of desktop
                        return screenCount
                    end tell
                    '''
                    result = subprocess.run(['osascript', '-e', applescript], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        screen_count = int(result.stdout.strip())
                        for i in range(1, screen_count + 1):
                            screens.append({
                                'id': i,
                                'resolution': 'Unknown',
                                'primary': i == 1
                            })
                
            elif system == "Windows":
                # Windows 多種方法偵測螢幕
                try:
                    # 方法1: 使用 wmic path Win32_VideoController
                    cmd = 'wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution /format:csv'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        screen_id = 1
                        for line in lines[1:]:  # 跳過標題行
                            if line.strip() and ',' in line:
                                parts = line.split(',')
                                if len(parts) >= 3:
                                    width = parts[1].strip()
                                    height = parts[2].strip()
                                    if width and height and width != 'NULL' and width.isdigit():
                                        screens.append({
                                            'id': screen_id,
                                            'resolution': f"{width}x{height}",
                                            'primary': screen_id == 1
                                        })
                                        screen_id += 1
                except Exception as e:
                    print(f"方法1失敗: {e}")
                
                # 方法2: 如果方法1失敗，使用 PowerShell
                if not screens:
                    try:
                        powershell_cmd = '''
                        Add-Type -AssemblyName System.Windows.Forms
                        [System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
                            Write-Output "$($_.Bounds.Width)x$($_.Bounds.Height):$($_.Primary)"
                        }
                        '''
                        result = subprocess.run(['powershell', '-Command', powershell_cmd], 
                                              capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            screen_id = 1
                            for line in lines:
                                if 'x' in line and ':' in line:
                                    resolution, is_primary = line.strip().split(':')
                                    screens.append({
                                        'id': screen_id,
                                        'resolution': resolution,
                                        'primary': is_primary.lower() == 'true'
                                    })
                                    screen_id += 1
                    except Exception as e:
                        print(f"方法2失敗: {e}")
                
                # 方法3: 如果前面都失敗，嘗試使用 Python 的 tkinter
                if not screens:
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        
                        # 獲取主螢幕資訊
                        width = root.winfo_screenwidth()
                        height = root.winfo_screenheight()
                        
                        screens.append({
                            'id': 1,
                            'resolution': f"{width}x{height}",
                            'primary': True
                        })
                        
                        # 嘗試獲取多螢幕資訊
                        try:
                            # 這個方法可能不適用於所有 Windows 版本
                            screen_count = root.tk.call('tk', 'scaling')
                            if screen_count and screen_count > 1:
                                for i in range(2, int(screen_count) + 1):
                                    screens.append({
                                        'id': i,
                                        'resolution': f"{width}x{height}",
                                        'primary': False
                                    })
                        except:
                            pass
                        
                        root.destroy()
                    except Exception as e:
                        print(f"方法3失敗: {e}")
                
                # 方法4: 最後的備用方案，使用 pyautogui (如果可用)
                if not screens:
                    try:
                        import pyautogui
                        width, height = pyautogui.size()
                        screens.append({
                            'id': 1,
                            'resolution': f"{width}x{height}",
                            'primary': True
                        })
                        
                        # pyautogui 沒有直接的多螢幕支援，但我們可以嘗試檢測
                        # 通過嘗試不同的座標來推測是否有多螢幕
                        try:
                            # 嘗試在主螢幕右側檢測
                            test_x = width + 100
                            test_y = 100
                            # 這裡我們假設如果能在主螢幕外截圖，就有第二個螢幕
                            # 但 pyautogui 的 screenshot 不支援這種檢測，所以這只是一個佔位符
                            pass
                        except:
                            pass
                            
                    except ImportError:
                        print("pyautogui 未安裝")
                    except Exception as e:
                        print(f"方法4失敗: {e}")
                
            else:  # Linux
                # Linux 使用 xrandr
                try:
                    result = subprocess.run(['xrandr'], capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        screen_id = 1
                        for line in lines:
                            if ' connected' in line:
                                parts = line.split()
                                if len(parts) >= 3:
                                    resolution = parts[2] if 'x' in parts[2] else 'Unknown'
                                    screens.append({
                                        'id': screen_id,
                                        'resolution': resolution,
                                        'primary': 'primary' in line
                                    })
                                    screen_id += 1
                except FileNotFoundError:
                    print("xrandr 命令未找到，無法偵測螢幕")
            
            # 如果無法偵測到螢幕，至少返回一個預設螢幕
            if not screens:
                screens.append({
                    'id': 1,
                    'resolution': 'Unknown',
                    'primary': True
                })
                
        except Exception as e:
            print(f"偵測螢幕時發生錯誤: {e}")
            screens.append({
                'id': 1,
                'resolution': 'Unknown',
                'primary': True
            })
        
        return screens
    
    @staticmethod
    def select_screen():
        """讓使用者選擇要使用的螢幕"""
        screens = ScreenManager.detect_screens()
        
        print("\n" + "="*50)
        print("偵測到的螢幕:")
        print("="*50)
        
        for screen in screens:
            primary_text = " (主螢幕)" if screen['primary'] else ""
            print(f"螢幕 {screen['id']}: {screen['resolution']}{primary_text}")
        
        print("="*50)
        
        # 如果只有一個螢幕，自動選擇
        if len(screens) == 1:
            print("只偵測到一個螢幕，自動選擇螢幕 1")
            return 1, screens[0]
        
        while True:
            try:
                choice = input(f"請選擇要使用的螢幕 (1-{len(screens)}) [預設: 1]: ").strip()
                
                # 如果使用者直接按 Enter，使用預設值 1
                if not choice:
                    choice = "1"
                
                screen_id = int(choice)
                
                if 1 <= screen_id <= len(screens):
                    selected_screen = next(s for s in screens if s['id'] == screen_id)
                    print(f"✅ 已選擇螢幕 {screen_id}: {selected_screen['resolution']}")
                    return screen_id, selected_screen
                else:
                    print(f"❌ 請輸入 1 到 {len(screens)} 之間的數字")
                    
            except ValueError:
                print("❌ 請輸入有效的數字")
            except KeyboardInterrupt:
                print("\n程式已取消")
                return None, None
    
    @staticmethod
    def get_screen_info(screen_id):
        """獲取指定螢幕的詳細資訊"""
        screens = ScreenManager.detect_screens()
        for screen in screens:
            if screen['id'] == screen_id:
                return screen
        return None

class WebsiteAdReplacer:
    def __init__(self, screen_id=1):
        self.screen_id = screen_id
        self.setup_driver()
        self.load_replace_images()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-gpu-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        
        # 根據作業系統設定螢幕位置
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # macOS 多螢幕支援
            if self.screen_id > 1:
                # 計算螢幕偏移量 (假設每個螢幕寬度為1920px)
                screen_offset = (self.screen_id - 1) * 1920
                chrome_options.add_argument(f'--window-position={screen_offset},0')
            
        elif system == "Windows":
            # Windows 多螢幕支援
            if self.screen_id > 1:
                screen_offset = (self.screen_id - 1) * 1920
                chrome_options.add_argument(f'--window-position={screen_offset},0')
        
        if FULLSCREEN_MODE:
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--start-fullscreen')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 確保瀏覽器在正確的螢幕上
        self.move_to_screen()
    
    def move_to_screen(self):
        """將瀏覽器移動到指定螢幕"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # 使用 AppleScript 移動 Chrome 到指定螢幕
                applescript = f'''
                tell application "Google Chrome"
                    activate
                    set bounds of front window to {{0, 0, 1920, 1080}}
                end tell
                '''
                
                if self.screen_id > 1:
                    # 計算螢幕偏移
                    screen_offset = (self.screen_id - 1) * 1920
                    applescript = f'''
                    tell application "Google Chrome"
                        activate
                        set bounds of front window to {{{screen_offset}, 0, {screen_offset + 1920}, 1080}}
                    end tell
                    '''
                
                subprocess.run(['osascript', '-e', applescript], 
                             capture_output=True, text=True)
                
            elif system == "Windows":
                # Windows 使用 Selenium 的視窗管理
                if self.screen_id > 1:
                    screen_offset = (self.screen_id - 1) * 1920
                    self.driver.set_window_position(screen_offset, 0)
                    
            # 確保全螢幕模式
            if FULLSCREEN_MODE:
                time.sleep(1)  # 等待視窗移動完成
                self.driver.fullscreen_window()
                
            print(f"✅ Chrome 已移動到螢幕 {self.screen_id}")
            
        except Exception as e:
            print(f"移動瀏覽器到螢幕 {self.screen_id} 失敗: {e}")
            print("將使用預設螢幕位置")
    
    def load_replace_images(self):
        """載入替換圖片並解析尺寸"""
        self.replace_images = []
        
        if not os.path.exists(REPLACE_IMAGE_FOLDER):
            print(f"找不到替換圖片資料夾: {REPLACE_IMAGE_FOLDER}")
            return
        
        print(f"開始載入 {REPLACE_IMAGE_FOLDER} 資料夾中的圖片...")
        
        for filename in os.listdir(REPLACE_IMAGE_FOLDER):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                # 解析檔案名中的尺寸 - 支援 google_ 和 img_ 兩種格式
                size_match = re.search(r'(?:google_|img_)(\d+)x(\d+)', filename)
                if size_match:
                    width = int(size_match.group(1))
                    height = int(size_match.group(2))
                    
                    image_path = os.path.join(REPLACE_IMAGE_FOLDER, filename)
                    self.replace_images.append({
                        'path': image_path,
                        'filename': filename,
                        'width': width,
                        'height': height
                    })
                    print(f"載入圖片: {filename} ({width}x{height})")
                else:
                    print(f"跳過不符合命名規則的圖片: {filename}")
        
        # 按檔案名排序
        self.replace_images.sort(key=lambda x: x['filename'])
        print(f"總共載入 {len(self.replace_images)} 張替換圖片")
        
        # 顯示載入的圖片清單
        for i, img in enumerate(self.replace_images):
            print(f"  {i+1}. {img['filename']} ({img['width']}x{img['height']})")
    
    def load_image_base64(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"找不到圖片: {image_path}")
            
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def debug_page_ads(self):
        """
        調試方法：顯示頁面上所有可能的廣告元素
        
        🔧 使用者自訂指南：
        如果程式無法偵測到您網站的廣告，請修改以下選擇器：
        
        1. 修改 adsbygoogle 選擇器：
           - 預設: 'ins.adsbygoogle'
           - 可改為您網站的廣告容器，例如: '.ad-container', '#advertisement', '.banner'
        
        2. 修改 iframe 選擇器：
           - 預設: 'iframe'
           - 可加入更具體的選擇器，例如: 'iframe[src*="ads"]', '.ad-frame iframe'
        
        3. 修改廣告關鍵字：
           - 預設關鍵字: ['ad', 'advertisement', 'banner', 'google', 'ads']
           - 可添加您網站特有的廣告類別名稱
        
        💡 提示：啟用此調試方法可幫助您了解網站的廣告結構
        """
        print("\n=== 調試：頁面廣告元素分析 ===")
        
        ad_info = self.driver.execute_script("""
            var adInfo = {
                adsbygoogle: [],
                iframes: [],
                divs_with_ad_keywords: [],
                all_sizes: []
            };
            
            // 🔧 使用者可修改：廣告容器選擇器
            // 預設選擇器: 'ins.adsbygoogle'
            // 可修改為您網站的廣告選擇器，例如: '.ad-container', '#advertisement', '.banner'
            var adsbygoogle = document.querySelectorAll('ins.adsbygoogle');
            for (var i = 0; i < adsbygoogle.length; i++) {
                var rect = adsbygoogle[i].getBoundingClientRect();
                adInfo.adsbygoogle.push({
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    style: adsbygoogle[i].getAttribute('style') || '',
                    'data-ad-client': adsbygoogle[i].getAttribute('data-ad-client') || '',
                    'data-ad-slot': adsbygoogle[i].getAttribute('data-ad-slot') || ''
                });
            }
            
            // 檢查 iframe
            var iframes = document.querySelectorAll('iframe');
            for (var i = 0; i < iframes.length; i++) {
                var iframe = iframes[i];
                var rect = iframe.getBoundingClientRect();
                if (rect.width > 100 && rect.height > 50) { // 過濾太小的 iframe
                    adInfo.iframes.push({
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        src: iframe.src || '',
                        id: iframe.id || ''
                    });
                }
            }
            
            // 🔧 使用者可修改：廣告關鍵字檢測
            // 檢查包含廣告關鍵字的 div
            var divs = document.querySelectorAll('div');
            for (var i = 0; i < divs.length; i++) {
                var div = divs[i];
                var className = div.className || '';
                var id = div.id || '';
                // 🔧 使用者可修改：廣告關鍵字列表
                // 預設關鍵字: ['ad', 'advertisement', 'banner', 'google', 'ads']
                // 可添加您網站特有的廣告類別名稱，例如: ['sponsor', 'promo', 'commercial']
                var hasAdKeyword = ['ad', 'advertisement', 'banner', 'google', 'ads'].some(function(keyword) {
                    return className.toLowerCase().includes(keyword) || id.toLowerCase().includes(keyword);
                });
                
                if (hasAdKeyword) {
                    var rect = div.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 50) {
                        adInfo.divs_with_ad_keywords.push({
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            className: className,
                            id: id
                        });
                    }
                }
            }
            
            // 收集所有常見的廣告尺寸
            var commonAdSizes = [
                {w: 970, h: 90}, {w: 728, h: 90}, {w: 300, h: 250},
                {w: 336, h: 280}, {w: 320, h: 50}, {w: 160, h: 600},
                {w: 300, h: 600}, {w: 970, h: 250}
            ];
            
            var allElements = document.querySelectorAll('*');
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var rect = element.getBoundingClientRect();
                var width = Math.round(rect.width);
                var height = Math.round(rect.height);
                
                for (var j = 0; j < commonAdSizes.length; j++) {
                    var adSize = commonAdSizes[j];
                    if (Math.abs(width - adSize.w) <= 5 && Math.abs(height - adSize.h) <= 5) {
                        adInfo.all_sizes.push({
                            width: width,
                            height: height,
                            tagName: element.tagName,
                            className: element.className || '',
                            id: element.id || ''
                        });
                    }
                }
            }
            
            return adInfo;
        """)
        
        print(f"AdsByGoogle 元素: {len(ad_info['adsbygoogle'])} 個")
        for ad in ad_info['adsbygoogle']:
            print(f"  - {ad['width']}x{ad['height']} (client: {ad['data-ad-client']}, slot: {ad['data-ad-slot']})")
        
        print(f"Iframe 元素: {len(ad_info['iframes'])} 個")
        for iframe in ad_info['iframes']:
            print(f"  - {iframe['width']}x{iframe['height']} (id: {iframe['id']}, src: {iframe['src'][:50]}...)")
        
        print(f"包含廣告關鍵字的 Div: {len(ad_info['divs_with_ad_keywords'])} 個")
        for div in ad_info['divs_with_ad_keywords']:
            print(f"  - {div['width']}x{div['height']} (class: {div['className']}, id: {div['id']})")
        
        print(f"符合常見廣告尺寸的元素: {len(ad_info['all_sizes'])} 個")
        for element in ad_info['all_sizes']:
            print(f"  - {element['width']}x{element['height']} <{element['tagName']}> (class: {element['className']}, id: {element['id']})")
        
        print("=== 調試結束 ===\n")
    
    def get_random_news_urls(self, base_url, count=5):
        """
        獲取新聞/文章連結 - 需要根據目標網站結構修改
        
        🔧 使用者自訂指南：
        這個方法需要根據目標網站的具體結構進行客製化：
        
        1. 📝 修改 link_selectors 中的 CSS 選擇器：
           - 找到您網站的文章連結模式
           - 使用瀏覽器開發者工具檢查連結的 HTML 結構
           - 更新下方的選擇器列表
        
        2. 🌐 更新域名檢查邏輯：
           - 確保只抓取同網域的連結
           - 避免外部連結干擾
        
        3. 🎯 添加額外的過濾條件：
           - 排除不需要的頁面類型
           - 確保連結指向有廣告的頁面
        
        📋 常見的文章連結模式：
        - 部落格: a[href*='/blog/'], a[href*='/post/']
        - 新聞: a[href*='/news/'], a[href*='/article/']
        - 旅遊: a[href*='/travel/'], a[href*='/tour/']
        - 美食: a[href*='/food/'], a[href*='/restaurant/']
        - 電商: a[href*='/product/'], a[href*='/item/']
        - 論壇: a[href*='/thread/'], a[href*='/topic/']
        """
        try:
            print(f"正在訪問首頁: {base_url}")
            self.driver.get(base_url)
            time.sleep(WAIT_TIME)
            
            # 🔧 使用者必須修改：根據目標網站修改這些選擇器
            # 💡 使用瀏覽器開發者工具 (F12) 檢查您網站的連結結構
            # 💡 右鍵點擊文章連結 → 檢查元素 → 複製選擇器
            link_selectors = [
                # 📰 通用文章連結模式
                "a[href*='/article/']",  # 一般文章連結
                "a[href*='/news/']",     # 新聞連結
                "a[href*='/blog/']",     # 部落格連結
                "a[href*='/post/']",     # 貼文連結
                
                # 🏷️ 特定主題連結
                "a[href*='/tour/']",     # 旅遊連結
                "a[href*='/travel/']",   # 旅行連結
                "a[href*='/activity/']", # 活動連結
                "a[href*='/food/']",     # 美食連結
                
                # 🔧 使用者自訂區域 - 請根據您的網站添加更多選擇器
                # 範例：
                # "a.article-link",           # 有 article-link 類別的連結
                # ".news-item a",             # news-item 容器內的連結
                # "h2 a",                     # 標題內的連結
                # ".post-title a",            # 文章標題連結
                # "[data-post-id] a",         # 有 data-post-id 屬性的連結
                # "a[href*='/product/']",     # 產品頁面連結
                # "a[href*='/review/']",      # 評論頁面連結
            ]
            
            news_urls = []
            
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if DEBUG_MODE:
                        print(f"使用選擇器 '{selector}' 找到 {len(links)} 個連結")
                    
                    for link in links:
                        href = link.get_attribute('href')
                        if href and href not in news_urls:
                            # 動態域名檢查 - 從 base_url 提取域名
                            from urllib.parse import urlparse
                            base_domain = urlparse(base_url).netloc
                            domain_check = any(domain in href for domain in [
                                base_domain,  # 主域名
                                base_domain.replace('www.', ''),  # 去掉 www
                                # 🔧 如需支援特定子域名，請在此添加
                                # 例如: 'news.' + base_domain.replace('www.', '')
                            ])
                            
                            if domain_check and href != base_url:
                                news_urls.append(href)
                                
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"處理選擇器 '{selector}' 時發生錯誤: {e}")
                    continue
            
            print(f"總共找到 {len(news_urls)} 個有效連結")
            
            # 隨機選擇指定數量的連結
            if len(news_urls) > count:
                selected_urls = random.sample(news_urls, count)
            else:
                selected_urls = news_urls
                
            print(f"選擇了 {len(selected_urls)} 個連結進行處理")
            return selected_urls
            
        except Exception as e:
            print(f"獲取新聞連結失敗: {e}")
            return []
    
    def remove_fullscreen_ads(self):
        """移除佔據整個畫面的廣告"""
        try:
            print("檢查並移除全螢幕廣告...")
            
            # 移除常見的全螢幕廣告元素
            removed_count = self.driver.execute_script("""
                var removedCount = 0;
                
                // 🔧 使用者可修改：全螢幕廣告選擇器
                // 💡 如果程式無法移除您網站的彈出廣告，請添加對應的選擇器
                var fullscreenAdSelectors = [
                    // 覆蓋整個螢幕的元素
                    'div[style*="position: fixed"][style*="z-index"]',
                    'div[style*="position: absolute"][style*="width: 100%"][style*="height: 100%"]',
                    
                    // 常見的廣告覆蓋層
                    '.overlay',
                    '.modal-overlay',
                    '.popup-overlay',
                    '.ad-overlay',
                    '.interstitial',
                    
                    // Google 廣告相關
                    'div[id*="google_ads_iframe"]',
                    'ins.adsbygoogle[style*="position: fixed"]',
                    
                    // 其他可能的全螢幕廣告
                    '[class*="fullscreen"]',
                    '[class*="popup"]',
                    '[id*="popup"]',
                    '[class*="modal"][style*="display: block"]',
                    
                    // 🔧 使用者自訂區域 - 請根據您網站的彈出廣告添加選擇器
                    // 範例：
                    // '.your-popup-class',        # 您網站的彈出視窗類別
                    // '#your-modal-id',           # 您網站的模態視窗 ID
                    // '.advertisement-popup',     # 廣告彈出視窗
                    // '[data-popup="true"]',      # 有彈出屬性的元素
                ];
                
                fullscreenAdSelectors.forEach(function(selector) {
                    try {
                        var elements = document.querySelectorAll(selector);
                        for (var i = 0; i < elements.length; i++) {
                            var element = elements[i];
                            var rect = element.getBoundingClientRect();
                            var style = window.getComputedStyle(element);
                            
                            // 檢查是否為全螢幕或大尺寸元素
                            var isFullscreen = (
                                (rect.width >= window.innerWidth * 0.8 && rect.height >= window.innerHeight * 0.8) ||
                                (style.position === 'fixed' && (
                                    (style.top === '0px' || style.top === '0') &&
                                    (style.left === '0px' || style.left === '0') &&
                                    (rect.width >= window.innerWidth * 0.5 || rect.height >= window.innerHeight * 0.5)
                                ))
                            );
                            
                            if (isFullscreen && style.display !== 'none') {
                                console.log('移除全螢幕廣告:', element);
                                element.style.display = 'none';
                                element.remove();
                                removedCount++;
                            }
                        }
                    } catch (e) {
                        console.log('處理選擇器失敗:', selector, e);
                    }
                });
                
                // 移除可能阻擋內容的遮罩
                var body = document.body;
                if (body.style.overflow === 'hidden') {
                    body.style.overflow = 'auto';
                    console.log('恢復頁面滾動');
                }
                
                return removedCount;
            """)
            
            if removed_count > 0:
                print(f"✅ 成功移除 {removed_count} 個全螢幕廣告")
                time.sleep(1)  # 等待頁面重新渲染
            else:
                print("未發現全螢幕廣告")
                
        except Exception as e:
            print(f"移除全螢幕廣告失敗: {e}")
    
    def scan_entire_page_for_ads(self, target_width, target_height):
        """
        掃描整個網頁尋找符合尺寸的廣告元素
        
        🔧 使用者自訂指南：
        如果程式找不到您網站的廣告，可能需要調整以下設定：
        
        1. 📏 廣告尺寸設定 (在 config.py 或 default_config.py)：
           - 修改 TARGET_AD_SIZES 列表
           - 添加您網站實際使用的廣告尺寸
           - 使用瀏覽器開發者工具測量廣告實際尺寸
        
        2. 🎯 廣告元素選擇策略：
           - 程式會掃描所有可見元素
           - 尋找尺寸完全匹配的元素
           - 如果尺寸不匹配，可能需要調整容差範圍
        
        3. 🔍 調試建議：
           - 啟用 debug_page_ads() 方法查看頁面廣告結構
           - 檢查廣告是否為動態載入 (需要等待時間)
           - 確認廣告元素是否可見且未被隱藏
        """
        if DEBUG_MODE:
            print(f"開始掃描整個網頁尋找 {target_width}x{target_height} 的廣告...")
        
        # 獲取所有可見的元素
        all_elements = self.driver.execute_script("""
            function getAllVisibleElements() {
                var all = [];
                var walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    {
                        acceptNode: function(node) {
                            // 只接受可見的元素
                            var style = window.getComputedStyle(node);
                            if (style.display === 'none' || 
                                style.visibility === 'hidden' || 
                                style.opacity === '0') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                
                var node;
                while (node = walker.nextNode()) {
                    all.push(node);
                }
                return all;
            }
            return getAllVisibleElements();
        """)
        
        print(f"找到 {len(all_elements)} 個可見元素，開始檢查尺寸...")
        
        matching_elements = []
        
        for i, element in enumerate(all_elements):
            try:
                # 檢查元素尺寸
                size_info = self.driver.execute_script("""
                    var element = arguments[0];
                    var rect = element.getBoundingClientRect();
                    return {
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: rect.top,
                        left: rect.left,
                        visible: rect.width > 0 && rect.height > 0
                    };
                """, element)
                
                if (size_info and 
                    size_info['visible'] and
                    size_info['width'] == target_width and 
                    size_info['height'] == target_height):
                    
                    # 進一步檢查是否可能是廣告（與 ad_replacer.py 一致）
                    is_ad = self.driver.execute_script("""
                        var element = arguments[0];
                        var tagName = element.tagName.toLowerCase();
                        var className = element.className || '';
                        var id = element.id || '';
                        var src = element.src || '';
                        
                        // 檢查是否包含廣告相關的關鍵字
                        var adKeywords = ['ad', 'advertisement', 'banner', 'google', 'ads', 'ad-', '-ad'];
                        var hasAdKeyword = adKeywords.some(function(keyword) {
                            return className.toLowerCase().includes(keyword) ||
                                   id.toLowerCase().includes(keyword) ||
                                   src.toLowerCase().includes(keyword);
                        });
                        
                        // 檢查是否為圖片、iframe 或 div
                        var isImageElement = tagName === 'img' || tagName === 'iframe' || tagName === 'div';
                        
                        // 檢查是否有背景圖片
                        var style = window.getComputedStyle(element);
                        var hasBackgroundImage = style.backgroundImage && style.backgroundImage !== 'none';
                        
                        return hasAdKeyword || isImageElement || hasBackgroundImage;
                    """, element)
                    
                    if is_ad:
                        matching_elements.append({
                            'element': element,
                            'width': size_info['width'],
                            'height': size_info['height'],
                            'position': f"top:{size_info['top']:.0f}, left:{size_info['left']:.0f}"
                        })
                        if DEBUG_MODE:
                            print(f"找到符合尺寸的廣告元素: {size_info['width']}x{size_info['height']} at {size_info['top']:.0f},{size_info['left']:.0f}")
                
                # 每檢查100個元素顯示進度
                if (i + 1) % 100 == 0:
                    if DEBUG_MODE:
                        print(f"已檢查 {i + 1}/{len(all_elements)} 個元素...")
                    
            except Exception as e:
                continue
        
        if DEBUG_MODE:
            print(f"掃描完成，找到 {len(matching_elements)} 個符合尺寸的廣告元素")
        return matching_elements
    
    def get_button_style(self):
        """根據配置返回按鈕樣式"""
        button_style = getattr(self, 'button_style', BUTTON_STYLE)
        
        # 預先定義的按鈕樣式
        # 統一的資訊按鈕樣式 - 使用 Google 標準設計
        unified_info_button = {
            "html": '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 1.5a6 6 0 100 12 6 6 0 100-12m0 1a5 5 0 110 10 5 5 0 110-10zM6.625 11h1.75V6.5h-1.75zM7.5 3.75a1 1 0 100 2 1 1 0 100-2z" fill="#00aecd"/></svg>',
            "style": 'position:absolute;top:0px;right:17px;width:15px;height:15px;z-index:100;display:block;background-color:rgba(255,255,255,1);border-radius:2px;cursor:pointer;'
        }
        
        button_styles = {
            "dots": {
                "close_button": {
                    "html": '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="7.5" cy="3.5" r="1.5" fill="#00aecd"/><circle cx="7.5" cy="7.5" r="1.5" fill="#00aecd"/><circle cx="7.5" cy="11.5" r="1.5" fill="#00aecd"/></svg>',
                    "style": 'position:absolute;top:0px;right:0px;width:15px;height:15px;z-index:101;display:block;background-color:rgba(255,255,255,1);border-radius:2px;cursor:pointer;'
                },
                "info_button": unified_info_button
            },
            "cross": {
                "close_button": {
                    "html": '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 4L11 11M11 4L4 11" stroke="#00aecd" stroke-width="1.5" stroke-linecap="round"/></svg>',
                    "style": 'position:absolute;top:0px;right:0px;width:15px;height:15px;z-index:101;display:block;background-color:rgba(255,255,255,1);border-radius:2px;cursor:pointer;'
                },
                "info_button": unified_info_button
            },
            "adchoices": {
                "close_button": {
                    "html": '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 4L11 11M11 4L4 11" stroke="#00aecd" stroke-width="1.5" stroke-linecap="round"/></svg>',
                    "style": 'position:absolute;top:0px;right:0px;width:15px;height:15px;z-index:101;display:block;background-color:rgba(255,255,255,1);border-radius:2px;cursor:pointer;'
                },
                "info_button": {
                    "html": '<img src="https://tpc.googlesyndication.com/pagead/images/adchoices/adchoices_blue_wb.png" width="15" height="15" style="display:block;width:15px;height:15px;">',
                    "style": 'position:absolute;top:0px;right:17px;width:15px;height:15px;z-index:100;display:block;cursor:pointer;'
                }
            },
            "adchoices_dots": {
                "close_button": {
                    "html": '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="7.5" cy="3.5" r="1.5" fill="#00aecd"/><circle cx="7.5" cy="7.5" r="1.5" fill="#00aecd"/><circle cx="7.5" cy="11.5" r="1.5" fill="#00aecd"/></svg>',
                    "style": 'position:absolute;top:0px;right:0px;width:15px;height:15px;z-index:101;display:block;background-color:rgba(255,255,255,1);border-radius:2px;cursor:pointer;'
                },
                "info_button": {
                    "html": '<img src="https://tpc.googlesyndication.com/pagead/images/adchoices/adchoices_blue_wb.png" width="15" height="15" style="display:block;width:15px;height:15px;">',
                    "style": 'position:absolute;top:0px;right:17px;width:15px;height:15px;z-index:100;display:block;cursor:pointer;'
                }
            },
            "none": {
                "close_button": {
                    "html": '',
                    "style": 'display:none;'
                },
                "info_button": {
                    "html": '',
                    "style": 'display:none;'
                }
            }
        }
        
        return button_styles.get(button_style, button_styles["dots"])

    def replace_ad_content(self, element, image_data, target_width, target_height):
        try:
            # 獲取原始尺寸
            original_info = self.driver.execute_script("""
                var element = arguments[0];
                if (!element || !element.getBoundingClientRect) return null;
                var rect = element.getBoundingClientRect();
                return {width: rect.width, height: rect.height};
            """, element)
            
            if not original_info:
                return False
            
            # 檢查是否符合目標尺寸（精確匹配，與 ad_replacer.py 一致）
            if (original_info['width'] != target_width or 
                original_info['height'] != target_height):
                return False
            
            # 獲取按鈕樣式
            button_style = self.get_button_style()
            close_button_html = button_style["close_button"]["html"]
            close_button_style = button_style["close_button"]["style"]
            info_button_html = button_style["info_button"]["html"]
            info_button_style = button_style["info_button"]["style"]
            
            # 只替換圖片，保留廣告按鈕
            success = self.driver.execute_script("""
                // 添加 Google 廣告標準樣式
                if (!document.getElementById('google_ad_styles')) {
                    var style = document.createElement('style');
                    style.id = 'google_ad_styles';
                    style.textContent = `
                        div {
                            margin: 0;
                            padding: 0;
                        }
                        .abgb {
                            position: absolute;
                            right: 16px;
                            top: 0px;
                        }
                        .abgb {
                            display: inline-block;
                            height: 15px;
                        }
                        .abgc {
                            cursor: pointer;
                        }
                        .abgc {
                            display: block;
                            height: 15px;
                            position: absolute;
                            right: 1px;
                            top: 1px;
                            text-rendering: geometricPrecision;
                            z-index: 2147483646;
                        }
                        .abgc .il-wrap {
                            background-color: #ffffff;
                            height: 15px;
                            white-space: nowrap;
                        }
                        .abgc .il-icon {
                            height: 15px;
                            width: 15px;
                        }
                        .abgc .il-icon svg {
                            fill: #00aecd;
                        }
                        .abgs svg, .abgb svg {
                            display: inline-block;
                            height: 15px;
                            width: 15px;
                            vertical-align: top;
                        }
                        #close_button { 
                            text-decoration: none; 
                            margin: 0; 
                            padding: 0; 
                            border: none;
                            cursor: pointer;
                            position: absolute; 
                            z-index: 100; 
                            top: 0px;
                            bottom: auto;
                            vertical-align: top;
                            margin-top: 1px;
                            right: 0px;
                            left: auto;
                            text-align: right;
                            margin-right: 1px;
                            display: block; 
                            width: 15px; 
                            height: 15px;
                        }
                        #close_button #close_button_svg { 
                            width: 15px; 
                            height: 15px; 
                            line-height: 0;
                        }
                        #abgb #info_button_svg { 
                            width: 15px; 
                            height: 15px; 
                            line-height: 0;
                        }
                    `;
                    document.head.appendChild(style);
                }
                
                var container = arguments[0];
                var imageBase64 = arguments[1];
                var targetWidth = arguments[2];
                var targetHeight = arguments[3];
                var closeButtonHtml = arguments[4];
                var closeButtonStyle = arguments[5];
                var infoButtonHtml = arguments[6];
                var infoButtonStyle = arguments[7];
                var isNoneMode = arguments[8];
                
                if (!container) return false;
                
                // 確保 container 是 relative
                if (window.getComputedStyle(container).position === 'static') {
                  container.style.position = 'relative';
                }
                // 先移除舊的（避免重複）
                ['close_button', 'abgb'].forEach(function(id){
                  var old = container.querySelector('#'+id);
                  if(old) old.remove();
                });
                
                var replacedCount = 0;
                var newImageSrc = 'data:image/png;base64,' + imageBase64;
                
                // 方法1: 只替換img標籤的src，不移除元素
                var imgs = container.querySelectorAll('img');
                for (var i = 0; i < imgs.length; i++) {
                    var img = imgs[i];
                    // 排除Google廣告控制按鈕
                    var imgRect = img.getBoundingClientRect();
                    var isControlButton = imgRect.width < 50 || imgRect.height < 50 || 
                                         img.className.includes('abg') || 
                                         img.id.includes('abg') ||
                                         img.src.includes('googleads') ||
                                         img.src.includes('googlesyndication') ||
                                         img.src.includes('adchoices') ||
                                         img.src.includes('zh_tw.png') ||
                                         img.closest('#abgcp') ||
                                         img.closest('.abgcp') ||
                                         img.closest('#abgc') ||
                                         img.closest('.abgc') ||
                                         img.closest('#abgb') ||
                                         img.closest('.abgb') ||
                                         img.closest('#abgs') ||
                                         img.closest('.abgs') ||
                                         img.closest('#cbb') ||
                                         img.closest('.cbb') ||
                                         img.closest('label.cbb') ||
                                         img.closest('[data-vars-label*="feedback"]') ||
                                         img.alt.includes('關閉') ||
                                         img.alt.includes('close');
                    
                    if (!isControlButton && img.src && !img.src.startsWith('data:')) {
                        // 保存原始src以便復原
                        if (!img.getAttribute('data-original-src')) {
                            img.setAttribute('data-original-src', img.src);
                        }
                        
                        // 嘗試替換圖片
                        var oldSrc = img.src;
                        img.src = newImageSrc;
                        
                        // 等待圖片載入並驗證
                        var imageLoaded = false;
                        try {
                            // 檢查圖片是否成功載入
                            if (img.complete && img.naturalWidth > 0) {
                                imageLoaded = true;
                            } else {
                                // 如果圖片未載入，恢復原始圖片
                                img.src = oldSrc;
                            }
                        } catch (e) {
                            // 載入失敗，恢復原始圖片
                            img.src = oldSrc;
                        }
                        
                        // 只有在圖片成功載入時才繼續
                        if (imageLoaded || newImageSrc.startsWith('data:')) {
                            // 設定圖片樣式
                            img.style.objectFit = 'contain';
                            img.style.width = '100%';
                            img.style.height = 'auto';
                            img.style.maxWidth = 'none';
                            img.style.maxHeight = 'none';
                            img.style.minWidth = 'auto';
                            img.style.minHeight = 'auto';
                            img.style.display = 'block';
                            img.style.margin = '0';
                            img.style.padding = '0';
                            img.style.border = 'none';
                            img.style.outline = 'none';
                            
                            // 確保img的父層是relative
                            var imgParent = img.parentElement || container;
                            if (window.getComputedStyle(imgParent).position === 'static') {
                                imgParent.style.position = 'relative';
                            }
                            
                            // 先移除舊的按鈕
                            ['close_button', 'abgb'].forEach(function(id){
                                var old = imgParent.querySelector('#'+id);
                                if(old) old.remove();
                            });
                            
                            // 只有在非 none 模式下才創建按鈕
                            if (!isNoneMode && closeButtonHtml && infoButtonHtml) {
                                // 叉叉 - 貼著替換圖片的右上角
                                var closeButton = document.createElement('div');
                                closeButton.id = 'close_button';
                                closeButton.innerHTML = closeButtonHtml;
                                closeButton.style.cssText = closeButtonStyle;
                                
                                // 驚嘆號 - 貼著替換圖片的右上角，與叉叉對齊
                                var abgb = document.createElement('div');
                                abgb.id = 'abgb';
                                abgb.className = 'abgb';
                                abgb.innerHTML = infoButtonHtml;
                                abgb.style.cssText = infoButtonStyle;
                                
                                // 將按鈕添加到img的父層（驚嘆號在左，叉叉在右）
                                imgParent.appendChild(abgb);
                                imgParent.appendChild(closeButton);
                            }
                            
                            // 只有成功替換才計數
                            replacedCount++;
                        }
                    }
                }
                
                // 方法2: 處理iframe
                var iframes = container.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    var iframe = iframes[i];
                    var iframeRect = iframe.getBoundingClientRect();
                    
                    // 隱藏iframe
                    iframe.style.visibility = 'hidden';
                    
                    // 確保容器是relative
                    if (window.getComputedStyle(container).position === 'static') {
                        container.style.position = 'relative';
                    }
                    
                    // 在iframe位置創建新的圖片元素
                    var newImg = document.createElement('img');
                    newImg.src = newImageSrc;
                    newImg.style.position = 'absolute';
                    newImg.style.top = (iframeRect.top - container.getBoundingClientRect().top) + 'px';
                    newImg.style.left = (iframeRect.left - container.getBoundingClientRect().left) + 'px';
                    newImg.style.width = Math.round(iframeRect.width) + 'px';
                    newImg.style.height = Math.round(iframeRect.height) + 'px';
                    newImg.style.objectFit = 'contain';
                    newImg.style.zIndex = '1';
                    
                    container.appendChild(newImg);
                    
                    // 先移除舊的按鈕
                    ['close_button', 'abgb'].forEach(function(id){
                        var old = container.querySelector('#'+id);
                        if(old) old.remove();
                    });
                    
                    // 只有在非 none 模式下才創建按鈕
                    if (!isNoneMode && closeButtonHtml && infoButtonHtml) {
                        // 叉叉 - 貼著替換圖片的右上角
                        var closeButton = document.createElement('div');
                        closeButton.id = 'close_button';
                        closeButton.innerHTML = closeButtonHtml;
                        closeButton.style.cssText = 'position:absolute;top:' + (iframeRect.top - container.getBoundingClientRect().top) + 'px;right:' + (container.getBoundingClientRect().right - iframeRect.right) + 'px;width:15px;height:15px;z-index:100;display:block;background-color:rgba(255,255,255,1);';
                        
                        // 驚嘆號 - 貼著替換圖片的右上角，與叉叉水平對齊
                        var abgb = document.createElement('div');
                        abgb.id = 'abgb';
                        abgb.className = 'abgb';
                        abgb.innerHTML = infoButtonHtml;
                        abgb.style.cssText = 'position:absolute;top:' + (iframeRect.top - container.getBoundingClientRect().top + 1) + 'px;right:' + (container.getBoundingClientRect().right - iframeRect.right + 17) + 'px;width:15px;height:15px;z-index:100;display:block;background-color:rgba(255,255,255,1);line-height:0;';
                        
                        // 將按鈕添加到container內，與圖片同層
                        container.appendChild(abgb);
                        container.appendChild(closeButton);
                    }
                    replacedCount++;
                }
                
                // 方法3: 處理背景圖片
                if (replacedCount === 0) {
                    var style = window.getComputedStyle(container);
                    if (style.backgroundImage && style.backgroundImage !== 'none') {
                        container.style.backgroundImage = 'url(' + newImageSrc + ')';
                        container.style.backgroundSize = 'contain';
                        container.style.backgroundRepeat = 'no-repeat';
                        container.style.backgroundPosition = 'center';
                        replacedCount = 1;
                        
                        // 確保容器是relative
                        if (window.getComputedStyle(container).position === 'static') {
                            container.style.position = 'relative';
                        }
                        
                        // 先移除舊的按鈕
                        ['close_button', 'abgb'].forEach(function(id){
                            var old = container.querySelector('#'+id);
                            if(old) old.remove();
                        });
                        
                        // 只有在非 none 模式下才創建按鈕
                        if (!isNoneMode && closeButtonHtml && infoButtonHtml) {
                            // 添加兩個按鈕 - 貼著替換圖片的右上角，水平對齊
                            var closeButton = document.createElement('div');
                            closeButton.id = 'close_button';
                            closeButton.innerHTML = closeButtonHtml;
                            closeButton.style.cssText = closeButtonStyle;
                            
                            var abgb = document.createElement('div');
                            abgb.id = 'abgb';
                            abgb.className = 'abgb';
                            abgb.innerHTML = infoButtonHtml;
                            abgb.style.cssText = infoButtonStyle;
                            
                            // 將按鈕添加到container內，與背景圖片同層
                            container.appendChild(abgb);
                            container.appendChild(closeButton);
                        }
                    }
                }
                return replacedCount > 0;
            """, element, image_data, target_width, target_height, close_button_html, close_button_style, info_button_html, info_button_style, False)
            
            if success:
                print(f"替換廣告 {original_info['width']}x{original_info['height']}")
                return True
            else:
                print(f"廣告替換失敗 {original_info['width']}x{original_info['height']}")
                return False
                
        except Exception as e:
            print(f"替換廣告失敗: {e}")
            return False
    
    def process_website(self, url):
        """處理單個網站，遍歷所有替換圖片"""
        try:
            print(f"\n開始處理網站: {url}")
            
            # 載入網頁
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            self.driver.get(url)
            
            # 等待頁面基本載入
            time.sleep(WAIT_TIME)
            
            # 等待頁面完全載入
            self.driver.execute_script("return document.readyState") == "complete"
            
            # 移除可能的全螢幕廣告
            self.remove_fullscreen_ads()
            
            # 額外等待 GDN 廣告載入
            print("等待 GDN 廣告載入...")
            time.sleep(5)
            
            # 滾動頁面以觸發懶載入的廣告
            print("滾動頁面以觸發廣告載入...")
            self.driver.execute_script("""
                // 滾動到頁面底部
                window.scrollTo(0, document.body.scrollHeight);
            """)
            time.sleep(2)
            
            # 滾動回頂部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # 如果啟用調試模式，顯示頁面廣告分析
            if DEBUG_MODE:
                self.debug_page_ads()
            
            # 遍歷所有替換圖片
            total_replacements = 0
            screenshot_paths = []  # 儲存所有截圖路徑
            
            for image_info in self.replace_images:
                print(f"\n檢查圖片: {image_info['filename']} ({image_info['width']}x{image_info['height']})")
                
                # 載入當前圖片
                try:
                    image_data = self.load_image_base64(image_info['path'])
                except Exception as e:
                    print(f"載入圖片失敗: {e}")
                    continue
                
                # 掃描網頁尋找符合尺寸的廣告
                matching_elements = self.scan_entire_page_for_ads(image_info['width'], image_info['height'])
                
                if not matching_elements:
                    print(f"未找到符合 {image_info['width']}x{image_info['height']} 尺寸的廣告位置")
                    continue
                
                # 嘗試替換找到的廣告
                replaced = False
                processed_positions = set()  # 記錄已處理的位置
                for ad_info in matching_elements:
                    # 檢查是否已經處理過這個位置
                    position_key = f"{ad_info['position']}_{image_info['width']}x{image_info['height']}"
                    if position_key in processed_positions:
                        print(f"跳過已處理的位置: {ad_info['position']}")
                        continue
                        
                    try:
                        if self.replace_ad_content(ad_info['element'], image_data, image_info['width'], image_info['height']):
                            print(f"成功替換廣告: {ad_info['width']}x{ad_info['height']} at {ad_info['position']}")
                            replaced = True
                            total_replacements += 1
                            processed_positions.add(position_key)  # 記錄已處理的位置
                            
                            # 滾動到廣告位置確保可見
                            try:
                                # 獲取廣告元素的位置
                                element_rect = self.driver.execute_script("""
                                    var element = arguments[0];
                                    var rect = element.getBoundingClientRect();
                                    return {
                                        top: rect.top + window.pageYOffset,
                                        left: rect.left + window.pageXOffset,
                                        width: rect.width,
                                        height: rect.height
                                    };
                                """, ad_info['element'])
                                
                                # 計算滾動位置，讓廣告出現在螢幕上方 30% 的位置
                                viewport_height = self.driver.execute_script("return window.innerHeight;")
                                scroll_position = element_rect['top'] - (viewport_height * 0.3)
                                
                                # 滾動到廣告位置
                                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                                print(f"滾動到廣告位置: {scroll_position:.0f}px")
                                
                                # 等待滾動完成
                                time.sleep(1)
                                
                            except Exception as e:
                                print(f"滾動到廣告位置失敗: {e}")
                            
                            # 每次替換後立即截圖
                            print("準備截圖...")
                            time.sleep(2)  # 等待頁面穩定
                            screenshot_path = self.take_screenshot()
                            if screenshot_path:
                                screenshot_paths.append(screenshot_path)
                                print(f"✅ 截圖保存: {screenshot_path}")
                            else:
                                print("❌ 截圖失敗")
                            
                            # 截圖後復原該位置的廣告
                            try:
                                self.driver.execute_script("""
                                    var container = arguments[0];
                                    
                                    // 移除我們添加的所有按鈕（在整個容器中搜尋）
                                    var closeButtons = container.querySelectorAll('#close_button');
                                    var infoButtons = container.querySelectorAll('#abgb');
                                    
                                    closeButtons.forEach(function(btn) { btn.remove(); });
                                    infoButtons.forEach(function(btn) { btn.remove(); });
                                    
                                    // 復原所有被修改的圖片
                                    var modifiedImgs = container.querySelectorAll('img[data-original-src]');
                                    modifiedImgs.forEach(function(img) {
                                        var originalSrc = img.getAttribute('data-original-src');
                                        if (originalSrc) {
                                            img.src = originalSrc;
                                            img.removeAttribute('data-original-src');
                                            // 清除我們添加的樣式
                                            img.style.objectFit = '';
                                            img.style.width = '';
                                            img.style.height = '';
                                            img.style.maxWidth = '';
                                            img.style.maxHeight = '';
                                            img.style.minWidth = '';
                                            img.style.minHeight = '';
                                            img.style.display = '';
                                            img.style.margin = '';
                                            img.style.padding = '';
                                            img.style.border = '';
                                            img.style.outline = '';
                                        }
                                    });
                                    
                                    // 復原iframe可見性
                                    var hiddenIframes = container.querySelectorAll('iframe[style*="visibility: hidden"]');
                                    hiddenIframes.forEach(function(iframe) {
                                        iframe.style.visibility = 'visible';
                                    });
                                """, ad_info['element'])
                                print("✅ 廣告位置已復原")
                            except Exception as e:
                                print(f"復原廣告失敗: {e}")
                            
                            # 繼續尋找下一個廣告位置，不要break
                            continue
                    except Exception as e:
                        print(f"替換廣告失敗: {e}")
                        continue
                
                if not replaced:
                    print(f"所有找到的 {image_info['width']}x{image_info['height']} 廣告位置都無法替換")
            
            # 總結處理結果
            if total_replacements > 0:
                print(f"\n{'='*50}")
                print(f"網站處理完成！總共成功替換了 {total_replacements} 個廣告")
                

                
                print(f"截圖檔案:")
                for i, path in enumerate(screenshot_paths, 1):
                    print(f"  {i}. {path}")
                print(f"{'='*50}")
                return screenshot_paths
            else:
                print("本網頁沒有找到任何可替換的廣告")
                return []
                
        except Exception as e:
            print(f"處理網站失敗: {e}")
            return []
    
    def take_screenshot(self):
        if not os.path.exists(SCREENSHOT_FOLDER):
            os.makedirs(SCREENSHOT_FOLDER)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{SCREENSHOT_FOLDER}/ad_{timestamp}.png"
        
        try:
            time.sleep(1)  # 等待頁面穩定
            
            system = platform.system()
            
            if system == "Windows":
                # Windows 多螢幕截圖 - 使用更可靠的方法
                try:
                    # 方法1: 嘗試使用 PIL 和 win32gui (如果可用)
                    try:
                        import win32gui
                        import win32con
                        from PIL import ImageGrab
                        
                        # 獲取所有螢幕的資訊
                        def enum_display_monitors():
                            monitors = []
                            def callback(hmonitor, hdc, rect, data):
                                monitors.append({
                                    'left': rect[0], 'top': rect[1], 
                                    'right': rect[2], 'bottom': rect[3],
                                    'width': rect[2] - rect[0], 'height': rect[3] - rect[1]
                                })
                                return True
                            win32gui.EnumDisplayMonitors(None, None, callback, None)
                            return monitors
                        
                        monitors = enum_display_monitors()
                        print(f"偵測到 {len(monitors)} 個螢幕")
                        
                        if self.screen_id <= len(monitors):
                            monitor = monitors[self.screen_id - 1]
                            bbox = (monitor['left'], monitor['top'], monitor['right'], monitor['bottom'])
                            screenshot = ImageGrab.grab(bbox)
                            screenshot.save(filepath)
                            print(f"使用 PIL 截圖 (螢幕 {self.screen_id}): {monitor}")
                            return filepath
                        else:
                            # 螢幕 ID 超出範圍，使用主螢幕
                            screenshot = ImageGrab.grab()
                            screenshot.save(filepath)
                            print(f"螢幕 ID 超出範圍，使用主螢幕截圖")
                            return filepath
                            
                    except ImportError:
                        print("win32gui 或 PIL 未安裝，嘗試 pyautogui")
                        
                        # 直接使用 MSS 庫 - 最可靠的多螢幕截圖方法
                        import mss
                        with mss.mss() as sct:
                            monitors = sct.monitors
                            print(f"MSS 偵測到 {len(monitors)-1} 個螢幕: {monitors}")
                            
                            # MSS monitors[0] 是所有螢幕的組合，實際螢幕從 monitors[1] 開始
                            # 所以 screen_id=1 對應 monitors[1]，screen_id=2 對應 monitors[2]
                            if self.screen_id < len(monitors):
                                # 截取指定螢幕 (screen_id 直接對應 monitors 索引)
                                monitor = monitors[self.screen_id]
                                screenshot_mss = sct.grab(monitor)
                                
                                # 轉換為 PIL Image
                                from PIL import Image
                                screenshot = Image.frombytes('RGB', screenshot_mss.size, screenshot_mss.bgra, 'raw', 'BGRX')
                                print(f"✅ 使用 MSS 截取螢幕 {self.screen_id}: {monitor}")
                                print(f"   截圖尺寸: {screenshot.size}")
                            else:
                                # 螢幕 ID 超出範圍，使用主螢幕
                                monitor = monitors[1]  # 主螢幕
                                screenshot_mss = sct.grab(monitor)
                                from PIL import Image
                                screenshot = Image.frombytes('RGB', screenshot_mss.size, screenshot_mss.bgra, 'raw', 'BGRX')
                                print(f"⚠️ 螢幕 {self.screen_id} 不存在，使用主螢幕: {monitor}")
                        
                        screenshot.save(filepath)
                        print(f"✅ MSS 截圖保存 (螢幕 {self.screen_id}): {filepath}")
                        return filepath
                        
                except ImportError:
                    print("❌ MSS 未安裝，使用 pyautogui 備用方案")
                    try:
                        import pyautogui
                        screenshot = pyautogui.screenshot()
                        screenshot.save(filepath)
                        print(f"✅ pyautogui 截圖保存: {filepath}")
                        return filepath
                    except:
                        print("pyautogui 也失敗，使用 Selenium 截圖")
                        self.driver.save_screenshot(filepath)
                        print(f"截圖保存: {filepath}")
                        return filepath
                except Exception as e:
                    print(f"❌ MSS 截圖失敗: {e}")
                    import traceback
                    traceback.print_exc()
                    print("使用 pyautogui 備用方案")
                    try:
                        import pyautogui
                        screenshot = pyautogui.screenshot()
                        screenshot.save(filepath)
                        print(f"✅ pyautogui 截圖保存: {filepath}")
                        return filepath
                    except:
                        print("pyautogui 也失敗，使用 Selenium 截圖")
                        self.driver.save_screenshot(filepath)
                        print(f"截圖保存: {filepath}")
                        return filepath
                    
            elif system == "Darwin":  # macOS
                # macOS 多螢幕截圖
                try:
                    # 使用 screencapture 的 -D 參數指定螢幕
                    result = subprocess.run([
                        'screencapture', 
                        '-D', str(self.screen_id),  # 指定螢幕編號
                        filepath
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(filepath):
                        print(f"截圖保存 (螢幕 {self.screen_id}): {filepath}")
                        return filepath
                    else:
                        print(f"指定螢幕 {self.screen_id} 截圖失敗，嘗試全螢幕截圖")
                        # 回退到全螢幕截圖
                        result = subprocess.run([
                            'screencapture', 
                            filepath
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0 and os.path.exists(filepath):
                            print(f"截圖保存 (全螢幕): {filepath}")
                            return filepath
                        else:
                            raise Exception("screencapture 命令失敗")
                            
                except Exception as e:
                    print(f"系統截圖失敗: {e}，使用 Selenium 截圖")
                    self.driver.save_screenshot(filepath)
                    print(f"截圖保存: {filepath}")
                    return filepath
                    
            else:  # Linux
                # Linux 多螢幕截圖
                try:
                    # 使用 import 命令截取指定螢幕
                    display = f":0.{self.screen_id - 1}" if self.screen_id > 1 else ":0"
                    result = subprocess.run([
                        'import', 
                        '-window', 'root',
                        '-display', display,
                        filepath
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(filepath):
                        print(f"截圖保存 (螢幕 {self.screen_id}): {filepath}")
                        return filepath
                    else:
                        raise Exception("import 命令失敗")
                        
                except Exception as e:
                    print(f"系統截圖失敗: {e}，使用 Selenium 截圖")
                    self.driver.save_screenshot(filepath)
                    print(f"截圖保存: {filepath}")
                    return filepath
                
        except Exception as e:
            print(f"截圖失敗: {e}")
            import traceback
            traceback.print_exc()
            print("使用 Selenium 截圖")
            try:
                self.driver.save_screenshot(filepath)
                print(f"截圖保存: {filepath}")
                return filepath
            except Exception as e2:
                print(f"Selenium 截圖也失敗: {e2}")
                import traceback
                traceback.print_exc()
                return None
    
    def close(self):
        self.driver.quit()

def main():
    # 偵測並選擇螢幕
    screen_id, selected_screen = ScreenManager.select_screen()
    
    if screen_id is None:
        print("未選擇螢幕，程式結束")
        return
    
    # 使用設定的 BASE_URL
    base_url = BASE_URL
    
    print(f"目標網站: {base_url}")
    print(f"\n正在啟動 Chrome 瀏覽器到螢幕 {screen_id}...")
    
    bot = WebsiteAdReplacer(screen_id=screen_id)
    
    try:
        # 獲取新聞連結
        news_urls = bot.get_random_news_urls(base_url, NEWS_COUNT)
        
        if not news_urls:
            print("無法獲取部落格連結")
            return
        
        print(f"獲取到 {len(news_urls)} 個部落格連結")
        print(f"目標截圖數量: {SCREENSHOT_COUNT}")
        
        total_screenshots = 0
        
        # 記錄已處理的URL，避免重複
        processed_urls = set()
        
        # 處理每個網站
        for i, url in enumerate(news_urls, 1):
            # 檢查是否已經處理過這個URL
            if url in processed_urls:
                print(f"跳過已處理的URL: {url}")
                continue
                
            print(f"\n{'='*50}")
            print(f"處理第 {i}/{len(news_urls)} 個網站")
            print(f"網站URL: {url}")
            print(f"{'='*50}")
            
            try:
                # 處理網站並嘗試替換廣告
                screenshot_paths = bot.process_website(url)
                
                # 記錄已處理的URL
                processed_urls.add(url)
                
                if screenshot_paths:
                    print(f"✅ 成功處理網站！共產生 {len(screenshot_paths)} 張截圖")
                    total_screenshots += len(screenshot_paths)
                    
                    # 檢查是否達到目標截圖數量
                    if total_screenshots >= SCREENSHOT_COUNT:
                        print(f"✅ 已達到目標截圖數量: {SCREENSHOT_COUNT}")
                        break
                else:
                    print("❌ 網站處理完成，但沒有找到可替換的廣告")
                
            except Exception as e:
                print(f"❌ 處理網站失敗: {e}")
                continue
            
            # 在處理下一個網站前稍作休息並回到首頁
            if i < len(news_urls) and total_screenshots < SCREENSHOT_COUNT:
                print("等待 3 秒後處理下一個網站...")
                time.sleep(3)
                
                # 回到首頁，確保下次獲取文章時的一致性
                try:
                    print("回到首頁...")
                    bot.driver.get(base_url)
                    time.sleep(2)
                    bot.remove_fullscreen_ads()
                except Exception as e:
                    print(f"回到首頁失敗: {e}")
        
        print(f"\n{'='*50}")
        print(f"所有網站處理完成！總共產生 {total_screenshots} 張截圖")
        print(f"{'='*50}")
        
    finally:
        bot.close()

def test_screen_setup():
    """測試螢幕設定功能"""
    print("測試螢幕偵測功能...")
    
    # 偵測螢幕
    screens = ScreenManager.detect_screens()
    print(f"偵測到 {len(screens)} 個螢幕:")
    
    for screen in screens:
        primary_text = " (主螢幕)" if screen['primary'] else ""
        print(f"  螢幕 {screen['id']}: {screen['resolution']}{primary_text}")
    
    # 讓使用者選擇螢幕進行測試
    screen_id, selected_screen = ScreenManager.select_screen()
    
    if screen_id is None:
        return
    
    print(f"\n正在測試螢幕 {screen_id}...")
    
    # 創建測試用的瀏覽器實例
    test_bot = WebsiteAdReplacer(screen_id=screen_id)
    
    try:
        # 開啟測試頁面
        test_bot.driver.get("https://www.google.com")
        time.sleep(3)
        
        # 測試截圖功能
        print("測試截圖功能...")
        screenshot_path = test_bot.take_screenshot()
        
        if screenshot_path:
            print(f"✅ 螢幕 {screen_id} 設定成功！")
            print(f"測試截圖已保存: {screenshot_path}")
        else:
            print(f"❌ 螢幕 {screen_id} 截圖失敗")
        
        input("按 Enter 鍵關閉測試...")
        
    finally:
        test_bot.close()

if __name__ == "__main__":
    import sys
    
    # 檢查是否有命令列參數
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_screen_setup()
    else:
        main()