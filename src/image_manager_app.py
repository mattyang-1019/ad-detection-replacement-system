#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖片上傳管理系統 - 獨立版本
專門用於管理廣告替換用的圖片
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
import json
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'image-manager-secret-key'

# 設定
REPLACE_IMAGE_FOLDER = 'data/replace_image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 建立必要的資料夾
os.makedirs(REPLACE_IMAGE_FOLDER, exist_ok=True)
os.makedirs('data/logs', exist_ok=True)

# 日誌設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/image_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """檢查是否為允許的圖片格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_info(image_path):
    """取得圖片資訊"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode
            
            # 計算檔案大小
            file_size = os.path.getsize(image_path)
            
            return {
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'file_size': file_size,
                'aspect_ratio': round(width / height, 2) if height != 0 else 0
            }
    except Exception as e:
        logger.error(f'無法讀取圖片資訊: {e}')
        return None

def generate_filename(original_filename, width, height):
    """根據圖片尺寸生成統一格式的檔名"""
    # 取得副檔名
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    
    # 生成廣告替換專用的檔名格式
    filename = f"img_{width}x{height}.{file_extension}"
    
    # 檢查是否存在，如果存在則加隨機數
    filepath = os.path.join(REPLACE_IMAGE_FOLDER, filename)
    if os.path.exists(filepath):
        import random
        random_suffix = random.randint(100, 999)
        filename = f"img_{width}x{height}_{random_suffix}.{file_extension}"
    
    return filename

def save_image_record(filename, original_name, image_info):
    """儲存圖片記錄到 JSON 檔案"""
    record_file = os.path.join(REPLACE_IMAGE_FOLDER, 'image_records.json')
    
    # 讀取現有記錄
    records = []
    if os.path.exists(record_file):
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except:
            records = []
    
    # 新增記錄
    new_record = {
        'filename': filename,
        'original_name': original_name,
        'upload_time': datetime.now().isoformat(),
        'image_info': image_info
    }
    records.append(new_record)
    
    # 儲存記錄
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def delete_image_record(filename):
    """刪除圖片記錄"""
    import threading
    import time
    
    record_file = os.path.join(REPLACE_IMAGE_FOLDER, 'image_records.json')
    logger.info(f'記錄檔案路徑: {record_file}')
    
    # 使用檔案鎖定機制避免並發問題
    lock_file = record_file + '.lock'
    max_retries = 5
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            # 嘗試創建鎖定檔案
            if not os.path.exists(lock_file):
                with open(lock_file, 'w') as lock:
                    lock.write(str(os.getpid()))
                
                try:
                    if os.path.exists(record_file):
                        with open(record_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if not content:
                                records = []
                            else:
                                records = json.loads(content)
                        
                        original_count = len(records)
                        logger.info(f'原始記錄數量: {original_count}')
                        
                        # 移除指定檔案的記錄
                        records = [record for record in records if record['filename'] != filename]
                        
                        new_count = len(records)
                        logger.info(f'刪除後記錄數量: {new_count}')
                        
                        # 儲存更新後的記錄
                        with open(record_file, 'w', encoding='utf-8') as f:
                            json.dump(records, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f'記錄檔案已更新')
                        return True
                    else:
                        return True
                finally:
                    # 移除鎖定檔案
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
            else:
                # 檔案被鎖定，等待後重試
                time.sleep(retry_delay)
                retry_delay *= 2  # 指數退避
                continue
                
        except Exception as e:
            logger.error(f'刪除記錄失敗 (嘗試 {attempt + 1}): {e}')
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                except:
                    pass
            if attempt == max_retries - 1:
                return False
            time.sleep(retry_delay)
    
    return False

@app.route('/')
def index():
    """首頁 - 圖片管理系統"""
    return render_template('single_page_app.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """處理圖片上傳（支援多檔案）"""
    # 檢查是否有檔案
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '沒有選擇圖片檔案'})
    
    files = request.files.getlist('image')
    if not files or (len(files) == 1 and files[0].filename == ''):
        return jsonify({'success': False, 'message': '沒有選擇圖片檔案'})
    
    results = []
    success_count = 0
    error_count = 0
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            try:
                # 先用臨時檔名儲存，以便讀取圖片尺寸
                temp_filename = secure_filename(file.filename)
                temp_filepath = os.path.join(REPLACE_IMAGE_FOLDER, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{temp_filename}")
                file.save(temp_filepath)
                
                # 取得圖片資訊
                image_info = get_image_info(temp_filepath)
                
                if image_info:
                    # 根據圖片尺寸生成新檔名（廣告替換專用格式）
                    new_filename = generate_filename(file.filename, image_info['width'], image_info['height'])
                    new_filepath = os.path.join(REPLACE_IMAGE_FOLDER, new_filename)
                    
                    # 將臨時檔案重新命名為正式檔名
                    os.rename(temp_filepath, new_filepath)
                    
                    # 儲存記錄
                    save_image_record(new_filename, file.filename, image_info)
                    
                    logger.info(f'圖片上傳成功: {file.filename} -> {new_filename}, 尺寸: {image_info["width"]}x{image_info["height"]}')
                    
                    results.append({
                        'success': True,
                        'filename': new_filename,
                        'original_name': file.filename,
                        'image_info': image_info
                    })
                    success_count += 1
                else:
                    # 刪除無效的圖片檔案
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                    results.append({
                        'success': False,
                        'filename': file.filename,
                        'message': '無法讀取圖片資訊'
                    })
                    error_count += 1
                    
            except Exception as e:
                logger.error(f'處理檔案 {file.filename} 時發生錯誤: {e}')
                results.append({
                    'success': False,
                    'filename': file.filename,
                    'message': f'處理失敗: {str(e)}'
                })
                error_count += 1
        else:
            results.append({
                'success': False,
                'filename': file.filename,
                'message': '不支援的檔案格式'
            })
            error_count += 1
    
    # 返回批量上傳結果
    return jsonify({
        'success': success_count > 0,
        'message': f'成功上傳 {success_count} 張圖片' + (f'，{error_count} 張失敗' if error_count > 0 else ''),
        'total_files': len(files),
        'success_count': success_count,
        'error_count': error_count,
        'results': results
    })

@app.route('/sync_files', methods=['POST'])
def sync_files():
    """同步檔案系統和 JSON 記錄"""
    try:
        # 獲取實際檔案列表
        actual_files = set()
        for file in os.listdir(REPLACE_IMAGE_FOLDER):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                actual_files.add(file)
        
        # 獲取 JSON 記錄中的檔案
        record_file = os.path.join(REPLACE_IMAGE_FOLDER, 'image_records.json')
        if os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            recorded_files = {record['filename'] for record in records}
        else:
            records = []
            recorded_files = set()
        
        # 找出需要刪除的檔案（在記錄中但實際不存在）
        files_to_remove_from_records = recorded_files - actual_files
        
        # 找出需要添加到記錄的檔案（實際存在但不在記錄中）
        files_to_add_to_records = actual_files - recorded_files
        
        # 更新記錄
        updated_records = [record for record in records if record['filename'] not in files_to_remove_from_records]
        
        # 為新檔案創建記錄
        for filename in files_to_add_to_records:
            filepath = os.path.join(REPLACE_IMAGE_FOLDER, filename)
            try:
                with Image.open(filepath) as img:
                    file_size = os.path.getsize(filepath)
                    record = {
                        "filename": filename,
                        "original_name": filename,
                        "upload_time": datetime.now().isoformat(),
                        "image_info": {
                            "width": img.width,
                            "height": img.height,
                            "format": img.format,
                            "mode": img.mode,
                            "file_size": file_size,
                            "aspect_ratio": round(img.width / img.height, 2)
                        }
                    }
                    updated_records.append(record)
            except Exception as e:
                logger.error(f'無法處理檔案 {filename}: {e}')
        
        # 儲存更新後的記錄
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(updated_records, f, ensure_ascii=False, indent=2)
        
        logger.info(f'檔案同步完成: 移除 {len(files_to_remove_from_records)} 個記錄, 新增 {len(files_to_add_to_records)} 個記錄')
        
        return jsonify({
            'success': True, 
            'message': f'同步完成！移除 {len(files_to_remove_from_records)} 個無效記錄，新增 {len(files_to_add_to_records)} 個檔案記錄',
            'removed': list(files_to_remove_from_records),
            'added': list(files_to_add_to_records)
        })
        
    except Exception as e:
        logger.error(f'檔案同步失敗: {e}')
        return jsonify({'success': False, 'message': f'同步失敗: {str(e)}'})

@app.route('/api/images')
def api_images():
    """API: 取得所有圖片資料"""
    record_file = os.path.join(REPLACE_IMAGE_FOLDER, 'image_records.json')
    
    records = []
    if os.path.exists(record_file):
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except:
            records = []
    
    # 按上傳時間排序（最新的在前）
    records.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return jsonify({'images': records})

@app.route('/api/stats')
def get_stats():
    """API: 取得統計資訊"""
    record_file = os.path.join(REPLACE_IMAGE_FOLDER, 'image_records.json')
    
    total_images = 0
    total_size = 0
    size_distribution = {}
    
    if os.path.exists(record_file):
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
                total_images = len(records)
                
                for record in records:
                    info = record.get('image_info', {})
                    total_size += info.get('file_size', 0)
                    
                    # 統計尺寸分布
                    size_key = f"{info.get('width', 0)}x{info.get('height', 0)}"
                    size_distribution[size_key] = size_distribution.get(size_key, 0) + 1
        except:
            pass
    
    return jsonify({
        'total_images': total_images,
        'total_size': total_size,
        'size_distribution': size_distribution
    })

@app.route('/replace_image/<filename>')
def uploaded_file(filename):
    """提供上傳的圖片檔案"""
    return send_from_directory(REPLACE_IMAGE_FOLDER, filename)

@app.route('/delete_image', methods=['POST'])
def delete_image():
    """刪除圖片"""
    logger.info(f'收到刪除圖片請求')
    data = request.get_json()
    filename = data.get('filename')
    logger.info(f'要刪除的檔案名稱: {filename}')
    
    if not filename:
        logger.warning('未提供檔案名稱')
        return jsonify({'success': False, 'message': '未提供檔案名稱'})
    
    try:
        # 刪除實際檔案
        filepath = os.path.join(REPLACE_IMAGE_FOLDER, filename)
        logger.info(f'檔案路徑: {filepath}')
        
        if os.path.exists(filepath):
            logger.info(f'檔案存在，準備刪除: {filepath}')
            os.remove(filepath)
            logger.info(f'檔案已刪除: {filepath}')
        else:
            logger.warning(f'檔案不存在: {filepath}')
        
        # 刪除記錄
        logger.info(f'準備刪除記錄: {filename}')
        delete_result = delete_image_record(filename)
        logger.info(f'記錄刪除結果: {delete_result}')
        
        logger.info(f'圖片刪除成功: {filename}')
        return jsonify({'success': True, 'message': '圖片刪除成功'})
        
    except Exception as e:
        logger.error(f'刪除圖片失敗: {filename}, 錯誤: {e}')
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'})

# 模板過濾器
@app.template_filter('format_file_size')
def format_file_size(size):
    """格式化檔案大小"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

@app.template_filter('format_datetime')
def format_datetime(datetime_str):
    """格式化日期時間"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime_str

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='圖片上傳管理系統')
    parser.add_argument('--port', type=int, default=5001, help='指定埠號 (預設: 5001)')
    parser.add_argument('--host', default='0.0.0.0', help='指定主機 (預設: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='啟用調試模式')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🖼️ 圖片上傳管理系統")
    print("=" * 60)
    print(f"🌐 Web 介面網址：")
    print(f"   • http://localhost:{args.port}")
    print(f"   • http://127.0.0.1:{args.port}")
    print(f"📁 圖片儲存位置: {os.path.abspath(REPLACE_IMAGE_FOLDER)}")
    print(f"📋 日誌儲存位置: {os.path.abspath('data/logs')}")
    print(f"🛑 按 Ctrl+C 停止伺服器")
    print("=" * 60)
    print("📋 功能說明：")
    print("   • 上傳廣告替換用的圖片")
    print("   • 自動重新命名為 img_寬度x高度.副檔名 格式")
    print("   • 支援 PNG, JPG, JPEG, GIF, BMP, WebP 格式")
    print("   • 最大檔案大小: 10MB")
    print("=" * 60)
    
    logger.info('啟動圖片上傳管理系統')
    
    try:
        app.run(debug=args.debug, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n✅ 圖片管理系統已安全停止")
        logger.info('圖片管理系統已停止')