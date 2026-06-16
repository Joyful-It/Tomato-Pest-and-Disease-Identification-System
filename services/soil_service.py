"""
文件名: soil_service.py
功能描述: 土壤服务封装，提供土壤分析功能（基于区域土壤库预留）
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, Dict, Any


class SoilService:
    """
    土壤服务类
    基于区域位置提供土壤分析（预留接口）
    """

    def __init__(self):
        """初始化土壤服务"""
        # 预留：加载区域土壤数据库
        self.soil_database = self._load_soil_database()

    def _load_soil_database(self) -> Dict[str, Any]:
        """
        加载土壤数据库（预留接口）

        Returns:
            土壤数据库字典
        """
        # 模拟数据，实际应该从数据库或文件加载
        return {
            "default": {
                "ph": 6.5,
                "organic_matter": 2.5,
                "nitrogen": 120,
                "phosphorus": 15,
                "potassium": 150,
                "texture": "壤土",
                "drainage": "良好",
                "fertility": "中等"
            }
        }

    async def analyze_soil(
        self,
        latitude: float,
        longitude: float,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析土壤情况

        Args:
            latitude: 纬度
            longitude: 经度
            location: 位置描述

        Returns:
            土壤分析结果
        """
        # 根据位置获取土壤数据
        soil_data = self._get_soil_by_location(latitude, longitude, location)

        # 分析土壤状况
        analysis = self._analyze_soil_data(soil_data)

        # 生成建议
        advice = self._generate_soil_advice(analysis)

        return {
            "success": True,
            "soil_data": soil_data,
            "analysis": analysis,
            "advice": advice,
            "source": "database"
        }

    def _get_soil_by_location(
        self,
        latitude: float,
        longitude: float,
        location: Optional[str]
    ) -> Dict[str, Any]:
        """
        根据位置获取土壤数据

        Args:
            latitude: 纬度
            longitude: 经度
            location: 位置描述

        Returns:
            土壤数据
        """
        # 这里应该根据实际位置查询数据库
        # 目前返回默认数据
        return self.soil_database.get("default", {
            "ph": 6.5,
            "organic_matter": 2.5,
            "nitrogen": 120,
            "phosphorus": 15,
            "potassium": 150,
            "texture": "壤土",
            "drainage": "良好",
            "fertility": "中等"
        })

    def _analyze_soil_data(self, soil_data: Dict) -> Dict[str, Any]:
        """
        分析土壤数据

        Args:
            soil_data: 土壤数据

        Returns:
            分析结果
        """
        ph = soil_data.get("ph", 7.0)
        organic_matter = soil_data.get("organic_matter", 0)
        nitrogen = soil_data.get("nitrogen", 0)
        phosphorus = soil_data.get("phosphorus", 0)
        potassium = soil_data.get("potassium", 0)

        # pH 分析
        ph_status = "正常"
        if ph < 5.5:
            ph_status = "偏酸"
        elif ph > 7.5:
            ph_status = "偏碱"

        # 有机质分析
        organic_status = "正常"
        if organic_matter < 1.5:
            organic_status = "偏低"
        elif organic_matter > 3.5:
            organic_status = "丰富"

        # 氮磷钾分析
        npk_status = {
            "nitrogen": "正常" if 100 <= nitrogen <= 150 else ("偏低" if nitrogen < 100 else "偏高"),
            "phosphorus": "正常" if 10 <= phosphorus <= 20 else ("偏低" if phosphorus < 10 else "偏高"),
            "potassium": "正常" if 120 <= potassium <= 180 else ("偏低" if potassium < 120 else "偏高")
        }

        return {
            "ph_status": ph_status,
            "organic_status": organic_status,
            "npk_status": npk_status,
            "overall_fertility": "良好" if ph_status == "正常" and organic_status != "偏低" else "需要改良"
        }

    def _generate_soil_advice(self, analysis: Dict) -> list:
        """
        生成土壤改良建议

        Args:
            analysis: 分析结果

        Returns:
            建议列表
        """
        advice = []

        # pH 建议
        if analysis["ph_status"] == "偏酸":
            advice.append("土壤偏酸，建议施用石灰或草木灰调节 pH 值")
        elif analysis["ph_status"] == "偏碱":
            advice.append("土壤偏碱，建议施用硫磺粉或酸性肥料调节 pH 值")

        # 有机质建议
        if analysis["organic_status"] == "偏低":
            advice.append("有机质含量偏低，建议增施有机肥或秸秆还田")

        # 氮磷钾建议
        npk = analysis["npk_status"]
        if npk["nitrogen"] == "偏低":
            advice.append("氮素不足，建议追施尿素或复合肥")
        if npk["phosphorus"] == "偏低":
            advice.append("磷素不足，建议施用过磷酸钙或磷酸二铵")
        if npk["potassium"] == "偏低":
            advice.append("钾素不足，建议施用硫酸钾或氯化钾")

        if not advice:
            advice.append("土壤状况良好，继续保持当前管理方式")

        return advice
