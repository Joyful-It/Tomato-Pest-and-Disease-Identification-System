"""
文件名: build_index.py
功能描述: 构建 RAG 向量索引的脚本（增强版）
作者: ZT
日期: 2026/6/17
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

from rag.rag_system import RAGSystem


def main():
    """主函数"""
    print("=" * 60)
    print("RAG 知识库索引构建工具（增强版）")
    print("=" * 60)

    # 配置路径
    model_path = str(project_dir.parent / "向量模型")
    knowledge_dir = str(project_dir / "rag知识库")
    db_dir = str(project_dir / "rag" / "vector_db")

    print(f"\n向量模型路径: {model_path}")
    print(f"知识文档目录: {knowledge_dir}")
    print(f"向量数据库目录: {db_dir}")

    # 创建 RAG 系统
    rag = RAGSystem(model_path, knowledge_dir, db_dir)

    # 加载模型
    print("\n正在加载向量模型...")
    if not rag.load_model():
        print("模型加载失败！")
        return

    # 加载文档
    print("\n正在加载知识文档...")
    if not rag.load_documents():
        print("文档加载失败！")
        return

    # 构建索引
    print("\n正在构建向量索引...")
    if rag.build_index():
        print("\n" + "=" * 60)
        print("索引构建完成！")
        print("=" * 60)

        # 测试检索
        print("\n测试混合检索功能:")
        test_queries = [
            "番茄早疫病怎么防治？",
            "河南省土壤类型有哪些？",
            "番茄叶子发黄是什么原因？"
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            print("-" * 40)

            # 向量检索
            print("【向量检索】")
            vector_results = rag.search_vector(query, top_k=2)
            for result in vector_results:
                print(f"  - [{result['source']}] {result['content'][:80]}...")

            # BM25 检索
            print("【BM25 检索】")
            bm25_results = rag.search_bm25(query, top_k=2)
            for result in bm25_results:
                print(f"  - [{result['source']}] {result['content'][:80]}...")

            # 混合检索
            print("【混合检索】")
            hybrid_results = rag.search_hybrid(query, top_k=2)
            for result in hybrid_results:
                print(f"  - [{result['source']}] (RRF: {result.get('rrf_score', 0):.4f}) {result['content'][:80]}...")
    else:
        print("索引构建失败！")


if __name__ == "__main__":
    main()
