"""
文件名: calendar_agent.py
功能描述: 种植日历 Agent，负责农事提醒和种植计划
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from .base_agent import BaseAgent


class CalendarAgent(BaseAgent):
    """
    种植日历 Agent
    负责提供农事提醒和种植计划
    """

    def __init__(self, llm_service):
        """
        初始化种植日历 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析种植日历需求

        Args:
            context: 包含各 Agent 分析结果的上下文

        Returns:
            种植日历建议
        """
        # 获取各 Agent 的分析结果
        disease_result = context.get("disease_result", {})
        weather_data = context.get("weather_data", {})
        soil_data = context.get("soil_data", {})
        irrigation_advice = context.get("irrigation_advice", {})
        safety_advice = context.get("safety_advice", {})

        # 获取当前日期
        current_date = datetime.now()

        # 生成农事日历
        farming_calendar = await self._generate_farming_calendar(
            current_date, disease_result, weather_data, soil_data
        )

        # 生成农事提醒
        farming_reminders = await self._generate_farming_reminders(
            current_date, disease_result, weather_data, irrigation_advice, safety_advice
        )

        # 生成阶段性管理计划
        management_plan = await self._generate_management_plan(
            current_date, disease_result, weather_data
        )

        return {
            "success": True,
            "current_date": current_date.strftime("%Y-%m-%d"),
            "farming_calendar": farming_calendar,
            "farming_reminders": farming_reminders,
            "management_plan": management_plan
        }

    async def _generate_farming_calendar(
        self,
        current_date: datetime,
        disease_result: Dict,
        weather_data: Dict,
        soil_data: Dict
    ) -> Dict[str, Any]:
        """
        生成农事日历

        Args:
            current_date: 当前日期
            disease_result: 病害结果
            weather_data: 天气数据
            soil_data: 土壤数据

        Returns:
            农事日历
        """
        # 计算未来7天的日期
        dates = []
        for i in range(7):
            date = current_date + timedelta(days=i)
            dates.append(date.strftime("%m月%d日"))

        prompt = f"""根据当前日期和病虫害情况，生成未来7天的农事日历：

当前日期：{current_date.strftime('%Y年%m月%d日')}
病害情况：{disease_result.get('disease_name', '未知')}
天气预报：{weather_data.get('forecast', [])}

请为每一天安排合适的农事活动，包括：
1. 施药/防治
2. 田间管理
3. 观察记录
4. 其他农事"""

        system_prompt = "你是一个农业技术专家，请根据实际情况安排合理的农事活动。"

        response = await self._call_llm(system_prompt, prompt)

        return {
            "dates": dates,
            "arrangement": response
        }

    async def _generate_farming_reminders(
        self,
        current_date: datetime,
        disease_result: Dict,
        weather_data: Dict,
        irrigation_advice: Dict,
        safety_advice: Dict
    ) -> list:
        """
        生成农事提醒

        Args:
            current_date: 当前日期
            disease_result: 病害结果
            weather_data: 天气数据
            irrigation_advice: 灌溉建议
            safety_advice: 用药建议

        Returns:
            提醒列表
        """
        reminders = []

        # 根据病害添加提醒
        disease_name = disease_result.get("disease_name", "")
        if disease_name and disease_name != "未知":
            reminders.append({
                "type": "disease",
                "priority": "high",
                "title": f"病害防治提醒",
                "content": f"检测到{disease_name}，请及时采取防治措施",
                "date": current_date.strftime("%Y-%m-%d")
            })

        # 根据天气添加提醒
        today_weather = weather_data.get("today", {})
        if today_weather.get("description") in ["小雨", "中雨", "大雨"]:
            reminders.append({
                "type": "weather",
                "priority": "medium",
                "title": "雨天提醒",
                "content": "雨天注意排水防涝，避免病害扩散",
                "date": current_date.strftime("%Y-%m-%d")
            })

        # 根据灌溉建议添加提醒
        if irrigation_advice.get("irrigation_needs", {}).get("analysis"):
            reminders.append({
                "type": "irrigation",
                "priority": "medium",
                "title": "灌溉提醒",
                "content": "根据分析，近期需要关注灌溉",
                "date": current_date.strftime("%Y-%m-%d")
            })

        # 根据用药建议添加提醒
        if safety_advice.get("medication_advice"):
            reminders.append({
                "type": "medication",
                "priority": "high",
                "title": "用药提醒",
                "content": "请按照用药建议进行施药，注意安全间隔期",
                "date": current_date.strftime("%Y-%m-%d")
            })

        # 添加通用提醒
        reminders.append({
            "type": "observation",
            "priority": "low",
            "title": "日常观察",
            "content": "每天观察番茄生长情况，记录病害变化",
            "date": current_date.strftime("%Y-%m-%d")
        })

        return reminders

    async def _generate_management_plan(
        self,
        current_date: datetime,
        disease_result: Dict,
        weather_data: Dict
    ) -> Dict[str, Any]:
        """
        生成阶段性管理计划

        Args:
            current_date: 当前日期
            disease_result: 病害结果
            weather_data: 天气数据

        Returns:
            管理计划
        """
        prompt = f"""根据当前病害情况，制定未来2-4周的阶段性管理计划：

当前日期：{current_date.strftime('%Y年%m月%d日')}
病害情况：{disease_result.get('disease_name', '未知')}

请制定：
1. 第一周：紧急防治阶段
2. 第二周：巩固治疗阶段
3. 第三周：恢复管理阶段
4. 第四周：预防监控阶段

每个阶段包括主要任务、注意事项和预期效果。"""

        system_prompt = "你是一个农业管理专家，请制定科学、可行的阶段性管理计划。"

        response = await self._call_llm(system_prompt, prompt)

        return {
            "plan": response,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": (current_date + timedelta(weeks=4)).strftime("%Y-%m-%d")
        }
