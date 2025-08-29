@echo off
chcp 65001 >nul
echo ====================================
echo 圖片上傳系統 - 自動設定和啟動
echo ====================================

REM 檢查是否存在虛擬環境
if not exist "image_upload_env" (
    echo 🔄 創建虛擬環境...
    python -m venv image_upload_env
    if errorlevel 1 (
        echo ❌ 創建虛擬環境失敗
        pause
        exit /b 1
    )
    echo ✅ 虛擬環境創建完成
)

REM 啟動虛擬環境
echo 🔄 啟動虛擬環境...
call image_upload_env\Scripts\activate.bat

REM 升級 pip
echo 🔄 升級 pip...
python -m pip install --upgrade pip

REM 安裝相依套件
echo 🔄 安裝相依套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 安裝套件失敗
    pause
    exit /b 1
)

echo ✅ 套件安裝完成

REM 啟動應用程式
echo 🚀 啟動圖片上傳系統...
echo.
echo 💡 提示：Flask 開發模式會自動重啟一次（這是正常現象）
echo 📱 伺服器將在 http://localhost:5001 啟動
echo 📁 圖片將儲存在 replace_image 資料夾
echo 🛑 按 Ctrl+C 停止伺服器
echo.
python image_manager_app.py

pause