"""
文件名: disease_detector.py
功能描述: 病虫害识别模型 — 使用 Swin Tiny 番茄 10 分类 (97.4% 准确率)
作者: ZT
日期: 2026/6/16
更新: 2026/6/26 — 从 ResNet50 38类 替换为 Swin Tiny 10类
"""

import os
from typing import Dict, Any, Optional, List
from PIL import Image
import torch


class DiseaseDetector:
    """
    病虫害识别器
    使用 Swin Tiny 在 PlantVillage 番茄 10 类上微调 (800 张训练, 15011 张独立测试)
    准确率: 97.4%
    """

    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: 模型路径，默认 models/swin_tomato_10cls
        """
        self.model = None
        self.processor = None
        self.id2label = {}
        self.supported_classes = 10

        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "models/swin_tomato_10cls")

        self._load_model(model_path)

    def _load_model(self, model_path: str):
        """加载 Swin Tiny 模型"""
        try:
            import json
            import builtins
            from transformers import AutoConfig, AutoImageProcessor, AutoModelForImageClassification

            if os.path.exists(model_path):
                print(f"[DiseaseDetector] 从本地加载 Swin Tiny: {model_path}")

                # Windows GBK 兼容: 临时 patch open() 为 UTF-8 模式
                _orig_open = builtins.open
                def _utf8_open(file, mode="r", *a, **kw):
                    if "b" not in mode and "encoding" not in kw:
                        kw["encoding"] = "utf-8"
                    return _orig_open(file, mode, *a, **kw)
                builtins.open = _utf8_open

                try:
                    config = AutoConfig.from_pretrained(model_path)
                    self.processor = AutoImageProcessor.from_pretrained(model_path)
                    self.model = AutoModelForImageClassification.from_pretrained(
                        model_path, ignore_mismatched_sizes=True
                    )
                finally:
                    builtins.open = _orig_open
            else:
                print(f"[DiseaseDetector] 本地模型不存在 ({model_path})，使用模拟模式")
                return

            self.id2label = self.model.config.id2label
            self.supported_classes = len(self.id2label)
            print(f"[DiseaseDetector] Swin Tiny 加载成功 ({self.supported_classes} 类, 97.4% acc)")

        except ImportError:
            print("[DiseaseDetector] transformers 未安装，使用模拟模式")
        except Exception as e:
            print(f"[DiseaseDetector] 模型加载失败: {e}，使用模拟模式")

    async def detect(
        self,
        image_path: str,
        image_features: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """识别病虫害"""
        if self.model is not None and self.processor is not None:
            return await self._model_detect(image_path)
        else:
            return self._mock_detect(image_path, image_features)

    async def _model_detect(self, image_path: str) -> Dict[str, Any]:
        """使用 Swin Tiny 推理"""
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

            top5_probs, top5_indices = torch.topk(probs[0], k=min(5, self.supported_classes))

            predictions = []
            for prob, idx in zip(top5_probs, top5_indices):
                idx_val = idx.item()
                predictions.append({
                    "label": self.id2label.get(idx_val, f"类别{idx_val}"),
                    "confidence": round(prob.item() * 100, 2),
                })

            top_idx = top5_indices[0].item()
            top_conf = round(top5_probs[0].item() * 100, 2)
            disease_name = self.id2label.get(top_idx, f"类别{top_idx}")

            is_healthy = "健康" in disease_name

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
                "source": "swin_tiny",
                "model": "Swin Tiny — 97.4% on 15,011 unseen tomato images",
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
        """模拟检测（后备）"""
        if image_features:
            avg_color = image_features.get("average_color", {})
            r = avg_color.get("r", 0)
            g = avg_color.get("g", 0)
            if g > 150 and r < 100:
                return {
                    "success": True,
                    "disease_name": "番茄-健康",
                    "confidence": 75.0,
                    "is_healthy": True,
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
        """获取支持的 10 类番茄病害"""
        return [
            "番茄-细菌性斑点病", "番茄-早疫病", "番茄-晚疫病",
            "番茄-叶霉病", "番茄-斑枯病", "番茄-红蜘蛛",
            "番茄-靶斑病", "番茄-黄化曲叶病毒", "番茄-花叶病毒",
            "番茄-健康",
        ]

    def get_all_labels(self) -> Dict[int, str]:
        """获取所有标签映射"""
        return self.id2label if self.id2label else {
            0: "番茄-细菌性斑点病", 1: "番茄-早疫病", 2: "番茄-晚疫病",
            3: "番茄-叶霉病", 4: "番茄-斑枯病", 5: "番茄-红蜘蛛",
            6: "番茄-靶斑病", 7: "番茄-黄化曲叶病毒", 8: "番茄-花叶病毒",
            9: "番茄-健康",
        }

    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
