@echo off
echo ====================================
echo   论文推送助手 - 打包程序
echo ====================================
echo.

echo 正在使用PyInstaller打包...
pyinstaller --clean --onefile --windowed --name PaperWidget --add-data "config.json;." main.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 打包失败！
    echo 请确保已安装PyInstaller: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo ====================================
echo   打包完成！
echo ====================================
echo.
echo 可执行文件位于: dist\PaperWidget.exe
echo.
pause