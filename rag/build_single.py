"""
文件名: build_single.py
功能描述: 使用单个文档构建 RAG 知识库（优化分词版）
作者: ZT
日期: 2026/6/17
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

from rag.rag_system import RAGSystem, DocumentChunk


def main():
    """主函数"""
    print("=" * 60)
    print("RAG 知识库单文档构建工具（优化分词版）")
    print("=" * 60)

    # 配置路径
    model_path = str(project_dir.parent / "向量模型")
    knowledge_dir = str(project_dir / "rag知识库")
    db_dir = str(project_dir / "rag" / "vector_db")

    # 指定要使用的文档
    target_doc = "土壤性质与番茄病虫害.txt"

    print(f"\n向量模型路径: {model_path}")
    print(f"目标文档: {target_doc}")
    print(f"向量数据库目录: {db_dir}")

    # 创建 RAG 系统
    rag = RAGSystem(model_path, knowledge_dir, db_dir)

    # 加载模型
    print("\n正在加载向量模型...")
    if not rag.load_model():
        print("模型加载失败！")
        return

    # 只加载指定文档
    print(f"\n正在加载文档: {target_doc}")
    doc_path = Path(knowledge_dir) / target_doc

    if not doc_path.exists():
        print(f"文档不存在: {doc_path}")
        return

    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用优化的分块策略
    chunks = split_document_optimized(content, target_doc)
    rag.documents = chunks

    print(f"文档分块完成: {len(chunks)} 个片段")

    # 显示分块示例
    print("\n分块示例:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  [{i+1}] {chunk.content[:100]}...")

    # 构建索引
    print("\n正在构建向量索引...")
    if rag.build_index():
        print("\n" + "=" * 60)
        print("索引构建完成！")
        print("=" * 60)

        # 测试检索
        print("\n测试检索功能:")
        test_queries = [
            "番茄早疫病怎么防治？",
            "河南豫北地区土壤是什么性质？",
            "番茄叶子发黄是什么原因？",
            "潮土的pH值是多少？",
            "如何防治番茄青枯病？"
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            print("-" * 40)

            # 混合检索
            results = rag.search_hybrid(query, top_k=2)
            for result in results:
                print(f"  - [RRF: {result.get('rrf_score', 0):.4f}] {result['content'][:120]}...")
    else:
        print("索引构建失败！")


def split_document_optimized(content: str, source: str) -> list:
    """
    优化的文档分块策略
    按照章节、段落、句子层次分块，保持语义完整性

    Args:
        content: 文档内容
        source: 文档来源

    Returns:
        文档片段列表
    """
    chunks = []

    # 按照大章节分割（=== 分隔符）
    sections = content.split("================================================================================")

    current_section = ""
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # 检查是否是章节标题
        if section.startswith("第") and "部分" in section:
            current_section = section.split("\n")[0]
            continue

        # 按照子章节分割（--- 分隔符）
        subsections = section.split("----------------------------------------------------------------------")

        for subsection in subsections:
            subsection = subsection.strip()
            if not subsection:
                continue

            # 如果内容较短，直接作为一个片段
            if len(subsection) < 600:
                if subsection:
                    chunks.append(DocumentChunk(
                        content=subsection,
                        source=source,
                        chunk_id=len(chunks),
                        metadata={"section": current_section, "method": "section_split"}
                    ))
            else:
                # 内容较长，按段落分割
                paragraphs = subsection.split("\n\n")
                current_chunk = ""

                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue

                    # 如果当前块加上新段落超过限制，保存当前块
                    if len(current_chunk) + len(para) > 500 and current_chunk:
                        chunks.append(DocumentChunk(
                            content=current_chunk.strip(),
                            source=source,
                            chunk_id=len(chunks),
                            metadata={"section": current_section, "method": "paragraph_split"}
                        ))
                        # 保留重叠部分
                        if len(current_chunk) > 50:
                            current_chunk = current_chunk[-50:] + "\n\n" + para
                        else:
                            current_chunk = para
                    else:
                        current_chunk += "\n\n" + para if current_chunk else para

                # 保存最后一个块
                if current_chunk.strip():
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        source=source,
                        chunk_id=len(chunks),
                        metadata={"section": current_section, "method": "paragraph_split"}
                    ))

    return chunks


if __name__ == "__main__":
    main()
