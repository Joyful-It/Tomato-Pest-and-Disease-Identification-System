"""
文件名: config.py
功能描述: 应用配置文件，包含所有配置项
作者: ZT
日期: 2026/6/16
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_URL = f"sqlite:///{BASE_DIR}/tomato_disease.db"

# 上传文件配置
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# LLM 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "你的DeepSeek-Key")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
LLM_TEMPERATURE = 0.3

# 彩云天气 API 配置（预留）
CAIYUN_API_KEY = os.getenv("CAIYUN_API_KEY", "")

# 定位服务配置
IP_LOCATION_API = "http://ip-api.com/json"  # IP 定位 API

# 应用配置
APP_HOST = "0.0.0.0"
APP_PORT = 8000
DEBUG = True

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
