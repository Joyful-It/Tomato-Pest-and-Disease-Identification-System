"""
文件名: weather_service.py
功能描述: 天气服务封装，提供天气查询功能（彩云天气 API 预留）
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, Dict, Any
import httpx
from config import CAIYUN_API_KEY


class WeatherService:
    """
    天气服务类
    封装彩云天气 API 调用（预留接口）
    """

    def __init__(self):
        """初始化天气服务"""
        self.api_key = CAIYUN_API_KEY
        self.base_url = "https://api.caiyunapp.com/v2.6"

    async def get_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        获取天气信息

        Args:
            latitude: 纬度
            longitude: 经度

        Returns:
            天气信息字典
        """
        # 检查 API Key 是否配置
        if not self.api_key:
            return self._get_mock_weather(latitude, longitude)

        try:
            url = f"{self.base_url}/{self.api_key}/{longitude},{latitude}/weather"
            params = {
                "dailysteps": 7,
                "hourlysteps": 24
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return self._parse_weather_data(data)

            return {
                "success": False,
                "error": "天气查询失败"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_weather_data(self, data: Dict) -> Dict[str, Any]:
        """
        解析天气数据

        Args:
            data: 原始天气数据

        Returns:
            解析后的天气信息
        """
        result = data.get("result", {})
        daily = result.get("daily", {})
        temperature = daily.get("temperature", [])
        humidity = daily.get("humidity", [])
        skycon = daily.get("skycon", [])

        # 获取今天的天气
        today_temp = temperature[0] if temperature else {}
        today_humidity = humidity[0] if humidity else {}
        today_skycon = skycon[0] if skycon else {}

        return {
            "success": True,
            "today": {
                "temperature": {
                    "max": today_temp.get("max", 0),
                    "min": today_temp.get("min", 0),
                    "avg": today_temp.get("avg", 0)
                },
                "humidity": {
                    "avg": today_humidity.get("avg", 0)
                },
                "skycon": today_skycon.get("value", ""),
                "description": self._get_skycon_description(today_skycon.get("value", ""))
            },
            "forecast": self._parse_forecast(daily),
            "source": "caiyun"
        }

    def _parse_forecast(self, daily: Dict) -> list:
        """
        解析预报数据

        Args:
            daily: 每日天气数据

        Returns:
            预报列表
        """
        forecast = []
        temperature = daily.get("temperature", [])
        skycon = daily.get("skycon", [])

        for i in range(min(7, len(temperature))):
            temp = temperature[i] if i < len(temperature) else {}
            sky = skycon[i] if i < len(skycon) else {}

            forecast.append({
                "day": i + 1,
                "temperature": {
                    "max": temp.get("max", 0),
                    "min": temp.get("min", 0)
                },
                "skycon": sky.get("value", ""),
                "description": self._get_skycon_description(sky.get("value", ""))
            })

        return forecast

    def _get_skycon_description(self, skycon: str) -> str:
        """
        获取天气描述

        Args:
            skycon: 天气代码

        Returns:
            天气描述
        """
        descriptions = {
            "CLEAR_DAY": "晴天",
            "CLEAR_NIGHT": "晴夜",
            "PARTLY_CLOUDY_DAY": "多云",
            "PARTLY_CLOUDY_NIGHT": "多云",
            "CLOUDY": "阴天",
            "LIGHT_HAZE": "轻度雾霾",
            "MODERATE_HAZE": "中度雾霾",
            "HEAVY_HAZE": "重度雾霾",
            "LIGHT_RAIN": "小雨",
            "MODERATE_RAIN": "中雨",
            "HEAVY_RAIN": "大雨",
            "STORM_RAIN": "暴雨",
            "FOG": "雾",
            "LIGHT_SNOW": "小雪",
            "MODERATE_SNOW": "中雪",
            "HEAVY_SNOW": "大雪",
            "STORM_SNOW": "暴雪",
            "WIND": "大风"
        }
        return descriptions.get(skycon, "未知")

    def _get_mock_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        获取模拟天气数据（当 API Key 未配置时使用）

        Args:
            latitude: 纬度
            longitude: 经度

        Returns:
            模拟天气数据
        """
        return {
            "success": True,
            "today": {
                "temperature": {
                    "max": 28,
                    "min": 18,
                    "avg": 23
                },
                "humidity": {
                    "avg": 65
                },
                "skycon": "PARTLY_CLOUDY_DAY",
                "description": "多云"
            },
            "forecast": [
                {"day": i + 1, "temperature": {"max": 28 - i, "min": 18 - i}, "skycon": "PARTLY_CLOUDY_DAY", "description": "多云"}
                for i in range(7)
            ],
            "source": "mock",
            "note": "彩云天气 API Key 未配置，使用模拟数据"
        }