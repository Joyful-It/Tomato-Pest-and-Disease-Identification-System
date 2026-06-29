"""
文件名: llm_service.py
功能描述: LLM 服务封装，提供与大语言模型的交互接口，支持降级到 RAG 模式
作者: ZT
日期: 2026/6/17
"""

from typing import Optional, List, Dict, Any
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE


class LLMService:
    """
    LLM 服务类
    封装与大语言模型的交互，提供统一的调用接口
    支持大模型不可用时降级到 RAG 模式
    """

    def __init__(self):
        """初始化 LLM 服务"""
        self.llm = None
        self.is_available = False
        self._init_llm()

    def _init_llm(self):
        """
        初始化 LLM 模型
        """
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                api_key=LLM_API_KEY,
                base_url=LLM_BASE_URL,
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE
            )
            self.is_available = True
            print("LLM 服务初始化成功")
        except Exception as e:
            print(f"LLM 服务初始化失败: {e}")
            print("将使用纯 RAG 模式")
            self.is_available = False

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        与 LLM 进行对话

        Args:
            messages: 消息列表，每个消息包含 role 和 content

        Returns:
            LLM 的回复内容
        """
        if not self.is_available:
            return None

        try:
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            # 转换消息格式
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))

            # 调用 LLM
            response = await self.llm.ainvoke(langchain_messages)
            return response.content
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            self.is_available = False
            return None

    async def generate_final_advice(
        self,
        disease_result: Optional[Dict] = None,
        weather_analysis: Optional[Dict] = None,
        soil_analysis: Optional[Dict] = None,
        irrigation_advice: Optional[Dict] = None,
        safety_advice: Optional[Dict] = None,
        calendar_advice: Optional[Dict] = None,
        user_memory: Optional[Dict] = None,
        rag_context: str = "",
        disease_agent_analysis: str = ""
    ) -> str:
        """
        综合所有分析结果，生成最终建议

        Args:
            disease_result: 病虫害识别结果
            weather_analysis: 天气分析结果
            soil_analysis: 土壤分析结果
            irrigation_advice: 灌溉建议
            safety_advice: 安全用药建议
            calendar_advice: 种植日历建议
            user_memory: 用户记忆
            rag_context: RAG 知识库检索结果
            disease_agent_analysis: disease_agent 的分析结果（已结合 RAG）

        Returns:
            最终综合建议
        """
        # 如果 LLM 可用，使用 LLM 生成建议
        if self.is_available:
            prompt = self._build_final_advice_prompt(
                disease_result, weather_analysis, soil_analysis,
                irrigation_advice, safety_advice, calendar_advice, user_memory,
                rag_context, disease_agent_analysis
            )

            messages = [
                {"role": "system", "content": """你是一个资深的农业专家。请根据以下信息为农户提供详细的防治建议。

要求：
1. 综合病害识别结果、知识库参考信息、专业分析等多个来源
2. 建议应该具体、实用、易于理解
3. 如果有知识库信息，优先参考并整合到建议中
4. 用通俗的语言，适合农户理解"""},
                {"role": "user", "content": prompt}
            ]

            response = await self.chat(messages)
            if response:
                return response

        # LLM 不可用，使用 RAG 结果构建建议
        return self._build_rag_based_advice(
            disease_result, weather_analysis, soil_analysis,
            irrigation_advice, safety_advice, rag_context
        )

    def _build_rag_based_advice(
        self,
        disease_result: Optional[Dict],
        weather_analysis: Optional[Dict],
        soil_analysis: Optional[Dict],
        irrigation_advice: Optional[Dict],
        safety_advice: Optional[Dict],
        rag_context: str
    ) -> str:
        """
        使用 RAG 检索结果构建建议（无 LLM 模式）

        Args:
            各分析模块的结果
            rag_context: RAG 检索结果

        Returns:
            基于知识库的建议
        """
        parts = []
        parts.append("【基于知识库的诊断结果】\n")

        # 病害信息
        if disease_result:
            disease_name = disease_result.get("disease_name", "未知")
            confidence = disease_result.get("confidence", 0)
            parts.append(f"📌 识别结果：{disease_name}")
            parts.append(f"📊 置信度：{confidence}%")

            if disease_result.get("symptoms"):
                parts.append(f"🔍 症状：{', '.join(disease_result['symptoms'])}")
            parts.append("")

        # RAG 知识库内容
        if rag_context:
            parts.append("📚 【知识库参考信息】")
            parts.append(rag_context)
            parts.append("")

        # 天气信息
        if weather_analysis and weather_analysis.get("success"):
            parts.append("🌤️ 【天气信息】")
            today = weather_analysis.get("today", {})
            if today:
                parts.append(f"天气：{today.get('description', '未知')}")
                parts.append(f"温度：{today.get('temperature', {}).get('min', 0)}°C ~ {today.get('temperature', {}).get('max', 0)}°C")
            parts.append("")

        # 土壤信息
        if soil_analysis and soil_analysis.get("success"):
            parts.append("🌱 【土壤信息】")
            parts.append(soil_analysis.get("disease_relation", ""))
            parts.append("")

        # 温馨提示
        parts.append("💡 【温馨提示】")
        parts.append("以上信息基于知识库检索，如需更详细的个性化建议，请确保大模型服务可用后重新诊断。")

        return "\n".join(parts)

    def _build_final_advice_prompt(
        self,
        disease_result: Optional[Dict],
        weather_analysis: Optional[Dict],
        soil_analysis: Optional[Dict],
        irrigation_advice: Optional[Dict],
        safety_advice: Optional[Dict],
        calendar_advice: Optional[Dict],
        user_memory: Optional[Dict],
        rag_context: str,
        disease_agent_analysis: str = ""
    ) -> str:
        """
        构建最终建议的提示词

        Args:
            各分析模块的结果
            disease_agent_analysis: disease_agent 的分析结果

        Returns:
            格式化的提示词
        """
        parts = ["请根据以下信息为番茄种植提供综合防治建议：\n"]

        # 病害识别结果
        if disease_result:
            parts.append("【病害识别结果】")
            parts.append(f"- 病害名称：{disease_result.get('disease_name', '未知')}")
            parts.append(f"- 置信度：{disease_result.get('confidence', 0)}")
            if disease_result.get('symptoms'):
                parts.append(f"- 症状：{', '.join(disease_result['symptoms'])}")
            parts.append("")

        # 知识库参考信息
        if rag_context:
            parts.append("【知识库参考信息】")
            parts.append(rag_context)
            parts.append("")

        # disease_agent 的专业分析（已结合 RAG）
        if disease_agent_analysis:
            parts.append("【专业分析结果】")
            parts.append(disease_agent_analysis)
            parts.append("")

        # 其他 Agent 分析结果
        if weather_analysis:
            parts.append("【天气分析】")
            parts.append(str(weather_analysis))
            parts.append("")

        if soil_analysis:
            parts.append("【土壤分析】")
            parts.append(str(soil_analysis))
            parts.append("")

        if irrigation_advice:
            parts.append("【灌溉建议】")
            parts.append(str(irrigation_advice))
            parts.append("")

        if safety_advice:
            parts.append("【安全用药建议】")
            parts.append(str(safety_advice))
            parts.append("")

        if calendar_advice:
            parts.append("【种植日历建议】")
            parts.append(str(calendar_advice))
            parts.append("")

        parts.append("\n请综合以上所有信息，提供详细、具体、实用的防治建议。")

        return "\n".join(parts)

    def _extract_symptoms(self, description: str) -> List[str]:
        """
        从描述中提取症状关键词

        Args:
            description: 描述文本

        Returns:
            症状列表
        """
        symptom_keywords = [
            "黄叶", "枯萎", "斑点", "腐烂", "虫蛀", "卷曲",
            "变色", "脱落", "畸形", "萎蔫", "坏死", "水渍"
        ]

        found_symptoms = []
        for keyword in symptom_keywords:
            if keyword in description:
                found_symptoms.append(keyword)

        return found_symptoms
