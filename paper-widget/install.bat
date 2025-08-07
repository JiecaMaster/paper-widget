@echo off
echo ====================================
echo   论文推送助手 - 安装依赖
echo ====================================
echo.

echo 正在安装Python依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo 错误: 安装依赖失败！
    echo 请确保已安装Python和pip。
    pause
    exit /b 1
)

echo.
echo ====================================
echo   依赖安装完成！
echo ====================================
echo.
echo 现在可以运行 run.bat 启动程序
echo.
pause