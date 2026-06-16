"""
文件名: text_processor.py
功能描述: 文本处理模块，负责用户输入文本的解析和理解
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any, List
import re


class TextProcessor:
    """
    文本处理器
    负责解析用户输入的文本描述，提取关键信息
    """

    def __init__(self):
        """初始化文本处理器"""
        # 病虫害关键词库
        self.disease_keywords = {
            "早疫病": ["早疫病", "轮纹", "同心圆", "黑斑"],
            "晚疫病": ["晚疫病", "水渍", "腐烂", "褐色"],
            "叶霉病": ["叶霉病", "霉层", "灰色", "绒毛"],
            "灰霉病": ["灰霉病", "灰色", "霉变", "腐烂"],
            "枯萎病": ["枯萎病", "萎蔫", "枯死", "维管束"],
            "病毒病": ["病毒病", "花叶", "卷叶", "畸形"],
            "蚜虫": ["蚜虫", "小虫", "绿色", "密集群"],
            "白粉虱": ["白粉虱", "小白虫", "飞虫"],
            "红蜘蛛": ["红蜘蛛", "红点", "丝网"],
            "脐腐病": ["脐腐病", "底部", "腐烂", "黑色"]
        }

        # 症状关键词库
        self.symptom_keywords = {
            "叶片症状": ["黄叶", "枯叶", "斑点", "卷叶", "落叶", "变色", "萎蔫"],
            "果实症状": ["腐烂", "畸形", "裂果", "变色", "斑点", "软化"],
            "茎秆症状": ["枯萎", "变色", "腐烂", "开裂", "流胶"],
            "根部症状": ["腐烂", "变色", "根结", "根肿"]
        }

        # 严重程度关键词
        self.severity_keywords = {
            "轻微": ["轻微", "少量", "刚开始", "初期"],
            "中等": ["中等", "一些", "部分", "明显"],
            "严重": ["严重", "大量", "很多", "大面积", "快速扩散"]
        }

    async def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理用户输入的文本

        Args:
            text: 用户输入的文本

        Returns:
            处理结果字典
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "输入文本为空"
            }

        # 清洗文本
        cleaned_text = self._clean_text(text)

        # 提取关键信息
        diseases = self._extract_diseases(cleaned_text)
        symptoms = self._extract_symptoms(cleaned_text)
        severity = self._extract_severity(cleaned_text)
        location_info = self._extract_location_info(cleaned_text)

        # 生成文本分析
        analysis = self._analyze_text(cleaned_text, diseases, symptoms, severity)

        return {
            "success": True,
            "original_text": text,
            "cleaned_text": cleaned_text,
            "diseases": diseases,
            "symptoms": symptoms,
            "severity": severity,
            "location_info": location_info,
            "analysis": analysis
        }

    def _clean_text(self, text: str) -> str:
        """
        清洗文本

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text.strip())

        # 去除特殊字符（保留中文、英文、数字、常用标点）
        text = re.sub(r'[^一-龥a-zA-Z0-9，。！？、；：""''（）\-]', '', text)

        return text

    def _extract_diseases(self, text: str) -> List[Dict[str, Any]]:
        """
        提取病虫害信息

        Args:
            text: 文本

        Returns:
            病虫害列表
        """
        found_diseases = []

        for disease_name, keywords in self.disease_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_diseases.append({
                        "name": disease_name,
                        "matched_keyword": keyword,
                        "confidence": 0.8  # 基于关键词匹配置信度
                    })
                    break

        return found_diseases

    def _extract_symptoms(self, text: str) -> Dict[str, List[str]]:
        """
        提取症状信息

        Args:
            text: 文本

        Returns:
            症状分类字典
        """
        found_symptoms = {}

        for category, keywords in self.symptom_keywords.items():
            category_symptoms = []
            for keyword in keywords:
                if keyword in text:
                    category_symptoms.append(keyword)

            if category_symptoms:
                found_symptoms[category] = category_symptoms

        return found_symptoms

    def _extract_severity(self, text: str) -> str:
        """
        提取严重程度

        Args:
            text: 文本

        Returns:
            严重程度描述
        """
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return severity

        return "未知"

    def _extract_location_info(self, text: str) -> Dict[str, Any]:
        """
        提取位置相关信息

        Args:
            text: 文本

        Returns:
            位置信息
        """
        # 提取可能的位置描述
        location_patterns = [
            r'在(.{2,10})地区',
            r'在(.{2,10})省',
            r'在(.{2,10})市',
            r'在(.{2,10})县',
            r'在(.{2,10})村'
        ]

        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)

        return {
            "mentioned_locations": locations,
            "has_location_info": len(locations) > 0
        }

    def _analyze_text(
        self,
        text: str,
        diseases: List[Dict],
        symptoms: Dict[str, List[str]],
        severity: str
    ) -> Dict[str, Any]:
        """
        分析文本内容

        Args:
            text: 文本
            diseases: 病虫害列表
            symptoms: 症状字典
            severity: 严重程度

        Returns:
            分析结果
        """
        # 计算文本长度
        text_length = len(text)

        # 判断是否包含疑问
        has_question = "？" in text or "?" in text

        # 判断是否包含时间信息
        time_keywords = ["天", "周", "月", "最近", "昨天", "今天", "前几天"]
        has_time_info = any(keyword in text for keyword in time_keywords)

        # 生成分析摘要
        summary_parts = []

        if diseases:
            disease_names = [d["name"] for d in diseases]
            summary_parts.append(f"提到了病虫害：{'、'.join(disease_names)}")

        if symptoms:
            symptom_count = sum(len(v) for v in symptoms.values())
            summary_parts.append(f"描述了{symptom_count}个症状")

        if severity != "未知":
            summary_parts.append(f"严重程度：{severity}")

        if has_time_info:
            summary_parts.append("包含了时间信息")

        if has_question:
            summary_parts.append("包含疑问，需要解答")

        return {
            "text_length": text_length,
            "has_question": has_question,
            "has_time_info": has_time_info,
            "summary": "；".join(summary_parts) if summary_parts else "文本描述较简单"
        }

    def generate_text_summary(self, processed_result: Dict[str, Any]) -> str:
        """
        生成文本摘要

        Args:
            processed_result: 处理结果

        Returns:
            文本摘要
        """
        if not processed_result.get("success"):
            return "文本处理失败"

        parts = []

        # 病虫害信息
        diseases = processed_result.get("diseases", [])
        if diseases:
            disease_names = [d["name"] for d in diseases]
            parts.append(f"病虫害：{'、'.join(disease_names)}")

        # 症状信息
        symptoms = processed_result.get("symptoms", {})
        if symptoms:
            all_symptoms = []
            for category_symptoms in symptoms.values():
                all_symptoms.extend(category_symptoms)
            parts.append(f"症状：{'、'.join(all_symptoms)}")

        # 严重程度
        severity = processed_result.get("severity", "未知")
        if severity != "未知":
            parts.append(f"严重程度：{severity}")

        # 位置信息
        location_info = processed_result.get("location_info", {})
        if location_info.get("has_location_info"):
            locations = location_info.get("mentioned_locations", [])
            parts.append(f"位置：{'、'.join(locations)}")

        return "；".join(parts) if parts else "未提取到关键信息"
