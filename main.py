"""
文件名: main.py
功能描述: FastAPI 应用主入口，启动服务和配置路由
作者: ZT
日期: 2026/6/16
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config import APP_HOST, APP_PORT, DEBUG
from api.routes import router
from database.init_db import init_database

# 创建 FastAPI 应用
app = FastAPI(
    title="番茄病虫害识别系统",
    description="基于多 Agent 协作的番茄病虫害智能诊断系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(router, prefix="/api")

# 静态文件服务（用于生产环境）
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    初始化数据库等
    """
    print("正在启动番茄病虫害识别系统...")
    init_database()
    print("系统启动完成！")
    print(f"访问地址: http://{APP_HOST}:{APP_PORT}")
    print(f"API 文档: http://{APP_HOST}:{APP_PORT}/docs")


@app.get("/")
async def root():
    """
    根路径
    返回前端页面（开发模式下重定向到 Vue 开发服务器）
    """
    return {
        "message": "番茄病虫害识别系统 API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "ok", "message": "服务运行正常"}


# 捕获所有非 API 路由，返回前端页面（用于生产环境）
# @app.get("/{full_path:path}")
# async def serve_frontend(full_path: str):
#     """
#     服务前端页面
#     """
#     # 检查静态文件是否存在
#     static_file = Path("static") / full_path
#     if static_file.exists():
#         return FileResponse(static_file)
#     # 否则返回 index.html（支持前端路由）
#     return FileResponse("static/index.html")


if __name__ == "__main__":
    """
    主程序入口
    启动 FastAPI 应用
    """
    print("=" * 50)
    print("番茄病虫害识别系统")
    print("=" * 50)
    print(f"服务地址: http://{APP_HOST}:{APP_PORT}")
    print(f"API 文档: http://{APP_HOST}:{APP_PORT}/docs")
    print(f"调试模式: {'开启' if DEBUG else '关闭'}")
    print("=" * 50)

    # 启动服务
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level="info"
    )
