"""
文件名: rag_system.py
功能描述: RAG 知识库系统 - 增强版，支持智能分块、混合检索、多格式文件解析
作者: ZT
日期: 2026/6/17
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import re


class DocumentChunk:
    """
    文档片段类
    存储单个文档片段的内容和元数据
    """

    def __init__(self, content: str, source: str, chunk_id: int, metadata: Dict = None):
        self.content = content
        self.source = source
        self.chunk_id = chunk_id
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "source": self.source,
            "chunk_id": self.chunk_id,
            "metadata": self.metadata
        }


class RAGSystem:
    """
    RAG 知识库系统 - 增强版
    功能：
    1. 智能分块（RecursiveCharacterTextSplitter）
    2. 混合检索（向量检索 + BM25 关键词检索 + RRF 融合）
    3. 多格式文件支持（PDF/Word/TXT/Markdown）
    4. 文件上传接口
    """

    def __init__(self, model_path: str, knowledge_dir: str, db_dir: str = "vector_db"):
        """
        初始化 RAG 系统

        Args:
            model_path: 向量模型路径
            knowledge_dir: 知识文档目录
            db_dir: 向量数据库存储目录
        """
        self.model_path = model_path
        self.knowledge_dir = knowledge_dir
        self.db_dir = db_dir

        # 模型和向量存储
        self.model = None
        self.tokenizer = None
        self.device = None
        self.documents: List[DocumentChunk] = []
        self.embeddings = None
        self.index = None

        # BM25 索引
        self.bm25_index = None
        self.tokenized_corpus = []

        # 确保目录存在
        os.makedirs(db_dir, exist_ok=True)
        os.makedirs(knowledge_dir, exist_ok=True)

    def load_model(self):
        """
        加载向量模型（使用 transformers 库，支持 GPU）
        """
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel

            print(f"正在加载向量模型: {self.model_path}")

            # 检测 GPU 可用性
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"使用设备: {self.device}")

            # 加载 tokenizer 和 model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModel.from_pretrained(self.model_path).to(self.device)
            self.model.eval()

            print("向量模型加载成功！")
            return True
        except Exception as e:
            print(f"加载向量模型失败: {e}")
            return False

    def _encode(self, texts: List[str], batch_size: int = 32) -> 'np.ndarray':
        """
        将文本转换为向量

        Args:
            texts: 文本列表
            batch_size: 批处理大小

        Returns:
            向量数组
        """
        import torch
        import numpy as np

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenize
            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)

            # 生成向量
            with torch.no_grad():
                outputs = self.model(**encoded)
                # 使用 [CLS] token 的输出作为句子向量
                embeddings = outputs.last_hidden_state[:, 0, :]
                # 归一化
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            all_embeddings.append(embeddings.cpu().numpy())

        return np.concatenate(all_embeddings, axis=0)

    def _split_document_smart(self, content: str, source: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[DocumentChunk]:
        """
        智能分块（使用递归字符分割器）

        Args:
            content: 文档内容
            source: 文档来源
            chunk_size: 片段大小（字符数）
            chunk_overlap: 重叠字符数

        Returns:
            文档片段列表
        """
        # 分隔符优先级：段落 > 换行 > 句号 > 逗号 > 空格
        separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", "，", ",", " ", ""]

        chunks = []
        current_chunks = self._recursive_split(content, separators, chunk_size, chunk_overlap)

        for i, chunk_text in enumerate(current_chunks):
            if chunk_text.strip():
                chunks.append(DocumentChunk(
                    content=chunk_text.strip(),
                    source=source,
                    chunk_id=i,
                    metadata={"method": "recursive_split"}
                ))

        return chunks

    def _recursive_split(self, text: str, separators: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        递归字符分割

        Args:
            text: 文本
            separators: 分隔符列表
            chunk_size: 片段大小
            chunk_overlap: 重叠大小

        Returns:
            分割后的文本列表
        """
        final_chunks = []

        # 如果文本小于 chunk_size，直接返回
        if len(text) <= chunk_size:
            if text.strip():
                return [text]
            return []

        # 找到合适的分隔符
        separator = separators[-1]  # 默认使用空格
        for sep in separators:
            if sep in text:
                separator = sep
                break

        # 按分隔符分割
        splits = text.split(separator)

        # 合并小片段
        current_chunk = ""
        for split in splits:
            split = split.strip()
            if not split:
                continue

            # 如果当前片段加上新片段超过大小限制
            if len(current_chunk) + len(split) + len(separator) > chunk_size:
                if current_chunk:
                    final_chunks.append(current_chunk)
                    # 保留重叠部分
                    if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                        current_chunk = current_chunk[-chunk_overlap:] + separator + split
                    else:
                        current_chunk = split
                else:
                    # 单个片段太大，递归分割
                    if len(split) > chunk_size:
                        sub_chunks = self._recursive_split(split, separators[1:], chunk_size, chunk_overlap)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(split)
            else:
                current_chunk = current_chunk + separator + split if current_chunk else split

        # 添加最后一个片段
        if current_chunk.strip():
            final_chunks.append(current_chunk)

        return final_chunks

    def load_documents(self):
        """
        加载知识文档（支持多格式）

        Returns:
            文档列表
        """
        documents = []
        knowledge_path = Path(self.knowledge_dir)

        if not knowledge_path.exists():
            print(f"知识文档目录不存在: {self.knowledge_dir}")
            return documents

        # 支持的文件格式
        supported_formats = {".txt", ".md", ".pdf", ".docx"}

        # 遍历所有支持的文件
        for file_path in knowledge_path.iterdir():
            if file_path.suffix.lower() in supported_formats:
                try:
                    content = self._read_file(file_path)
                    if content:
                        # 智能分块
                        chunks = self._split_document_smart(content, file_path.name)
                        documents.extend(chunks)
                        print(f"已加载文档: {file_path.name} ({len(chunks)} 个片段)")
                except Exception as e:
                    print(f"加载文档失败 {file_path.name}: {e}")

        self.documents = documents
        print(f"共加载 {len(documents)} 个文档片段")
        return documents

    def _read_file(self, file_path: Path) -> str:
        """
        读取文件内容（支持多格式）

        Args:
            file_path: 文件路径

        Returns:
            文件内容
        """
        suffix = file_path.suffix.lower()

        if suffix in [".txt", ".md"]:
            return self._read_text_file(file_path)
        elif suffix == ".pdf":
            return self._read_pdf_file(file_path)
        elif suffix == ".docx":
            return self._read_docx_file(file_path)
        else:
            print(f"不支持的文件格式: {suffix}")
            return ""

    def _read_text_file(self, file_path: Path) -> str:
        """读取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_pdf_file(self, file_path: Path) -> str:
        """读取 PDF 文件"""
        try:
            import pdfplumber

            content = ""
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n\n"
            return content
        except Exception as e:
            print(f"PDF 读取失败: {e}")
            return ""

    def _read_docx_file(self, file_path: Path) -> str:
        """读取 Word 文件"""
        try:
            from docx import Document

            doc = Document(str(file_path))
            content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append(para.text)
            return "\n\n".join(content)
        except Exception as e:
            print(f"Word 文件读取失败: {e}")
            return ""

    def build_index(self):
        """
        构建向量索引和 BM25 索引
        """
        if not self.model:
            print("请先加载模型")
            return False

        if not self.documents:
            print("请先加载文档")
            return False

        try:
            import faiss
            import numpy as np

            print("正在生成文档向量...")

            # 提取文档内容
            texts = [doc.content for doc in self.documents]

            # 生成向量（使用 GPU）
            self.embeddings = self._encode(texts)
            print(f"向量生成完成，形状: {self.embeddings.shape}")

            # 构建 FAISS 索引
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))

            print(f"向量索引构建完成！向量维度: {dimension}, 文档数量: {self.index.ntotal}")

            # 构建 BM25 索引
            self._build_bm25_index()

            # 保存索引和文档
            self._save_index()

            return True
        except Exception as e:
            print(f"构建向量索引失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _build_bm25_index(self):
        """
        构建 BM25 索引（用于关键词检索）
        """
        try:
            from rank_bm25 import BM25Okapi
            import jieba

            print("正在构建 BM25 索引...")

            # 中文分词
            self.tokenized_corpus = []
            for doc in self.documents:
                # 使用 jieba 分词
                tokens = list(jieba.cut(doc.content))
                self.tokenized_corpus.append(tokens)

            # 构建 BM25 索引
            self.bm25_index = BM25Okapi(self.tokenized_corpus)

            print("BM25 索引构建完成！")
        except ImportError:
            print("警告: rank_bm25 或 jieba 未安装，BM25 检索不可用")
            self.bm25_index = None
        except Exception as e:
            print(f"BM25 索引构建失败: {e}")
            self.bm25_index = None

    def _save_index(self):
        """
        保存向量索引和文档
        """
        try:
            import faiss

            # 保存 FAISS 索引
            index_path = os.path.join(self.db_dir, "faiss_index.bin")
            faiss.write_index(self.index, index_path)

            # 保存文档数据
            docs_path = os.path.join(self.db_dir, "documents.json")
            docs_data = [doc.to_dict() for doc in self.documents]
            with open(docs_path, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, ensure_ascii=False, indent=2)

            print(f"索引已保存到: {self.db_dir}")
        except Exception as e:
            print(f"保存索引失败: {e}")

    def load_index(self):
        """
        加载已有的向量索引

        Returns:
            是否加载成功
        """
        try:
            import faiss

            index_path = os.path.join(self.db_dir, "faiss_index.bin")
            docs_path = os.path.join(self.db_dir, "documents.json")

            if not os.path.exists(index_path) or not os.path.exists(docs_path):
                print("索引文件不存在，请先构建索引")
                return False

            # 加载 FAISS 索引
            self.index = faiss.read_index(index_path)

            # 加载文档数据
            with open(docs_path, 'r', encoding='utf-8') as f:
                docs_data = json.load(f)
                self.documents = [DocumentChunk(**doc) for doc in docs_data]

            print(f"索引加载成功！文档数量: {self.index.ntotal}")

            # 重建 BM25 索引
            self._build_bm25_index()

            return True
        except Exception as e:
            print(f"加载索引失败: {e}")
            return False

    def search_vector(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果

        Returns:
            检索结果列表
        """
        if not self.model or not self.index:
            return []

        try:
            import numpy as np

            # 生成查询向量
            query_embedding = self._encode([query])

            # 检索
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                min(top_k, self.index.ntotal)
            )

            # 构建结果
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    results.append({
                        "content": self.documents[idx].content,
                        "source": self.documents[idx].source,
                        "distance": float(dist),
                        "score": 1.0 / (1.0 + float(dist)),  # 转换为相似度分数
                        "rank": i + 1,
                        "method": "vector"
                    })

            return results
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []

    def search_bm25(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        BM25 关键词检索

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果

        Returns:
            检索结果列表
        """
        if not self.bm25_index:
            return []

        try:
            import jieba

            # 查询分词
            query_tokens = list(jieba.cut(query))

            # BM25 检索
            scores = self.bm25_index.get_scores(query_tokens)

            # 获取 top_k 结果
            top_indices = scores.argsort()[-top_k:][::-1]

            results = []
            for i, idx in enumerate(top_indices):
                if idx < len(self.documents) and scores[idx] > 0:
                    results.append({
                        "content": self.documents[idx].content,
                        "source": self.documents[idx].source,
                        "score": float(scores[idx]),
                        "rank": i + 1,
                        "method": "bm25"
                    })

            return results
        except Exception as e:
            print(f"BM25 检索失败: {e}")
            return []

    def search_hybrid(self, query: str, top_k: int = 5, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """
        混合检索（向量检索 + BM25 关键词检索 + RRF 融合排序）

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            rrf_k: RRF 参数（控制排名融合的权重）

        Returns:
            融合后的检索结果列表
        """
        # 向量检索
        vector_results = self.search_vector(query, top_k=top_k * 2)

        # BM25 检索
        bm25_results = self.search_bm25(query, top_k=top_k * 2)

        # RRF 融合排序
        rrf_scores = {}

        # 处理向量检索结果
        for result in vector_results:
            content = result["content"]
            if content not in rrf_scores:
                rrf_scores[content] = {"score": 0, "data": result}
            rrf_scores[content]["score"] += 1.0 / (rrf_k + result["rank"])

        # 处理 BM25 检索结果
        for result in bm25_results:
            content = result["content"]
            if content not in rrf_scores:
                rrf_scores[content] = {"score": 0, "data": result}
            rrf_scores[content]["score"] += 1.0 / (rrf_k + result["rank"])

        # 按 RRF 分数排序
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)

        # 构建最终结果
        final_results = []
        for i, item in enumerate(sorted_results[:top_k]):
            result = item["data"].copy()
            result["rrf_score"] = item["score"]
            result["rank"] = i + 1
            result["method"] = "hybrid"
            final_results.append(result)

        return final_results

    def search(self, query: str, top_k: int = 3, method: str = "hybrid") -> List[Dict[str, Any]]:
        """
        统一检索接口

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            method: 检索方法（vector/bm25/hybrid）

        Returns:
            检索结果列表
        """
        if method == "vector":
            return self.search_vector(query, top_k)
        elif method == "bm25":
            return self.search_bm25(query, top_k)
        else:  # hybrid
            return self.search_hybrid(query, top_k)

    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        获取查询相关的上下文

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果

        Returns:
            拼接的上下文文本
        """
        results = self.search(query, top_k, method="hybrid")

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[参考{i}] {result['content']}")

        return "\n\n".join(context_parts)

    def add_document(self, file_path: str) -> bool:
        """
        添加新文档到知识库

        Args:
            file_path: 文件路径

        Returns:
            是否添加成功
        """
        try:
            path = Path(file_path)

            if not path.exists():
                print(f"文件不存在: {file_path}")
                return False

            # 读取文件内容
            content = self._read_file(path)
            if not content:
                print(f"文件内容为空: {file_path}")
                return False

            # 复制文件到知识库目录
            import shutil
            dest_path = Path(self.knowledge_dir) / path.name
            shutil.copy2(file_path, dest_path)

            # 智能分块
            new_chunks = self._split_document_smart(content, path.name)

            # 添加到文档列表
            start_id = len(self.documents)
            for i, chunk in enumerate(new_chunks):
                chunk.chunk_id = start_id + i
                self.documents.append(chunk)

            # 重新构建索引
            self.build_index()

            print(f"文档添加成功: {path.name} ({len(new_chunks)} 个片段)")
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False


def init_rag_system():
    """
    初始化 RAG 系统（项目级别调用）

    Returns:
        RAGSystem 实例
    """
    # 获取项目根目录
    project_dir = Path(__file__).parent.parent

    # 配置路径
    model_path = str(project_dir.parent / "向量模型")
    knowledge_dir = str(project_dir / "rag知识库")
    db_dir = str(project_dir / "rag" / "vector_db")

    # 创建 RAG 系统
    rag = RAGSystem(model_path, knowledge_dir, db_dir)

    # 尝试加载已有索引
    if rag.load_index():
        # 加载模型用于检索
        rag.load_model()
        return rag

    # 如果没有索引，构建新的
    print("首次运行，正在构建 RAG 知识库...")
    if rag.load_model() and rag.load_documents():
        rag.build_index()
        return rag

    print("RAG 系统初始化失败")
    return None
