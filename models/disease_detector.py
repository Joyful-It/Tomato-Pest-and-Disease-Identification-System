"""
文件名: disease_detector.py
功能描述: 病虫害识别模型 — 已接入 ResNet50 (PlantVillage 38类)
作者: ZT
日期: 2026/6/16
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from PIL import Image
import numpy as np


# 英文标签 → 中文标签映射
LABEL_ZH_MAP = {
    "Apple___Apple_scab": "苹果-黑星病",
    "Apple___Black_rot": "苹果-黑腐病",
    "Apple___Cedar_apple_rust": "苹果-锈病",
    "Apple___healthy": "苹果-健康",
    "Blueberry___healthy": "蓝莓-健康",
    "Cherry_(including_sour)___Powdery_mildew": "樱桃-白粉病",
    "Cherry_(including_sour)___healthy": "樱桃-健康",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "玉米-灰斑病",
    "Corn_(maize)___Common_rust_": "玉米-锈病",
    "Corn_(maize)___Northern_Leaf_Blight": "玉米-大斑病",
    "Corn_(maize)___healthy": "玉米-健康",
    "Grape___Black_rot": "葡萄-黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄-黑麻疹病",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄-叶斑病",
    "Grape___healthy": "葡萄-健康",
    "Orange___Haunglongbing_(Citrus_greening)": "橙子-黄龙病",
    "Peach___Bacterial_spot": "桃子-细菌性斑点病",
    "Peach___healthy": "桃子-健康",
    "Pepper,_bell___Bacterial_spot": "辣椒-细菌性斑点病",
    "Pepper,_bell___healthy": "辣椒-健康",
    "Potato___Early_blight": "马铃薯-早疫病",
    "Potato___Late_blight": "马铃薯-晚疫病",
    "Potato___healthy": "马铃薯-健康",
    "Raspberry___healthy": "树莓-健康",
    "Soybean___healthy": "大豆-健康",
    "Squash___Powdery_mildew": "南瓜-白粉病",
    "Strawberry___Leaf_scorch": "草莓-叶焦病",
    "Strawberry___healthy": "草莓-健康",
    "Tomato___Bacterial_spot": "番茄-细菌性斑点病",
    "Tomato___Early_blight": "番茄-早疫病",
    "Tomato___Late_blight": "番茄-晚疫病",
    "Tomato___Leaf_Mold": "番茄-叶霉病",
    "Tomato___Septoria_leaf_spot": "番茄-斑枯病",
    "Tomato___Spider_mites Two-spotted_spider_mite": "番茄-红蜘蛛",
    "Tomato___Target_Spot": "番茄-靶斑病",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄-黄化曲叶病毒病",
    "Tomato___Tomato_mosaic_virus": "番茄-花叶病毒病",
    "Tomato___healthy": "番茄-健康",
}


class DiseaseDetector:
    """
    病虫害识别器
    使用 ResNet50 在 PlantVillage 上训练的模型进行推理
    """

    def __init__(self, model_path: str = None):
        """
        初始化病虫害识别器

        Args:
            model_path: 模型路径，默认读取环境变量 MODEL_PATH
        """
        self.model = None
        self.processor = None

        # 决定模型路径
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "models/resnet50_plant")

        self._load_model(model_path)

    def _load_model(self, model_path: str):
        """
        加载模型

        Args:
            model_path: 模型目录路径
        """
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification

            if os.path.exists(model_path):
                print(f"[DiseaseDetector] 从本地加载模型: {model_path}")
                self.processor = AutoImageProcessor.from_pretrained(model_path)
                self.model = AutoModelForImageClassification.from_pretrained(model_path)
            else:
                print(f"[DiseaseDetector] 本地模型不存在 ({model_path})，尝试从 HuggingFace 加载...")
                self.processor = AutoImageProcessor.from_pretrained(
                    "SanketJadhav/PlantDiseaseClassifier-Resnet50"
                )
                self.model = AutoModelForImageClassification.from_pretrained(
                    "SanketJadhav/PlantDiseaseClassifier-Resnet50"
                )

            # 构建 id → 中文标签映射
            en_id2label = self.model.config.id2label
            self.id2label = {}
            for idx, en_name in en_id2label.items():
                self.id2label[idx] = LABEL_ZH_MAP.get(en_name, en_name)

            print(f"[DiseaseDetector] 模型加载成功，支持 {len(self.id2label)} 个类别")

        except ImportError:
            print("[DiseaseDetector] transformers 未安装，使用模拟模式")
        except Exception as e:
            print(f"[DiseaseDetector] 模型加载失败: {e}，使用模拟模式")

    async def detect(
        self,
        image_path: str,
        image_features: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        识别病虫害

        Args:
            image_path: 图像路径
            image_features: 图像特征（可选，模型加载后不使用）

        Returns:
            识别结果
        """
        if self.model is not None and self.processor is not None:
            return await self._model_detect(image_path)
        else:
            return self._mock_detect(image_path, image_features)

    async def _model_detect(self, image_path: str) -> Dict[str, Any]:
        """
        使用真实模型推理

        Args:
            image_path: 图像路径

        Returns:
            识别结果
        """
        import torch

        try:
            # 加载图片
            image = Image.open(image_path).convert("RGB")

            # 预处理
            inputs = self.processor(images=image, return_tensors="pt")

            # 推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # 取 Top 5
            top5_probs, top5_indices = torch.topk(probs[0], k=5)

            predictions = []
            for prob, idx in zip(top5_probs, top5_indices):
                idx_val = idx.item()
                predictions.append({
                    "label": self.id2label.get(idx_val, f"类别{idx_val}"),
                    "confidence": round(prob.item() * 100, 2),
                })

            # 取最高置信度结果
            top_idx = top5_indices[0].item()
            top_conf = round(top5_probs[0].item() * 100, 2)
            disease_name = self.id2label.get(top_idx, f"类别{top_idx}")

            # 判断是否健康
            is_healthy = "健康" in disease_name

            # 提取植物名和病害名
            if "-" in disease_name:
                plant, disease = disease_name.split("-", 1)
            else:
                plant, disease = disease_name, ""

            return {
                "success": True,
                "disease_name": disease_name,
                "plant": plant,
                "disease": disease,
                "confidence": top_conf,
                "top5_predictions": predictions,
                "is_healthy": is_healthy,
                "source": "resnet50",
                "model": "SanketJadhav/PlantDiseaseClassifier-Resnet50",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"模型推理失败: {str(e)}",
            }

    def _mock_detect(
        self,
        image_path: str,
        image_features: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        模拟检测（模型未加载时的后备方案）

        Args:
            image_path: 图像路径
            image_features: 图像特征

        Returns:
            模拟结果
        """
        if image_features:
            avg_color = image_features.get("average_color", {})
            r, g, b = avg_color.get("r", 0), avg_color.get("g", 0), avg_color.get("b", 0)
            if g > 150 and r < 100 and b < 100:
                return {
                    "success": True,
                    "disease_name": "番茄-健康",
                    "confidence": 75.0,
                    "is_healthy": True,
                    "source": "mock",
                }
            elif r > 150 and g < 100:
                return {
                    "success": True,
                    "disease_name": "番茄-早疫病",
                    "confidence": 60.0,
                    "is_healthy": False,
                    "source": "mock",
                }

        return {
            "success": True,
            "disease_name": "番茄-健康",
            "confidence": 50.0,
            "is_healthy": True,
            "source": "mock",
        }

    def get_supported_diseases(self) -> List[str]:
        """获取支持的病害列表（番茄）"""
        tomato_diseases = [
            "番茄-细菌性斑点病", "番茄-早疫病", "番茄-晚疫病",
            "番茄-叶霉病", "番茄-斑枯病", "番茄-红蜘蛛",
            "番茄-靶斑病", "番茄-黄化曲叶病毒病", "番茄-花叶病毒病",
            "番茄-健康",
        ]
        return tomato_diseases

    def get_all_labels(self) -> Dict[int, str]:
        """获取所有 38 类标签"""
        return self.id2label if self.id2label else LABEL_ZH_MAP

    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
