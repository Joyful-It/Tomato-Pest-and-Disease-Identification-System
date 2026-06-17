"""
文件名: file_upload.py
功能描述: 文件上传 API，支持 PDF/Word/TXT/Markdown 文件上传并自动解析入库
作者: ZT
日期: 2026/6/17
"""

import os
import shutil
from typing import List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

# 创建路由器
router = APIRouter()

# 支持的文件格式
SUPPORTED_FORMATS = {".txt", ".md", ".pdf", ".docx"}

# 上传目录
UPLOAD_DIR = Path(__file__).parent.parent / "rag知识库"


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool
    message: str
    filename: str = None
    chunks: int = 0


class KnowledgeBaseResponse(BaseModel):
    """知识库状态响应模型"""
    success: bool
    total_documents: int
    document_list: List[str]
    rag_status: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件到知识库

    Args:
        file: 上传的文件

    Returns:
        上传结果
    """
    # 检查文件格式
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}，支持的格式: {', '.join(SUPPORTED_FORMATS)}"
        )

    try:
        # 确保上传目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 保存文件
        dest_path = UPLOAD_DIR / file.filename
        with open(dest_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 添加到 RAG 知识库
        from rag.rag_system import init_rag_system
        rag = init_rag_system()

        if rag:
            # 重新加载文档并构建索引
            rag.load_documents()
            rag.build_index()

            # 计算片段数
            chunks_count = len([d for d in rag.documents if d.source == file.filename])

            return UploadResponse(
                success=True,
                message=f"文件上传成功，已添加到知识库",
                filename=file.filename,
                chunks=chunks_count
            )
        else:
            return UploadResponse(
                success=True,
                message="文件上传成功，但 RAG 系统未就绪",
                filename=file.filename
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/knowledge-base", response_model=KnowledgeBaseResponse)
async def get_knowledge_base_status():
    """
    获取知识库状态

    Returns:
        知识库状态信息
    """
    try:
        # 获取文档列表
        document_list = []
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.suffix.lower() in SUPPORTED_FORMATS:
                    document_list.append(file_path.name)

        # 获取 RAG 状态
        from rag.rag_system import init_rag_system
        rag = init_rag_system()

        rag_status = "not_loaded"
        total_documents = 0

        if rag:
            rag_status = "loaded"
            total_documents = len(rag.documents)

        return KnowledgeBaseResponse(
            success=True,
            total_documents=total_documents,
            document_list=document_list,
            rag_status=rag_status
        )

    except Exception as e:
        return KnowledgeBaseResponse(
            success=False,
            total_documents=0,
            document_list=[],
            rag_status="error"
        )


@router.delete("/knowledge-base/{filename}")
async def delete_document(filename: str):
    """
    从知识库删除文档

    Args:
        filename: 文件名

    Returns:
        删除结果
    """
    try:
        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 删除文件
        os.remove(file_path)

        # 重建索引
        from rag.rag_system import init_rag_system
        rag = init_rag_system()

        if rag:
            rag.load_documents()
            rag.build_index()

        return {"success": True, "message": f"文件 {filename} 已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/knowledge-base/rebuild")
async def rebuild_knowledge_base():
    """
    重建知识库索引

    Returns:
        重建结果
    """
    try:
        from rag.rag_system import init_rag_system
        rag = init_rag_system()

        if rag:
            rag.load_documents()
            success = rag.build_index()

            if success:
                return {
                    "success": True,
                    "message": "知识库索引重建成功",
                    "total_documents": len(rag.documents)
                }
            else:
                return {"success": False, "message": "索引构建失败"}
        else:
            return {"success": False, "message": "RAG 系统未就绪"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")
