"""
文件名: llm_service.py
功能描述: LLM 服务封装，提供与大语言模型的交互接口
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE


class LLMService:
    """
    LLM 服务类
    封装与大语言模型的交互，提供统一的调用接口
    """

    def __init__(self):
        """初始化 LLM 服务"""
        self.llm = ChatOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE
        )

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        与 LLM 进行对话

        Args:
            messages: 消息列表，每个消息包含 role 和 content

        Returns:
            LLM 的回复内容
        """
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

    async def analyze_image_description(self, description: str) -> Dict[str, Any]:
        """
        分析图像描述，提取关键信息

        Args:
            description: 图像描述文本

        Returns:
            分析结果字典
        """
        messages = [
            {"role": "system", "content": "你是一个农业专家，请分析以下作物图像描述，提取病虫害相关信息。"},
            {"role": "user", "content": f"请分析这个图像描述，提取病虫害相关信息：\n{description}"}
        ]

        response = await self.chat(messages)

        return {
            "raw_analysis": response,
            "has_disease": "病" in description or "虫" in description or "害" in description,
            "symptoms": self._extract_symptoms(description)
        }

    async def generate_final_advice(
        self,
        disease_result: Optional[Dict] = None,
        weather_analysis: Optional[Dict] = None,
        soil_analysis: Optional[Dict] = None,
        irrigation_advice: Optional[Dict] = None,
        safety_advice: Optional[Dict] = None,
        calendar_advice: Optional[Dict] = None,
        user_memory: Optional[Dict] = None
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

        Returns:
            最终综合建议
        """
        prompt = self._build_final_advice_prompt(
            disease_result, weather_analysis, soil_analysis,
            irrigation_advice, safety_advice, calendar_advice, user_memory
        )

        messages = [
            {"role": "system", "content": "你是一个资深的农业专家，请根据以下信息为农户提供详细的防治建议。建议应该具体、实用、易于理解。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.chat(messages)
        return response

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

    def _build_final_advice_prompt(
        self,
        disease_result: Optional[Dict],
        weather_analysis: Optional[Dict],
        soil_analysis: Optional[Dict],
        irrigation_advice: Optional[Dict],
        safety_advice: Optional[Dict],
        calendar_advice: Optional[Dict],
        user_memory: Optional[Dict]
    ) -> str:
        """
        构建最终建议的提示词

        Args:
            各分析模块的结果

        Returns:
            格式化的提示词
        """
        parts = ["请根据以下信息为番茄种植提供综合防治建议：\n"]

        if disease_result:
            parts.append(f"病虫害识别结果：{disease_result}\n")

        if weather_analysis:
            parts.append(f"天气分析：{weather_analysis}\n")

        if soil_analysis:
            parts.append(f"土壤分析：{soil_analysis}\n")

        if irrigation_advice:
            parts.append(f"灌溉建议：{irrigation_advice}\n")

        if safety_advice:
            parts.append(f"安全用药建议：{safety_advice}\n")

        if calendar_advice:
            parts.append(f"种植日历建议：{calendar_advice}\n")

        if user_memory:
            parts.append(f"用户历史记录：{user_memory}\n")

        parts.append("\n请提供详细、具体、实用的防治建议，包括：")
        parts.append("1. 病虫害诊断确认")
        parts.append("2. 防治措施（物理、化学、生物方法）")
        parts.append("3. 用药建议（如果需要）")
        parts.append("4. 预防措施")
        parts.append("5. 后续观察要点")

        return "\n".join(parts)
