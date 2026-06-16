@echo off
chcp 65001 >nul
title 番茄病虫害识别系统

echo ========================================
echo 🍅 番茄病虫害识别系统 - 启动中...
echo ========================================
echo.

cd /d "%~dp0"
python start.py

pause
