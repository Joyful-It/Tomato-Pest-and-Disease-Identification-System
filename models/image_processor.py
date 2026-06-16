"""
文件名: image_processor.py
功能描述: 图像处理模块，负责图像预处理和特征提取
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import io


class ImageProcessor:
    """
    图像处理器
    负责图像预处理、特征提取和格式转换
    """

    def __init__(self):
        """初始化图像处理器"""
        self.supported_formats = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        self.max_size = (1024, 1024)  # 最大处理尺寸

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        处理图像

        Args:
            image_path: 图像文件路径

        Returns:
            处理结果字典
        """
        try:
            # 验证文件
            path = Path(image_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": "图像文件不存在"
                }

            if path.suffix.lower() not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"不支持的图像格式，支持的格式：{', '.join(self.supported_formats)}"
                }

            # 打开图像
            image = Image.open(image_path)

            # 获取图像信息
            image_info = self._get_image_info(image, path)

            # 预处理图像
            processed_image = self._preprocess_image(image)

            # 提取特征描述
            features = self._extract_features(processed_image)

            return {
                "success": True,
                "image_info": image_info,
                "features": features,
                "processed_image": processed_image
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"图像处理失败：{str(e)}"
            }

    def _get_image_info(self, image: Image.Image, path: Path) -> Dict[str, Any]:
        """
        获取图像基本信息

        Args:
            image: PIL 图像对象
            path: 文件路径

        Returns:
            图像信息字典
        """
        return {
            "filename": path.name,
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "file_size": path.stat().st_size,
            "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2)
        }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        预处理图像

        Args:
            image: 原始图像

        Returns:
            处理后的图像
        """
        # 转换为 RGB 模式
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 调整大小
        if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
            image.thumbnail(self.max_size, Image.Resampling.LANCZOS)

        return image

    def _extract_features(self, image: Image.Image) -> Dict[str, Any]:
        """
        提取图像特征（基础版本）

        Args:
            image: 预处理后的图像

        Returns:
            特征字典
        """
        # 获取图像统计信息
        pixels = list(image.getdata())

        # 计算平均颜色
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)

        # 计算颜色分布
        r_distribution = self._calculate_distribution([p[0] for p in pixels])
        g_distribution = self._calculate_distribution([p[1] for p in pixels])
        b_distribution = self._calculate_distribution([p[2] for p in pixels])

        return {
            "average_color": {
                "r": round(avg_r, 2),
                "g": round(avg_g, 2),
                "b": round(avg_b, 2)
            },
            "color_distribution": {
                "r": r_distribution,
                "g": g_distribution,
                "b": b_distribution
            },
            "brightness": round((avg_r + avg_g + avg_b) / 3, 2),
            "colorfulness": self._calculate_colorfulness(avg_r, avg_g, avg_b)
        }

    def _calculate_distribution(self, values: list) -> Dict[str, float]:
        """
        计算值分布

        Args:
            values: 数值列表

        Returns:
            分布字典
        """
        # 将 0-255 分为 4 个区间
        bins = [0, 64, 128, 192, 256]
        distribution = {"low": 0, "medium_low": 0, "medium_high": 0, "high": 0}

        for value in values:
            if value < 64:
                distribution["low"] += 1
            elif value < 128:
                distribution["medium_low"] += 1
            elif value < 192:
                distribution["medium_high"] += 1
            else:
                distribution["high"] += 1

        # 转换为百分比
        total = len(values)
        return {k: round(v / total * 100, 2) for k, v in distribution.items()}

    def _calculate_colorfulness(self, r: float, g: float, b: float) -> str:
        """
        计算色彩丰富度

        Args:
            r: 红色平均值
            g: 绿色平均值
            b: 蓝色平均值

        Returns:
            色彩丰富度描述
        """
        # 简单的色彩丰富度计算
        diff_rg = abs(r - g)
        diff_rb = abs(r - b)
        diff_gb = abs(g - b)

        avg_diff = (diff_rg + diff_rb + diff_gb) / 3

        if avg_diff < 20:
            return "低"
        elif avg_diff < 50:
            return "中"
        else:
            return "高"

    async def image_to_base64(self, image_path: str) -> Optional[str]:
        """
        将图像转换为 base64

        Args:
            image_path: 图像路径

        Returns:
            base64 字符串
        """
        try:
            import base64

            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode("utf-8")
                return base64_data

        except Exception:
            return None

    def get_image_description(self, features: Dict[str, Any]) -> str:
        """
        根据特征生成图像描述

        Args:
            features: 图像特征

        Returns:
            图像描述文本
        """
        avg_color = features.get("average_color", {})
        brightness = features.get("brightness", 0)
        colorfulness = features.get("colorfulness", "中")

        # 根据颜色判断可能的植物状态
        r, g, b = avg_color.get("r", 0), avg_color.get("g", 0), avg_color.get("b", 0)

        description_parts = []

        # 亮度描述
        if brightness < 80:
            description_parts.append("图像较暗")
        elif brightness > 180:
            description_parts.append("图像较亮")
        else:
            description_parts.append("图像亮度适中")

        # 颜色分析
        if g > r and g > b:
            description_parts.append("以绿色为主，可能是健康叶片")
        elif r > g and r > b:
            description_parts.append("以红色为主，可能是成熟果实或病害")
        elif b > r and b > g:
            description_parts.append("以蓝色为主，可能是背景或阴影")
        elif r > 150 and g > 150 and b < 100:
            description_parts.append("黄色调，可能是叶片黄化或成熟")

        # 色彩丰富度
        description_parts.append(f"色彩丰富度：{colorfulness}")

        return "，".join(description_parts)
