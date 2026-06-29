"""
文件名: disease_agent.py
功能描述: 病害知识 Agent，负责病虫害知识分析（接入 RAG 知识库，支持无 LLM 模式）
作者: ZT
日期: 2026/6/17
"""

from typing import Dict, Any, List
from pathlib import Path
from .base_agent import BaseAgent


class DiseaseAgent(BaseAgent):
    """
    病害知识 Agent
    负责病虫害知识分析，接入 RAG 知识库
    支持 LLM 不可用时直接返回知识库检索结果
    """

    def __init__(self, llm_service):
        """
        初始化病害知识 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        self.rag_system = None  # RAG 系统实例
        self._init_rag()

    def _init_rag(self):
        """
        初始化 RAG 系统
        """
        try:
            from rag.rag_system import init_rag_system
            self.rag_system = init_rag_system()
            if self.rag_system:
                print("病害知识 Agent: RAG 知识库加载成功")
            else:
                print("病害知识 Agent: RAG 知识库加载失败")
        except Exception as e:
            print(f"病害知识 Agent: RAG 初始化失败: {e}")
            self.rag_system = None

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析病虫害信息

        Args:
            context: 包含病虫害识别结果的上下文

        Returns:
            病害知识分析结果
        """
        # 获取病虫害识别结果
        disease_result = context.get("disease_result", {})
        image_analysis = context.get("image_analysis", {})
        text_input = context.get("text_input", "")

        # 构建查询文本
        query = self._build_query(disease_result, image_analysis, text_input)

        # 从 RAG 知识库检索相关知识
        rag_context = ""
        rag_results = []
        if self.rag_system:
            rag_results = self.rag_system.search(query, top_k=3)
            rag_context = self.rag_system.get_context(query, top_k=3)

        # 判断 LLM 是否可用
        llm_available = self.llm_service.is_available if self.llm_service else False

        if llm_available:
            # LLM 可用，使用 LLM 生成分析
            analysis_prompt = self._build_analysis_prompt(
                disease_result, image_analysis, text_input, rag_context
            )

            system_prompt = """你是一个植物病害专家。根据病虫害识别结果和相关知识库信息，
分析病害的成因、传播途径、危害程度，并提供详细的防治建议。

请用通俗易懂的语言回答，适合农户理解。
如果知识库中有相关信息，请优先参考使用。"""

            user_prompt = f"""{analysis_prompt}

请提供：
1. 病害确认与分析
2. 病害成因
3. 传播途径
4. 危害程度评估
5. 防治建议（物理、化学、生物方法）
6. 预防措施"""

            response = await self._call_llm(system_prompt, user_prompt)

            return {
                "success": True,
                "disease_name": disease_result.get("disease_name", "未知"),
                "confidence": disease_result.get("confidence", 0),
                "analysis": response,
                "knowledge_source": "RAG + LLM",
                "rag_references": rag_context[:500] if rag_context else ""
            }
        else:
            # LLM 不可用，直接返回 RAG 检索结果
            return self._build_rag_response(disease_result, rag_results, rag_context)

    def _build_rag_response(
        self,
        disease_result: Dict,
        rag_results: List[Dict],
        rag_context: str
    ) -> Dict[str, Any]:
        """
        构建 RAG 模式的响应（无 LLM）

        Args:
            disease_result: 病虫害识别结果
            rag_results: RAG 检索结果
            rag_context: RAG 上下文文本

        Returns:
            响应字典
        """
        disease_name = disease_result.get("disease_name", "未知")
        confidence = disease_result.get("confidence", 0)
        symptoms = disease_result.get("symptoms", [])

        # 构建分析文本
        analysis_parts = []
        analysis_parts.append(f"📌 病害识别结果：{disease_name}")
        analysis_parts.append(f"📊 置信度：{confidence}%")

        if symptoms:
            analysis_parts.append(f"🔍 症状：{', '.join(symptoms)}")

        analysis_parts.append("")

        if rag_context:
            analysis_parts.append("📚 【知识库相关信息】")
            analysis_parts.append(rag_context)
        else:
            analysis_parts.append("⚠️ 未找到相关知识库信息")

        analysis_parts.append("")
        analysis_parts.append("💡 提示：如需更详细的个性化建议，请确保大模型服务可用。")

        return {
            "success": True,
            "disease_name": disease_name,
            "confidence": confidence,
            "analysis": "\n".join(analysis_parts),
            "knowledge_source": "RAG only (LLM unavailable)",
            "rag_references": rag_context[:500] if rag_context else ""
        }

    def _build_query(self, disease_result: Dict, image_analysis: Dict, text_input: str) -> str:
        """
        构建查询文本

        Args:
            disease_result: 病虫害识别结果
            image_analysis: 图像分析结果
            text_input: 用户文字描述

        Returns:
            查询文本
        """
        parts = []

        # 添加病害名称
        disease_name = disease_result.get("disease_name", "")
        if disease_name and disease_name != "未知":
            parts.append(disease_name)

        # 添加症状
        symptoms = disease_result.get("symptoms", [])
        if symptoms:
            parts.extend(symptoms)

        # 添加用户描述
        if text_input:
            parts.append(text_input)

        # 如果没有足够信息，使用通用查询
        if not parts:
            parts.append("番茄病虫害防治")

        return " ".join(parts)

    def _build_analysis_prompt(
        self,
        disease_result: Dict,
        image_analysis: Dict,
        text_input: str,
        rag_context: str
    ) -> str:
        """
        构建分析提示词

        Args:
            disease_result: 病虫害识别结果
            image_analysis: 图像分析结果
            text_input: 用户文字描述
            rag_context: RAG 检索的上下文

        Returns:
            提示词
        """
        parts = ["请分析以下病虫害信息：\n"]

        if disease_result:
            parts.append(f"识别结果：{disease_result.get('disease_name', '未知')}")
            parts.append(f"置信度：{disease_result.get('confidence', 0)}%")
            if disease_result.get("symptoms"):
                parts.append(f"症状：{', '.join(disease_result['symptoms'])}")

        if image_analysis:
            parts.append(f"\n图像分析：{image_analysis.get('raw_analysis', '')}")

        if text_input:
            parts.append(f"\n用户描述：{text_input}")

        if rag_context:
            parts.append(f"\n\n知识库参考信息：\n{rag_context}")

        return "\n".join(parts)
