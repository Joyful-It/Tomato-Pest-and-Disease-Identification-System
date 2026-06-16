"""
文件名: weather_agent.py
功能描述: 天气 Agent，负责天气分析和对病虫害的影响评估
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from services.weather_service import WeatherService


class WeatherAgent(BaseAgent):
    """
    天气 Agent
    负责天气分析，评估天气对病虫害的影响
    """

    def __init__(self, llm_service):
        """
        初始化天气 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        self.weather_service = WeatherService()

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析天气情况及其对病虫害的影响

        Args:
            context: 包含位置信息的上下文

        Returns:
            天气分析结果
        """
        # 获取位置信息
        latitude = context.get("latitude", 0)
        longitude = context.get("longitude", 0)
        disease_result = context.get("disease_result", {})

        # 获取天气数据
        weather_data = await self.weather_service.get_weather(latitude, longitude)

        if not weather_data.get("success"):
            return {
                "success": False,
                "error": weather_data.get("error", "天气查询失败")
            }

        # 分析天气对病虫害的影响
        impact_analysis = await self._analyze_weather_impact(
            weather_data, disease_result
        )

        # 生成天气相关建议
        advice = await self._generate_weather_advice(
            weather_data, disease_result, impact_analysis
        )

        return {
            "success": True,
            "weather_data": weather_data,
            "impact_analysis": impact_analysis,
            "advice": advice
        }

    async def _analyze_weather_impact(
        self,
        weather_data: Dict,
        disease_result: Dict
    ) -> Dict[str, Any]:
        """
        分析天气对病虫害的影响

        Args:
            weather_data: 天气数据
            disease_result: 病虫害识别结果

        Returns:
            影响分析结果
        """
        today = weather_data.get("today", {})
        temperature = today.get("temperature", {})
        humidity = today.get("humidity", {})
        skycon = today.get("skycon", "")

        # 构建分析提示词
        prompt = f"""根据以下天气信息，分析对番茄病虫害的影响：

当前天气：
- 温度：最高 {temperature.get('max', 0)}°C，最低 {temperature.get('min', 0)}°C，平均 {temperature.get('avg', 0)}°C
- 湿度：{humidity.get('avg', 0)}%
- 天气：{today.get('description', '未知')}

病虫害信息：
- 病害：{disease_result.get('disease_name', '未知')}

请分析：
1. 当前天气是否有利于病害发展？
2. 未来几天天气对病害的可能影响
3. 需要特别注意的天气变化"""

        system_prompt = "你是一个农业气象专家，请分析天气对番茄病虫害的影响。"

        response = await self._call_llm(system_prompt, prompt)

        return {
            "analysis": response,
            "temperature": temperature,
            "humidity": humidity,
            "weather_condition": skycon
        }

    async def _generate_weather_advice(
        self,
        weather_data: Dict,
        disease_result: Dict,
        impact_analysis: Dict
    ) -> str:
        """
        生成天气相关建议

        Args:
            weather_data: 天气数据
            disease_result: 病虫害结果
            impact_analysis: 影响分析

        Returns:
            天气建议
        """
        prompt = f"""根据天气分析结果，为农户提供具体的操作建议：

天气分析：{impact_analysis.get('analysis', '')}

病害类型：{disease_result.get('disease_name', '未知')}

请提供：
1. 适合施药的天气条件
2. 需要避免的天气操作
3. 天气相关的防护措施"""

        system_prompt = "你是一个农业技术员，请根据天气情况为农户提供实用的操作建议。"

        return await self._call_llm(system_prompt, prompt)