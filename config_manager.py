#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
廣告替換系統設定管理器
互動式設定並執行廣告替換程式
"""

import json
import os
import subprocess
import sys
from datetime import datetime

CONFIG_FILE = 'ad_replacer_config.json'

def load_config():
    """載入現有設定"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # 預設設定
    return {
        'url': '',
        'screenshots': 30,
        'articles': 20,

        'screen': 1,
        'button_style': 'cross',
        'max_attempts': 50,
        'page_timeout': 15,
        'wait_time': 3,
        'max_failures': 3,
        'fullscreen': True,
        'debug_mode': True,
        'last_updated': ''
    }

def save_config(config):
    """儲存設定"""
    config['last_updated'] = datetime.now().isoformat()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_user_input(prompt, default=None, input_type=str, required=False):
    """取得使用者輸入"""
    if default is not None:
        prompt += f" (預設: {default})"
    prompt += " [ENTER跳過]" if not required else ""
    prompt += ": "
    
    while True:
        user_input = input(prompt).strip()
        
        if not user_input and default is not None:
            return default
        
        if not user_input and required:
            print("❌ 此欄位不能為空，請重新輸入")
            continue
        
        if not user_input and not required:
            print("⏭️ 已跳過此設定")
            return default
        
        if input_type == bool:
            if user_input.lower() in ['y', 'yes', '是', '1', 'true']:
                return True
            elif user_input.lower() in ['n', 'no', '否', '0', 'false']:
                return False
            else:
                print("❌ 請輸入 y/n 或 是/否")
                continue
        
        if input_type == int:
            try:
                return int(user_input)
            except ValueError:
                print("❌ 請輸入有效的數字")
                continue
        
        return user_input

def show_current_config(config):
    """顯示目前設定"""
    print("\n" + "="*60)
    print("📋 目前設定")
    print("="*60)
    print(f"🌐 目標網址: {config['url'] or '(未設定)'}")
    print(f"📸 截圖數量: {config['screenshots']}")
    print(f"📰 掃描文章數: {config['articles']}")
    print(f"🖥️ 螢幕編號: {config['screen']}")
    print(f"🖼️ 全螢幕模式: {'是' if config.get('fullscreen', True) else '否'}")
    print(f"🎨 按鈕樣式: {config.get('button_style', 'cross')}")
    print(f"🔄 最大嘗試: {config.get('max_attempts', 50)}")
    print(f"⏱️ 頁面超時: {config.get('page_timeout', 15)} 秒")
    print(f"⏳ 等待時間: {config.get('wait_time', 3)} 秒")
    print(f"❌ 失敗限制: {config.get('max_failures', 3)}")
    print(f"🔍 偵測調試: {'是' if config.get('debug_mode', False) else '否'}")
    if config['last_updated']:
        print(f"⏰ 最後更新: {config['last_updated'][:19].replace('T', ' ')}")
    print("="*60)

def interactive_config():
    """互動式設定"""
    print("\n🔧 廣告替換系統設定")
    print("="*50)
    
    config = load_config()
    show_current_config(config)
    
    print("\n💡 設定提示：")
    print("   • 直接按 ENTER 保持原設定")
    print("   • 輸入新值後按 ENTER 確認")
    print("   • 所有設定都可以跳過")
    print("\n請輸入新的設定值：")
    
    # 網址設定
    print("\n1️⃣ 目標網址設定")
    print("   範例格式:")
    print("   • https://example.com")
    print("   • https://www.example.com/news")
    print("   • https://news.example.com")
    config['url'] = get_user_input("🌐 目標網址", config['url'], required=True)
    
    # 截圖數量
    print("\n2️⃣ 截圖設定")
    print("   💡 按 ENTER 保持目前設定")
    config['screenshots'] = get_user_input("📸 截圖數量", config['screenshots'], int)
    
    # 文章數量
    print("\n3️⃣ 掃描設定")
    print("   💡 按 ENTER 保持目前設定")
    config['articles'] = get_user_input("📰 掃描文章數", config['articles'], int)
    
    # 螢幕選擇
    print("\n4️⃣ 螢幕設定")
    print("   💡 按 ENTER 保持目前設定")
    config['screen'] = get_user_input("🖥️ 螢幕編號", config['screen'], int)
    
    # 全螢幕模式
    print("\n5️⃣ 顯示模式設定")
    print("   💡 按 ENTER 保持目前設定")
    config['fullscreen'] = get_user_input("🖼️ 全螢幕模式 (y/n)", 'y' if config.get('fullscreen', True) else 'n', bool)
    
    # 進階設定
    print("\n6️⃣ 進階設定")
    print("   按鈕樣式選項:")
    print("   • cross - 驚嘆號+叉叉")
    print("   • dots - 驚嘆號+點點")
    print("   • adchoices - AdChoices+叉叉")
    print("   • adchoices_dots - AdChoices+點點")
    print("   • none - 無按鈕")
    print("   💡 按 ENTER 保持目前設定")
    
    button_styles = ['cross', 'dots', 'adchoices', 'adchoices_dots', 'none']
    while True:
        style = get_user_input("🎨 按鈕樣式", config.get('button_style', 'cross'))
        if style in button_styles:
            config['button_style'] = style
            break
        else:
            print(f"❌ 請輸入有效的樣式: {', '.join(button_styles)}")
    
    print("\n7️⃣ 效能設定")
    print("   💡 以下設定都可以按 ENTER 跳過")
    
    print("   最大嘗試次數: 尋找廣告元素的最大嘗試次數")
    config['max_attempts'] = get_user_input("🔄 最大嘗試次數", config.get('max_attempts', 50), int)
    
    print("   頁面載入超時: 等待網頁完全載入的最長時間")
    config['page_timeout'] = get_user_input("⏱️ 頁面載入超時(秒)", config.get('page_timeout', 15), int)
    
    print("   等待時間: 操作間的暫停時間 (截圖前、點擊後等)")
    config['wait_time'] = get_user_input("⏳ 等待時間(秒)", config.get('wait_time', 3), int)
    
    print("   連續失敗限制: 找不到對應尺寸廣告時的重試次數")
    config['max_failures'] = get_user_input("❌ 連續失敗限制", config.get('max_failures', 3), int)
    
    print("   偵測調試模式: 顯示詳細的廣告偵測過程資訊")
    config['debug_mode'] = get_user_input("🔍 偵測調試模式 (y/n)", 'y' if config.get('debug_mode', False) else 'n', bool)
    
    return config

def build_command(config):
    """根據設定建立執行命令"""
    cmd = ['python', 'ad_replacer_runner.py']
    
    # 必要參數
    cmd.extend(['--url', config['url']])
    
    # 可選參數
    if config['screenshots'] != 10:  # 預設值
        cmd.extend(['--screenshots', str(config['screenshots'])])
    
    if config['articles'] != 20:  # 預設值
        cmd.extend(['--articles', str(config['articles'])])
    

    
    if config['screen'] != 1:  # 預設值
        cmd.extend(['--screen', str(config['screen'])])
    
    return cmd

def main():
    """主程式"""
    print("🤖 廣告替換系統設定管理器")
    print("="*50)
    
    while True:
        print("\n請選擇操作:")
        print("1️⃣ 查看目前設定")
        print("2️⃣ 修改設定")
        print("3️⃣ 執行廣告替換")
        print("4️⃣ 修改設定並立即執行")
        print("5️⃣ 離開")
        
        choice = input("\n請輸入選項 (1-5): ").strip()
        
        if choice == '1':
            # 查看設定
            config = load_config()
            show_current_config(config)
            
        elif choice == '2':
            # 修改設定
            config = interactive_config()
            save_config(config)
            print("\n✅ 設定已儲存!")
            show_current_config(config)
            
        elif choice == '3':
            # 執行程式
            config = load_config()
            if not config['url']:
                print("\n❌ 尚未設定目標網址，請先進行設定")
                continue
            
            cmd = build_command(config)
            print(f"\n🚀 執行命令: {' '.join(cmd)}")
            print("="*50)
            
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"\n❌ 執行失敗: {e}")
            except KeyboardInterrupt:
                print("\n⏹️ 使用者中斷執行")
            
        elif choice == '4':
            # 修改設定並執行
            config = interactive_config()
            save_config(config)
            print("\n✅ 設定已儲存!")
            
            cmd = build_command(config)
            print(f"\n🚀 執行命令: {' '.join(cmd)}")
            print("="*50)
            
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"\n❌ 執行失敗: {e}")
            except KeyboardInterrupt:
                print("\n⏹️ 使用者中斷執行")
            
        elif choice == '5':
            print("\n👋 再見!")
            break
            
        else:
            print("\n❌ 無效選項，請重新選擇")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程式已結束")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")