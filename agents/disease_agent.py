"""
文件名: disease_agent.py
功能描述: 病害知识 Agent，负责病虫害知识分析（预留 RAG 接口）
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class DiseaseAgent(BaseAgent):
    """
    病害知识 Agent
    负责病虫害知识分析，预留 RAG 知识库接口
    """

    def __init__(self, llm_service):
        """
        初始化病害知识 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        # 预留：RAG 知识库初始化
        self.knowledge_base = None  # TODO: 接入 RAG 知识库

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

        # 构建分析提示词
        analysis_prompt = self._build_analysis_prompt(
            disease_result, image_analysis, text_input
        )

        # 查询知识库（预留）
        knowledge = await self._query_knowledge_base(disease_result)

        # 调用 LLM 进行分析
        system_prompt = """你是一个植物病害专家。根据病虫害识别结果和相关知识，
分析病害的成因、传播途径、危害程度，并提供详细的防治建议。

请用通俗易懂的语言回答，适合农户理解。"""

        user_prompt = f"""{analysis_prompt}

知识库参考信息：
{knowledge if knowledge else "暂无知识库数据"}

请提供：
1. 病害确认与分析
2. 病害成因
3. 传播途径
4. 危害程度评估
5. 防治建议（物理、化学、生物方法）"""

        response = await self._call_llm(system_prompt, user_prompt)

        return {
            "success": True,
            "disease_name": disease_result.get("disease_name", "未知"),
            "confidence": disease_result.get("confidence", 0),
            "analysis": response,
            "knowledge_source": "RAG" if knowledge else "LLM"
        }

    def _build_analysis_prompt(
        self,
        disease_result: Dict,
        image_analysis: Dict,
        text_input: str
    ) -> str:
        """
        构建分析提示词

        Args:
            disease_result: 病虫害识别结果
            image_analysis: 图像分析结果
            text_input: 用户文字描述

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

        return "\n".join(parts)

    async def _query_knowledge_base(self, disease_result: Dict) -> str:
        """
        查询知识库（预留 RAG 接口）

        Args:
            disease_result: 病虫害识别结果

        Returns:
            知识库查询结果
        """
        # TODO: 实现 RAG 知识库查询
        # 这里预留接口，之后接入 RAG 系统
        if self.knowledge_base:
            # 实际的 RAG 查询逻辑
            pass

        # 返回 None 表示知识库未配置
        return None