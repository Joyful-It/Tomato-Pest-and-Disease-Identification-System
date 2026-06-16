"""
文件名: location_service.py
功能描述: 定位服务封装，提供多种定位方式
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, Dict, Any
import httpx
from config import IP_LOCATION_API


class LocationService:
    """
    定位服务类
    提供 IP 定位和地址解析功能
    支持浏览器定位（前端实现）、IP 定位、用户手动输入三种方式
    """

    def __init__(self):
        """初始化定位服务"""
        self.ip_api = IP_LOCATION_API

    async def get_location_by_ip(self, ip: Optional[str] = None) -> Dict[str, Any]:
        """
        通过 IP 地址获取位置信息

        Args:
            ip: IP 地址，如果为 None 则使用客户端 IP

        Returns:
            位置信息字典
        """
        try:
            url = self.ip_api
            if ip:
                url = f"{self.ip_api}/{ip}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        return {
                            "success": True,
                            "location": f"{data.get('country', '')} {data.get('regionName', '')} {data.get('city', '')}",
                            "latitude": data.get("lat", 0.0),
                            "longitude": data.get("lon", 0.0),
                            "country": data.get("country", ""),
                            "region": data.get("regionName", ""),
                            "city": data.get("city", ""),
                            "source": "ip"
                        }

            return {
                "success": False,
                "error": "IP 定位失败",
                "source": "ip"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": "ip"
            }

    def parse_location_text(self, location_text: str) -> Dict[str, Any]:
        """
        解析用户手动输入的位置文本

        Args:
            location_text: 位置文本（如"北京市海淀区"）

        Returns:
            解析后的位置信息
        """
        # 简单的地址解析（实际应该用更复杂的地址解析库）
        location_text = location_text.strip()

        if not location_text:
            return {
                "success": False,
                "error": "位置信息为空"
            }

        # 尝试解析省市区
        parts = []
        if "省" in location_text:
            province = location_text.split("省")[0] + "省"
            remaining = location_text.split("省")[1]
            parts.append(province)

            if "市" in remaining:
                city = remaining.split("市")[0] + "市"
                remaining = remaining.split("市")[1]
                parts.append(city)

                if "区" in remaining or "县" in remaining:
                    district = remaining
                    parts.append(district)
            elif "区" in remaining or "县" in remaining:
                parts.append(remaining)
        elif "市" in location_text:
            city = location_text.split("市")[0] + "市"
            remaining = location_text.split("市")[1]
            parts.append(city)

            if "区" in remaining or "县" in remaining:
                parts.append(remaining)
        else:
            parts.append(location_text)

        return {
            "success": True,
            "location": "".join(parts),
            "province": parts[0] if len(parts) > 0 else "",
            "city": parts[1] if len(parts) > 1 else "",
            "district": parts[2] if len(parts) > 2 else "",
            "source": "manual"
        }

    async def get_location_from_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        根据经纬度获取位置信息（反向地理编码）

        Args:
            latitude: 纬度
            longitude: 经度

        Returns:
            位置信息
        """
        try:
            # 使用免费的反向地理编码 API
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "accept-language": "zh-CN"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    timeout=5.0,
                    headers={"User-Agent": "TomatoDiseaseApp/1.0"}
                )

                if response.status_code == 200:
                    data = response.json()
                    address = data.get("address", {})

                    return {
                        "success": True,
                        "location": data.get("display_name", ""),
                        "province": address.get("state", ""),
                        "city": address.get("city", ""),
                        "district": address.get("suburb", ""),
                        "latitude": latitude,
                        "longitude": longitude,
                        "source": "reverse_geocode"
                    }

            return {
                "success": False,
                "error": "反向地理编码失败",
                "latitude": latitude,
                "longitude": longitude,
                "source": "reverse_geocode"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latitude": latitude,
                "longitude": longitude,
                "source": "reverse_geocode"
            }

    async def resolve_location(
        self,
        browser_location: Optional[Dict] = None,
        manual_location: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        综合解析位置信息
        优先级：浏览器定位 > 用户手动输入 > IP 定位

        Args:
            browser_location: 浏览器定位结果（包含 latitude 和 longitude）
            manual_location: 用户手动输入的位置
            client_ip: 客户端 IP 地址

        Returns:
            最终的位置信息
        """
        # 1. 优先使用浏览器定位
        if browser_location and browser_location.get("latitude") and browser_location.get("longitude"):
            result = await self.get_location_from_coordinates(
                browser_location["latitude"],
                browser_location["longitude"]
            )
            if result["success"]:
                result["source"] = "browser"
                return result

        # 2. 其次使用用户手动输入
        if manual_location:
            result = self.parse_location_text(manual_location)
            if result["success"]:
                return result

        # 3. 最后使用 IP 定位
        if client_ip:
            result = await self.get_location_by_ip(client_ip)
            if result["success"]:
                return result

        # 所有方式都失败
        return {
            "success": False,
            "error": "无法获取位置信息，请手动输入",
            "source": "none"
        }