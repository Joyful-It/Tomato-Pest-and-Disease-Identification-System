"""
文件名: soil_agent.py
功能描述: 土壤分析 Agent，负责土壤状况分析和改良建议
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from services.soil_service import SoilService


class SoilAgent(BaseAgent):
    """
    土壤分析 Agent
    负责分析土壤状况，提供土壤改良建议
    """

    def __init__(self, llm_service):
        """
        初始化土壤分析 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        self.soil_service = SoilService()

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析土壤状况

        Args:
            context: 包含位置信息的上下文

        Returns:
            土壤分析结果
        """
        # 获取位置信息
        latitude = context.get("latitude", 0)
        longitude = context.get("longitude", 0)
        location = context.get("location", "")
        disease_result = context.get("disease_result", {})

        # 获取土壤数据
        soil_data = await self.soil_service.analyze_soil(
            latitude, longitude, location
        )

        if not soil_data.get("success"):
            return {
                "success": False,
                "error": soil_data.get("error", "土壤分析失败")
            }

        # 分析土壤与病害的关系
        disease_relation = await self._analyze_soil_disease_relation(
            soil_data, disease_result
        )

        # 生成土壤改良建议
        improvement_advice = await self._generate_improvement_advice(
            soil_data, disease_result, disease_relation
        )

        return {
            "success": True,
            "soil_data": soil_data.get("soil_data", {}),
            "analysis": soil_data.get("analysis", {}),
            "basic_advice": soil_data.get("advice", []),
            "disease_relation": disease_relation,
            "improvement_advice": improvement_advice
        }

    async def _analyze_soil_disease_relation(
        self,
        soil_data: Dict,
        disease_result: Dict
    ) -> str:
        """
        分析土壤与病害的关系

        Args:
            soil_data: 土壤数据
            disease_result: 病虫害结果

        Returns:
            关系分析
        """
        soil_info = soil_data.get("soil_data", {})
        analysis = soil_data.get("analysis", {})

        prompt = f"""分析土壤状况与番茄病害的关系：

土壤数据：
- pH值：{soil_info.get('ph', '未知')}（状态：{analysis.get('ph_status', '未知')}）
- 有机质：{soil_info.get('organic_matter', '未知')}%（状态：{analysis.get('organic_status', '未知')}）
- 氮素：{soil_info.get('nitrogen', '未知')} mg/kg
- 磷素：{soil_info.get('phosphorus', '未知')} mg/kg
- 钾素：{soil_info.get('potassium', '未知')} mg/kg
- 质地：{soil_info.get('texture', '未知')}
- 排水性：{soil_info.get('drainage', '未知')}

病害信息：
- 病害：{disease_result.get('disease_name', '未知')}

请分析：
1. 当前土壤状况是否可能诱发或加重该病害？
2. 土壤中哪些因素与病害相关？
3. 如何通过土壤改良来预防病害？"""

        system_prompt = "你是一个土壤学专家，请分析土壤状况与植物病害的关系。"

        return await self._call_llm(system_prompt, prompt)

    async def _generate_improvement_advice(
        self,
        soil_data: Dict,
        disease_result: Dict,
        disease_relation: str
    ) -> str:
        """
        生成土壤改良建议

        Args:
            soil_data: 土壤数据
            disease_result: 病害结果
            disease_relation: 病害关系分析

        Returns:
            改良建议
        """
        prompt = f"""根据土壤分析和病害关系，提供具体的土壤改良建议：

土壤分析：{soil_data.get('analysis', {})}
病害关系分析：{disease_relation}

请提供：
1. 短期改良措施（立即可以做的）
2. 长期改良方案
3. 推荐的土壤改良剂
4. 注意事项"""

        system_prompt = "你是一个土壤改良专家，请提供实用、经济的土壤改良方案。"

        return await self._call_llm(system_prompt, prompt)