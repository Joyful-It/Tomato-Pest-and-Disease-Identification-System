"""
文件名: main.py
功能描述: FastAPI 应用主入口，启动服务和配置路由（增强版）
作者: ZT
日期: 2026/6/17
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import APP_HOST, APP_PORT, DEBUG
from api.routes import router as api_router
from rag.file_upload import router as rag_router
from database.init_db import init_database

# 创建 FastAPI 应用
app = FastAPI(
    title="番茄病虫害识别系统",
    description="基于多 Agent 协作的番茄病虫害智能诊断系统（支持 RAG 知识库）",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix="/api")

# 注册 RAG 文件上传路由
app.include_router(rag_router, prefix="/api/rag", tags=["RAG 知识库"])


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    初始化数据库和 RAG 系统
    """
    print("=" * 60)
    print("正在启动番茄病虫害识别系统...")
    print("=" * 60)

    # 初始化数据库
    init_database()

    # 预加载 RAG 系统
    print("\n正在初始化 RAG 知识库...")
    try:
        from rag.rag_system import init_rag_system
        rag = init_rag_system()
        if rag:
            print("RAG 知识库初始化成功！")
        else:
            print("RAG 知识库初始化失败，将使用纯 LLM 模式")
    except Exception as e:
        print(f"RAG 知识库初始化错误: {e}")

    print("\n" + "=" * 60)
    print("系统启动完成！")
    print(f"访问地址: http://{APP_HOST}:{APP_PORT}")
    print(f"API 文档: http://{APP_HOST}:{APP_PORT}/docs")
    print("=" * 60)


@app.get("/")
async def root():
    """
    根路径
    """
    return {
        "message": "番茄病虫害识别系统 API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "病虫害识别",
            "RAG 知识库检索",
            "混合检索（向量 + BM25）",
            "多格式文件上传（PDF/Word/TXT/MD）"
        ]
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "ok", "message": "服务运行正常"}


if __name__ == "__main__":
    """
    主程序入口
    启动 FastAPI 应用
    """
    print("=" * 50)
    print("番茄病虫害识别系统（增强版）")
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
