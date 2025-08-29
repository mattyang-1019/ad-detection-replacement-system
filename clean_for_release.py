#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
發布前清理腳本
清除所有測試產生的檔案，恢復到原始狀態
"""

import os
import shutil
import json
from datetime import datetime

def clean_files():
    """清理所有測試產生的檔案"""
    print("🧹 開始清理測試檔案...")
    print("=" * 50)
    
    cleaned_items = []
    
    # 1. 清理設定檔 (保留 default_config.py 模板)
    config_files = [
        'ad_replacer_config.json',  # 使用者設定檔
        'config.py'                 # 自動生成的內部設定檔
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            os.remove(config_file)
            cleaned_items.append(f"🗑️ 刪除設定檔: {config_file}")
    
    # 2. 清理截圖資料夾
    screenshots_folder = 'screenshots'
    if os.path.exists(screenshots_folder):
        screenshot_files = os.listdir(screenshots_folder)
        if screenshot_files:
            for file in screenshot_files:
                file_path = os.path.join(screenshots_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            cleaned_items.append(f"🗑️ 清理截圖: {len(screenshot_files)} 個檔案")
    
    # 3. 清理上傳的圖片（保留 image_records.json）
    replace_image_folder = 'replace_image'
    if os.path.exists(replace_image_folder):
        image_files = []
        for file in os.listdir(replace_image_folder):
            if file != 'image_records.json' and not file.startswith('.'):
                file_path = os.path.join(replace_image_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    image_files.append(file)
        
        if image_files:
            cleaned_items.append(f"🗑️ 清理上傳圖片: {len(image_files)} 個檔案")
        
        # 重置 image_records.json
        records_file = os.path.join(replace_image_folder, 'image_records.json')
        if os.path.exists(records_file):
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            cleaned_items.append("🗑️ 重置圖片記錄檔")
    
    # 4. 清理日誌檔案
    logs_folder = 'logs'
    if os.path.exists(logs_folder):
        log_files = []
        for file in os.listdir(logs_folder):
            if file.endswith('.log'):
                file_path = os.path.join(logs_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    log_files.append(file)
        
        if log_files:
            cleaned_items.append(f"🗑️ 清理日誌檔案: {len(log_files)} 個檔案")
    
    # 5. 清理 Python 快取
    pycache_folders = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)
            pycache_folders.append(pycache_path)
    
    if pycache_folders:
        cleaned_items.append(f"🗑️ 清理 Python 快取: {len(pycache_folders)} 個資料夾")
    
    # 6. 清理臨時檔案
    temp_files = []
    for file in os.listdir('.'):
        if file.endswith(('.tmp', '.temp', '.bak')):
            os.remove(file)
            temp_files.append(file)
    
    if temp_files:
        cleaned_items.append(f"🗑️ 清理臨時檔案: {len(temp_files)} 個檔案")
    
    # 顯示清理結果
    print("\n".join(cleaned_items))
    
    if not cleaned_items:
        print("✅ 沒有需要清理的檔案，系統已經是乾淨狀態")
    else:
        print(f"\n✅ 清理完成！共處理 {len(cleaned_items)} 項")
    
    print("=" * 50)
    print("🎯 系統已恢復到原始狀態，可以安全發布")

def create_clean_gitignore():
    """創建完整的 .gitignore 檔案"""
    gitignore_content = """# 測試和個人設定檔案
ad_replacer_config.json
config.py

# 上傳的圖片檔案
replace_image/*.jpg
replace_image/*.jpeg
replace_image/*.png
replace_image/*.gif
replace_image/*.bmp
replace_image/*.webp

# 但保留記錄檔案結構
!replace_image/
!replace_image/.gitkeep
!replace_image/image_records.json

# 截圖結果
screenshots/
!screenshots/
!screenshots/.gitkeep

# 日誌檔案
logs/
*.log
!logs/
!logs/.gitkeep

# Python 相關
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虛擬環境
venv/
env/
ENV/
image_upload_env/

# IDE 設定
.vscode/
.idea/
*.swp
*.swo
*~

# 系統檔案
.DS_Store
Thumbs.db
desktop.ini

# 環境變數
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# 臨時檔案
*.tmp
*.temp
*.bak

# 資料庫檔案
*.db
*.sqlite
*.sqlite3
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ 已更新 .gitignore 檔案")

def create_gitkeep_files():
    """創建 .gitkeep 檔案以保持資料夾結構"""
    folders = ['replace_image', 'screenshots', 'logs']
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        gitkeep_path = os.path.join(folder, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('')
        print(f"✅ 創建 {gitkeep_path}")

def main():
    """主函數"""
    print("🧹 廣告替換系統 - 發布前清理工具")
    print("=" * 50)
    print("此工具將清理所有測試產生的檔案，恢復到原始狀態")
    print("包括：設定檔、截圖、上傳圖片、日誌等")
    print("=" * 50)
    
    confirm = input("確定要執行清理嗎？(y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', '是']:
        clean_files()
        create_clean_gitignore()
        create_gitkeep_files()
        
        print("\n🎉 清理完成！")
        print("💡 建議執行步驟：")
        print("   1. 檢查檔案是否正確清理")
        print("   2. 測試程式是否正常運作")
        print("   3. 提交到版本控制系統")
    else:
        print("❌ 取消清理操作")

if __name__ == '__main__':
    main()