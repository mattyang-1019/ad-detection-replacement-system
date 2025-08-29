#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
廣告替換執行器 - 獨立版本
直接執行廣告偵測和替換功能
"""

import os
import sys
import argparse
import json
from datetime import datetime

def create_config_file(config_data):
    """創建配置檔案"""
    # 從設定檔或預設值取得參數
    target_url = config_data.get('url', '')
    screenshot_count = config_data.get('screenshots', 30)
    news_count = config_data.get('articles', 20)
    button_style = config_data.get('button_style', 'cross')
    max_attempts = config_data.get('max_attempts', 50)
    page_timeout = config_data.get('page_timeout', 15)
    wait_time = config_data.get('wait_time', 3)
    max_failures = config_data.get('max_failures', 3)
    fullscreen = config_data.get('fullscreen', True)
    debug_mode = config_data.get('debug_mode', True)
    
    config_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
廣告替換系統配置 - 由執行器自動生成
生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

# 基本設定
SCREENSHOT_COUNT = {screenshot_count}
MAX_ATTEMPTS = {max_attempts}
PAGE_LOAD_TIMEOUT = {page_timeout}
WAIT_TIME = {wait_time}
REPLACE_IMAGE_FOLDER = "data/replace_image"
DEFAULT_IMAGE = "mini.jpg"
MINI_IMAGE = "mini.jpg"
BASE_URL = "{target_url}"

# 進階設定
NEWS_COUNT = {news_count}
TARGET_AD_SIZES = [
    {{"width": 970, "height": 90}}, 
    {{"width": 986, "height": 106}},
    {{"width": 728, "height": 90}},
    {{"width": 300, "height": 250}},
    {{"width": 336, "height": 280}},
    {{"width": 320, "height": 50}},
    {{"width": 160, "height": 600}},
    {{"width": 300, "height": 600}},
    {{"width": 120, "height": 600}},
    {{"width": 240, "height": 400}},
    {{"width": 250, "height": 250}},
    {{"width": 300, "height": 50}},
    {{"width": 320, "height": 100}},
    {{"width": 980, "height": 120}}
]

IMAGE_USAGE_COUNT = {{
    "data/replace_image/img_120x600.jpg": 5,
    "data/replace_image/img_160x600.jpg": 5,
    "data/replace_image/img_240x400.jpg": 5,
    "data/replace_image/img_250x250.jpg": 5,
    "data/replace_image/img_300x50.jpg": 5,
    "data/replace_image/img_300x250.jpg": 5,
    "data/replace_image/img_300x600.jpg": 5,
    "data/replace_image/img_320x50.jpg": 5,
    "data/replace_image/img_320x100.jpg": 5,
    "data/replace_image/img_336x280.jpg": 5,
    "data/replace_image/img_728x90.jpg": 5,
    "data/replace_image/img_970x90.jpg": 5,
    "data/replace_image/img_980x120.jpg": 5
}}

MAX_CONSECUTIVE_FAILURES = {max_failures}
CLOSE_BUTTON_SIZE = {{"width": 15, "height": 15}}
INFO_BUTTON_SIZE = {{"width": 15, "height": 15}}
INFO_BUTTON_COLOR = "#00aecd"
INFO_BUTTON_OFFSET = 16
FULLSCREEN_MODE = {fullscreen}
DEBUG_MODE = {debug_mode}
SCREENSHOT_FOLDER = "data/screenshots"
BUTTON_STYLE = "{button_style}"
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ 配置檔案已創建")
    print(f"   目標網址: {target_url}")
    print(f"   截圖數量: {screenshot_count}")
    print(f"   掃描文章: {news_count}")
    print(f"   按鈕樣式: {button_style}")
    print(f"   全螢幕模式: {fullscreen}")

def check_requirements():
    """檢查系統需求"""
    print("🔍 檢查系統需求...")
    
    # 檢查必要資料夾
    required_folders = ['data/replace_image', 'data/screenshots']
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"✅ 創建資料夾: {folder}")
        else:
            print(f"✅ 資料夾存在: {folder}")
    
    # 檢查替換圖片
    replace_image_folder = 'data/replace_image'
    image_files = []
    if os.path.exists(replace_image_folder):
        for filename in os.listdir(replace_image_folder):
            if filename.startswith('img_') and filename.endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(filename)
    
    if image_files:
        print(f"✅ 找到 {len(image_files)} 張替換圖片:")
        for img in image_files:
            print(f"   • {img}")
    else:
        print("⚠️ 警告：沒有找到替換圖片！")
        print("   請先執行圖片管理系統上傳圖片")
        print("   執行命令: python image_manager_app.py")
        return False
    
    # 檢查 website_template_complete.py
    if not os.path.exists('src/website_template_complete.py'):
        print("❌ 錯誤：找不到 src/website_template_complete.py")
        return False
    else:
        print("✅ 廣告替換核心模組存在")
    
    return True

def check_config_file():
    """檢查是否存在設定檔"""
    config_file = 'ad_replacer_config.json'
    
    if not os.path.exists(config_file):
        print("=" * 70)
        print("⚠️ 尚未進行系統設定")
        print("=" * 70)
        print("📋 請先使用設定管理器進行設定：")
        print("")
        print("   python config_manager.py")
        print("")
        print("💡 設定管理器功能：")
        print("   • 🔧 互動式設定所有參數")
        print("   • 💾 自動儲存設定檔")
        print("   • 🚀 一鍵執行廣告替換")
        print("")
        print("🎯 或者你也可以直接提供參數執行：")
        print("   python ad_replacer_runner.py --url https://example.com")
        print("=" * 70)
        return False
    
    return True

def load_config_if_exists():
    """如果存在設定檔則載入"""
    config_file = 'ad_replacer_config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("✅ 找到設定檔，載入預設值：")
            print(f"   🌐 目標網址: {config.get('url', '未設定')}")
            print(f"   📸 截圖數量: {config.get('screenshots', 10)}")
            print(f"   📰 掃描文章: {config.get('articles', 20)}")
            print(f"   🖥️ 螢幕編號: {config.get('screen', 1)}")
            print("")
            
            return config
        except:
            print("⚠️ 設定檔格式錯誤，將使用命令列參數")
    
    return None

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='廣告替換執行器')
    parser.add_argument('--url', help='目標網站網址')
    parser.add_argument('--screenshots', type=int, help='目標截圖數量 (預設: 10)')
    parser.add_argument('--articles', type=int, help='掃描文章數量 (預設: 20)')

    parser.add_argument('--screen', type=int, help='使用的螢幕編號 (預設: 1)')
    
    args = parser.parse_args()
    
    # 載入設定檔（如果存在）
    config = load_config_if_exists()
    
    # 如果沒有提供 --url 參數且沒有設定檔，則提示使用設定管理器
    if not args.url and not config:
        if not check_config_file():
            return 1
    
    # 合併設定檔和命令列參數（命令列參數優先）
    if config:
        url = args.url or config.get('url')
        screenshots = args.screenshots if args.screenshots is not None else config.get('screenshots', 10)
        articles = args.articles if args.articles is not None else config.get('articles', 20)
        screen = args.screen if args.screen is not None else config.get('screen', 1)
        # 處理 fullscreen 設定（支援布林值和字串）
        config_fullscreen = config.get('fullscreen', True)
        if isinstance(config_fullscreen, str):
            config_fullscreen = config_fullscreen in ['是', 'true', 'True', 'yes', 'Yes']
        fullscreen = config_fullscreen
    else:
        url = args.url
        screenshots = args.screenshots or 10
        articles = args.articles or 20
        screen = args.screen or 1
        fullscreen = True  # 預設值
    
    # 檢查必要參數
    if not url:
        print("❌ 錯誤：未提供目標網址")
        print("請使用 --url 參數或先執行設定管理器")
        return 1
    
    print("=" * 70)
    print("🤖 廣告替換執行器")
    print("=" * 70)
    print(f"🎯 目標網址: {url}")
    print(f"📸 目標截圖: {screenshots} 張")
    print(f"📄 掃描文章: {articles} 篇")
    print(f"🖥️ 使用螢幕: {screen}")
    print("=" * 70)
    
    # 檢查系統需求
    if not check_requirements():
        print("\n❌ 系統需求檢查失敗，請先解決上述問題")
        return 1
    
    print("\n🔧 準備執行環境...")
    
    # 創建配置檔案
    config_data = {
        'url': url,
        'screenshots': screenshots,
        'articles': articles,

        'button_style': config.get('button_style', 'cross') if config else 'cross',
        'max_attempts': config.get('max_attempts', 50) if config else 50,
        'page_timeout': config.get('page_timeout', 15) if config else 15,
        'wait_time': config.get('wait_time', 3) if config else 3,
        'max_failures': config.get('max_failures', 3) if config else 3,
        'fullscreen': fullscreen
    }
    create_config_file(config_data)
    
    print("\n🚀 開始執行廣告替換...")
    print("=" * 70)
    
    try:
        # 導入並執行廣告替換系統
        import sys
        sys.path.append('src')
        from website_template_complete import main as run_ad_replacement
        
        # 執行廣告替換
        run_ad_replacement()
        
        print("\n" + "=" * 70)
        print("✅ 廣告替換執行完成！")
        
        # 顯示結果
        screenshots_folder = 'data/screenshots'
        if os.path.exists(screenshots_folder):
            screenshot_files = [f for f in os.listdir(screenshots_folder) 
                              if f.endswith(('.png', '.jpg', '.jpeg'))]
            if screenshot_files:
                print(f"📸 產生了 {len(screenshot_files)} 張截圖:")
                for screenshot in sorted(screenshot_files)[-5:]:  # 顯示最新的5張
                    print(f"   • {screenshot}")
                if len(screenshot_files) > 5:
                    print(f"   ... 還有 {len(screenshot_files) - 5} 張截圖")
                print(f"📁 截圖位置: {os.path.abspath(screenshots_folder)}")
            else:
                print("⚠️ 沒有產生截圖")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n⚠️ 使用者中斷執行")
        return 1
    except Exception as e:
        print(f"\n❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())