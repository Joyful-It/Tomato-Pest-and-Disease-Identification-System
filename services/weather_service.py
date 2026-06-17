"""
文件名: weather_service.py
功能描述: 天气服务封装，提供天气查询功能（彩云天气 API）
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, Dict, Any
import httpx


class WeatherService:
    """
    天气服务类
    封装彩云天气 API 调用
    """

    def __init__(self):
        """初始化天气服务"""
        self.api_key = "bpxwpKFicBRp71m6"
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
        try:
            url = f"{self.base_url}/{self.api_key}/{longitude},{latitude}/weather"
            params = {
                "dailysteps": 3,
                "hourlysteps": 48
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
        hourly = result.get("hourly", {})
        temperature = daily.get("temperature", [])
        humidity = daily.get("humidity", [])
        skycon = daily.get("skycon", [])
        precipitation = daily.get("precipitation", [])

        # 获取今天的天气
        today_temp = temperature[0] if temperature else {}
        today_humidity = humidity[0] if humidity else {}
        today_skycon = skycon[0] if skycon else {}
        today_precip = precipitation[0] if precipitation else {}

        # 获取小时级数据
        hourly_data = self._parse_hourly(hourly)

        return {
            "success": True,
            "today": {
                "date": today_temp.get("date", ""),
                "temperature": {
                    "max": today_temp.get("max", 0),
                    "min": today_temp.get("min", 0),
                    "avg": today_temp.get("avg", 0)
                },
                "humidity": {
                    "avg": today_humidity.get("avg", 0)
                },
                "skycon": today_skycon.get("value", ""),
                "description": self._get_skycon_description(today_skycon.get("value", "")),
                "precipitation": {
                    "avg": today_precip.get("avg", 0)
                }
            },
            "forecast": self._parse_forecast(daily),
            "hourly": hourly_data,
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
        humidity = daily.get("humidity", [])
        precipitation = daily.get("precipitation", [])

        for i in range(min(3, len(temperature))):
            temp = temperature[i] if i < len(temperature) else {}
            sky = skycon[i] if i < len(skycon) else {}
            hum = humidity[i] if i < len(humidity) else {}
            precip = precipitation[i] if i < len(precipitation) else {}

            forecast.append({
                "day": i + 1,
                "date": temp.get("date", ""),
                "temperature": {
                    "max": temp.get("max", 0),
                    "min": temp.get("min", 0)
                },
                "skycon": sky.get("value", ""),
                "description": self._get_skycon_description(sky.get("value", "")),
                "humidity": hum.get("avg", 0),
                "precipitation": precip.get("avg", 0)
            })

        return forecast

    def _parse_hourly(self, hourly: Dict) -> list:
        """
        解析小时级数据

        Args:
            hourly: 小时级天气数据

        Returns:
            小时级数据列表
        """
        result = []
        temperature = hourly.get("temperature", [])
        humidity = hourly.get("humidity", [])
        skycon = hourly.get("skycon", [])
        precipitation = hourly.get("precipitation", [])

        # 只取未来 24 小时
        for i in range(min(24, len(temperature))):
            temp = temperature[i] if i < len(temperature) else {}
            hum = humidity[i] if i < len(humidity) else {}
            sky = skycon[i] if i < len(skycon) else {}
            precip = precipitation[i] if i < len(precipitation) else {}

            result.append({
                "time": temp.get("datetime", ""),
                "temperature": temp.get("value", 0),
                "humidity": hum.get("value", 0),
                "skycon": sky.get("value", ""),
                "description": self._get_skycon_description(sky.get("value", "")),
                "precipitation": precip.get("value", 0)
            })

        return result

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

    def _get_skycon_icon(self, skycon: str) -> str:
        """
        获取天气图标

        Args:
            skycon: 天气代码

        Returns:
            天气图标 class
        """
        icons = {
            "CLEAR_DAY": "bi bi-sun",
            "CLEAR_NIGHT": "bi bi-moon",
            "PARTLY_CLOUDY_DAY": "bi bi-cloud-sun",
            "PARTLY_CLOUDY_NIGHT": "bi bi-cloud-moon",
            "CLOUDY": "bi bi-cloud",
            "LIGHT_HAZE": "bi bi-cloud-haze",
            "MODERATE_HAZE": "bi bi-cloud-haze",
            "HEAVY_HAZE": "bi bi-cloud-haze",
            "LIGHT_RAIN": "bi bi-cloud-drizzle",
            "MODERATE_RAIN": "bi bi-cloud-rain",
            "HEAVY_RAIN": "bi bi-cloud-rain-heavy",
            "STORM_RAIN": "bi bi-cloud-lightning-rain",
            "FOG": "bi bi-cloud-fog",
            "LIGHT_SNOW": "bi bi-cloud-snow",
            "MODERATE_SNOW": "bi bi-cloud-snow",
            "HEAVY_SNOW": "bi bi-cloud-snow",
            "STORM_SNOW": "bi bi-cloud-snow",
            "WIND": "bi bi-wind"
        }
        return icons.get(skycon, "bi bi-cloud")