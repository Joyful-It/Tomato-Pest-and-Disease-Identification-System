"""
文件名: safety_agent.py
功能描述: 安全用药 Agent，负责农药使用建议和安全审核
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class SafetyAgent(BaseAgent):
    """
    安全用药 Agent
    负责农药使用建议和安全审核
    """

    def __init__(self, llm_service):
        """
        初始化安全用药 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        # 预留：农药数据库
        self.pesticide_database = None  # TODO: 接入农药数据库

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用药安全

        Args:
            context: 包含病害信息的上下文

        Returns:
            用药安全分析结果
        """
        # 获取相关信息
        disease_result = context.get("disease_result", {})
        disease_analysis = context.get("disease_analysis", {})
        weather_data = context.get("weather_data", {})

        # 查询推荐农药
        recommended_pesticides = await self._query_pesticides(disease_result)

        # 分析用药安全性
        safety_analysis = await self._analyze_safety(
            disease_result, recommended_pesticides, weather_data
        )

        # 生成用药建议
        medication_advice = await self._generate_medication_advice(
            disease_result, recommended_pesticides, safety_analysis
        )

        # 生成安全提醒
        safety_reminders = await self._generate_safety_reminders(
            recommended_pesticides, weather_data
        )

        return {
            "success": True,
            "recommended_pesticides": recommended_pesticides,
            "safety_analysis": safety_analysis,
            "medication_advice": medication_advice,
            "safety_reminders": safety_reminders
        }

    async def _query_pesticides(self, disease_result: Dict) -> List[Dict]:
        """
        查询推荐农药（预留数据库接口）

        Args:
            disease_result: 病虫害结果

        Returns:
            推荐农药列表
        """
        # TODO: 实现农药数据库查询
        # 目前返回模拟数据
        disease_name = disease_result.get("disease_name", "未知")

        # 模拟农药数据
        mock_pesticides = [
            {
                "name": "百菌清",
                "type": "杀菌剂",
                "dosage": "75%可湿性粉剂600-800倍液",
                "interval": "7-10天",
                "safety_period": "7天",
                "toxicity": "低毒",
                "target_diseases": ["早疫病", "晚疫病", "叶霉病"]
            },
            {
                "name": "多菌灵",
                "type": "杀菌剂",
                "dosage": "50%可湿性粉剂500-800倍液",
                "interval": "7-10天",
                "safety_period": "15天",
                "toxicity": "低毒",
                "target_diseases": ["枯萎病", "灰霉病"]
            },
            {
                "name": "吡虫啉",
                "type": "杀虫剂",
                "dosage": "10%可湿性粉剂2000-3000倍液",
                "interval": "10-15天",
                "safety_period": "7天",
                "toxicity": "低毒",
                "target_diseases": ["蚜虫", "白粉虱"]
            }
        ]

        # 根据病害筛选农药
        recommended = []
        for pesticide in mock_pesticides:
            for target in pesticide["target_diseases"]:
                if target in disease_name:
                    recommended.append(pesticide)
                    break

        # 如果没有匹配的，返回通用农药
        if not recommended:
            recommended = mock_pesticides[:2]

        return recommended

    async def _analyze_safety(
        self,
        disease_result: Dict,
        pesticides: List[Dict],
        weather_data: Dict
    ) -> str:
        """
        分析用药安全性

        Args:
            disease_result: 病害结果
            pesticides: 推荐农药
            weather_data: 天气数据

        Returns:
            安全性分析
        """
        pesticide_info = "\n".join([
            f"- {p['name']}（{p['type']}）：{p['dosage']}，安全间隔期{s['safety_period']}"
            for p in pesticides
        ])

        today_weather = weather_data.get("today", {})
        weather_desc = today_weather.get("description", "未知")

        prompt = f"""分析以下农药使用的安全性：

病害：{disease_result.get('disease_name', '未知')}

推荐农药：
{pesticide_info}

当前天气：{weather_desc}

请分析：
1. 这些农药是否适合当前病害？
2. 当前天气是否适合施药？
3. 是否有农药混用禁忌？
4. 安全注意事项"""

        system_prompt = "你是一个农药安全专家，请分析用药安全性，确保农产品安全。"

        return await self._call_llm(system_prompt, prompt)

    async def _generate_medication_advice(
        self,
        disease_result: Dict,
        pesticides: List[Dict],
        safety_analysis: str
    ) -> str:
        """
        生成用药建议

        Args:
            disease_result: 病害结果
            pesticides: 推荐农药
            safety_analysis: 安全性分析

        Returns:
            用药建议
        """
        prompt = f"""根据安全性分析，提供具体的用药建议：

病害：{disease_result.get('disease_name', '未知')}
安全性分析：{safety_analysis}

请提供：
1. 推荐的用药方案（优先使用低毒农药）
2. 施药时间和方法
3. 注意事项
4. 替代方案（如果不想使用化学农药）"""

        system_prompt = "你是一个植保技术员，请提供安全、有效的用药方案。"

        return await self._call_llm(system_prompt, prompt)

    async def _generate_safety_reminders(
        self,
        pesticides: List[Dict],
        weather_data: Dict
    ) -> List[str]:
        """
        生成安全提醒

        Args:
            pesticides: 推荐农药
            weather_data: 天气数据

        Returns:
            安全提醒列表
        """
        reminders = [
            "施药时请佩戴防护装备（口罩、手套、护目镜）",
            "避免在高温时段（11:00-15:00）施药",
            "施药后请彻底清洗双手和暴露部位",
            "农药应存放在儿童接触不到的地方",
            "严格遵守安全间隔期，确保农产品安全"
        ]

        # 根据天气添加特殊提醒
        today_weather = weather_data.get("today", {})
        if today_weather.get("description") in ["小雨", "中雨", "大雨"]:
            reminders.append("雨天不宜施药，药效会降低且易流失污染环境")

        if today_weather.get("temperature", {}).get("max", 0) > 35:
            reminders.append("高温天气避免施药，防止药害和中毒")

        return reminders