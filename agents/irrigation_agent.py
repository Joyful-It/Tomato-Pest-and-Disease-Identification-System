"""
文件名: irrigation_agent.py
功能描述: 灌溉 Agent，负责灌溉建议和水分管理
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class IrrigationAgent(BaseAgent):
    """
    灌溉 Agent
    负责提供灌溉建议和水分管理方案
    """

    def __init__(self, llm_service):
        """
        初始化灌溉 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析灌溉需求

        Args:
            context: 包含天气、土壤、病害信息的上下文

        Returns:
            灌溉建议
        """
        # 获取相关信息
        weather_data = context.get("weather_data", {})
        soil_data = context.get("soil_data", {})
        disease_result = context.get("disease_result", {})
        weather_analysis = context.get("weather_analysis", {})

        # 分析灌溉需求
        irrigation_needs = await self._analyze_irrigation_needs(
            weather_data, soil_data, disease_result
        )

        # 生成灌溉建议
        irrigation_advice = await self._generate_irrigation_advice(
            weather_data, soil_data, disease_result, irrigation_needs
        )

        # 生成灌溉计划
        irrigation_plan = await self._generate_irrigation_plan(
            weather_data, soil_data, irrigation_needs
        )

        return {
            "success": True,
            "irrigation_needs": irrigation_needs,
            "advice": irrigation_advice,
            "plan": irrigation_plan
        }

    async def _analyze_irrigation_needs(
        self,
        weather_data: Dict,
        soil_data: Dict,
        disease_result: Dict
    ) -> Dict[str, Any]:
        """
        分析灌溉需求

        Args:
            weather_data: 天气数据
            soil_data: 土壤数据
            disease_result: 病害结果

        Returns:
            灌溉需求分析
        """
        # 提取关键数据
        today_weather = weather_data.get("today", {})
        temperature = today_weather.get("temperature", {})
        humidity = today_weather.get("humidity", {})
        soil_info = soil_data.get("soil_data", {})

        prompt = f"""分析番茄的灌溉需求：

天气信息：
- 温度：最高 {temperature.get('max', 0)}°C，最低 {temperature.get('min', 0)}°C
- 湿度：{humidity.get('avg', 0)}%
- 天气：{today_weather.get('description', '未知')}

土壤信息：
- 质地：{soil_info.get('texture', '未知')}
- 排水性：{soil_info.get('drainage', '未知')}
- 有机质：{soil_info.get('organic_matter', 0)}%

病害信息：
- 病害：{disease_result.get('disease_name', '未知')}

请分析：
1. 当前是否需要灌溉？
2. 灌溉的紧迫程度（高/中/低）
3. 病害对灌溉的特殊要求"""

        system_prompt = "你是一个灌溉专家，请分析番茄的灌溉需求。"

        response = await self._call_llm(system_prompt, prompt)

        return {
            "analysis": response,
            "temperature": temperature.get("avg", 0),
            "humidity": humidity.get("avg", 0),
            "soil_drainage": soil_info.get("drainage", "未知")
        }

    async def _generate_irrigation_advice(
        self,
        weather_data: Dict,
        soil_data: Dict,
        disease_result: Dict,
        irrigation_needs: Dict
    ) -> str:
        """
        生成灌溉建议

        Args:
            weather_data: 天气数据
            soil_data: 土壤数据
            disease_result: 病害结果
            irrigation_needs: 灌溉需求分析

        Returns:
            灌溉建议
        """
        prompt = f"""根据灌溉需求分析，提供具体的灌溉建议：

需求分析：{irrigation_needs.get('analysis', '')}

病害类型：{disease_result.get('disease_name', '未知')}

请提供：
1. 推荐的灌溉方式（滴灌、喷灌、沟灌等）
2. 灌溉时间建议
3. 灌溉量建议
4. 病害期间的特殊灌溉注意事项"""

        system_prompt = "你是一个灌溉技术专家，请提供实用、节水的灌溉方案。"

        return await self._call_llm(system_prompt, prompt)

    async def _generate_irrigation_plan(
        self,
        weather_data: Dict,
        soil_data: Dict,
        irrigation_needs: Dict
    ) -> Dict[str, Any]:
        """
        生成灌溉计划

        Args:
            weather_data: 天气数据
            soil_data: 土壤数据
            irrigation_needs: 灌溉需求

        Returns:
            灌溉计划
        """
        forecast = weather_data.get("forecast", [])

        # 根据天气预报生成未来几天的灌溉计划
        plan = []
        for day in forecast[:7]:  # 未来7天
            day_plan = {
                "day": day.get("day", 0),
                "weather": day.get("description", "未知"),
                "temperature": day.get("temperature", {}),
                "irrigation_recommended": self._should_irrigate(day, irrigation_needs),
                "notes": ""
            }
            plan.append(day_plan)

        return {
            "weekly_plan": plan,
            "summary": "根据天气预报生成的7天灌溉计划"
        }

    def _should_irrigate(self, weather: Dict, needs: Dict) -> bool:
        """
        判断是否需要灌溉

        Args:
            weather: 天气信息
            needs: 灌溉需求

        Returns:
            是否需要灌溉
        """
        # 简单判断：高温低湿时需要灌溉
        temp = weather.get("temperature", {})
        avg_temp = temp.get("avg", 25)

        # 如果温度高于25度，建议灌溉
        return avg_temp > 25
