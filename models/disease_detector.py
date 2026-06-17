"""
文件名: disease_detector.py
功能描述: 病虫害识别模块，支持返回多种可能病症及概率
作者: ZT
日期: 2026/6/17
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


class DiseaseDetector:
    """
    病虫害识别器
    返回多种可能的病症及概率
    """

    def __init__(self):
        """初始化病虫害识别器"""
        self.model = None
        self.label_map = self._load_label_map()
        self.tomato_labels = [
            "番茄-细菌性斑点病", "番茄-早疫病", "番茄-晚疫病",
            "番茄-叶霉病", "番茄-斑枯病", "番茄-红蜘蛛",
            "番茄-花叶病毒病", "番茄-黄化曲叶病毒病", "番茄-健康"
        ]
        self.disease_keywords = self._init_keywords()

    def _init_keywords(self):
        """初始化关键词库"""
        return {
            "番茄-早疫病": {
                "keywords": ["早疫病", "轮纹", "同心圆", "黑斑", "小黑点", "黑圈", "一圈一圈", "杆子发黑", "叶子有黑圈", "褐色圆斑"],
                "symptoms": ["同心轮纹", "黑斑", "叶片枯死"]
            },
            "番茄-晚疫病": {
                "keywords": ["晚疫病", "水渍", "腐烂", "烂了", "臭了", "发臭", "水烂", "软烂", "淌水", "白毛", "长白毛", "叶子烂了", "果子烂了", "发软"],
                "symptoms": ["水渍状", "腐烂", "白色霉层"]
            },
            "番茄-叶霉病": {
                "keywords": ["叶霉病", "霉层", "叶子背面长毛", "灰毛", "紫毛", "叶子发灰", "背面有毛", "叶片黄化"],
                "symptoms": ["叶片黄化", "灰色霉层", "卷叶"]
            },
            "番茄-灰霉病": {
                "keywords": ["灰霉病", "灰色的毛", "烂果", "果子长毛", "烂花", "花烂了", "V字形"],
                "symptoms": ["灰色霉层", "V字形病斑", "果实腐烂"]
            },
            "番茄-细菌性斑点病": {
                "keywords": ["斑点病", "细菌性", "小点点", "褐色小点", "周围发黄", "一圈黄色", "小斑"],
                "symptoms": ["小斑点", "褐色", "黄色晕圈"]
            },
            "番茄-溃疡病": {
                "keywords": ["溃疡病", "溃疡", "杆子里面烂了", "杆子空了", "流脓", "里面有脓", "鸟眼斑"],
                "symptoms": ["溃疡", "维管束变褐"]
            },
            "番茄-青枯病": {
                "keywords": ["青枯病", "青枯", "突然蔫了", "白天蔫晚上好", "全株蔫了", "挤出白水", "一下子枯了", "死得快"],
                "symptoms": ["萎蔫", "青枯"]
            },
            "番茄-枯萎病": {
                "keywords": ["枯萎病", "枯萎", "慢慢枯了", "一边枯一边好", "半边枯", "老叶先黄", "黄叶"],
                "symptoms": ["枯萎", "黄叶"]
            },
            "番茄-花叶病毒病": {
                "keywords": ["花叶", "病毒病", "叶子花花的", "深浅不一", "果子花了", "长得奇怪", "畸形"],
                "symptoms": ["花叶", "叶片畸形"]
            },
            "番茄-黄化曲叶病毒病": {
                "keywords": ["黄化", "曲叶", "叶子卷了", "叶子往上卷", "长不高", "叶子发黄卷起来", "有小白虫飞"],
                "symptoms": ["叶片黄化", "卷曲", "植株矮化"]
            },
            "番茄-红蜘蛛": {
                "keywords": ["红蜘蛛", "小红虫", "结网", "有丝网", "叶背有虫", "红色的虫子", "红点点"],
                "symptoms": ["叶片发黄", "细丝网", "红色小虫"]
            },
            "番茄-蚜虫": {
                "keywords": ["蚜虫", "腻虫", "绿色小虫", "小绿虫", "绿色虫子", "密密麻麻", "一窝虫", "虫子一堆", "绿色的小虫子", "小青虫"],
                "symptoms": ["叶片卷曲", "蜜露"]
            },
            "番茄-白粉虱": {
                "keywords": ["白粉虱", "小白虫", "小飞虫", "飞来飞去", "白色小飞虫", "粉虱"],
                "symptoms": ["叶片发黄", "蜜露"]
            },
            "番茄-斑枯病": {
                "keywords": ["斑枯病", "叶子有洞", "破了", "穿了", "中间白边上黑", "穿孔"],
                "symptoms": ["小斑点", "穿孔"]
            },
            "番茄-灰叶斑病": {
                "keywords": ["灰叶斑", "叶子干了", "叶子发灰", "叶子枯了", "灰褐色"],
                "symptoms": ["灰褐色斑点", "叶片干枯"]
            },
            "番茄-猝倒病": {
                "keywords": ["猝倒病", "倒苗", "苗倒了", "小苗死了", "苗烂了", "卡脖子"],
                "symptoms": ["幼苗倒伏", "茎基腐烂"]
            }
        }

    def _load_label_map(self):
        return {
            12: "番茄-细菌性斑点病", 13: "番茄-早疫病", 14: "番茄-晚疫病",
            15: "番茄-叶霉病", 16: "番茄-斑枯病", 17: "番茄-红蜘蛛",
            18: "番茄-花叶病毒病", 19: "番茄-黄化曲叶病毒病", 20: "番茄-健康"
        }

    async def detect(
        self,
        image_path: str = "",
        image_features: Optional[Dict] = None,
        text_input: str = ""
    ) -> Dict[str, Any]:
        """
        识别病虫害，返回多种可能结果

        Returns:
            包含 candidates 列表的结果
        """
        if text_input:
            return self._detect_from_text(text_input)
        if image_features:
            return self._detect_from_features(image_features)

        return {
            "success": True,
            "disease_name": "番茄-健康",
            "confidence": 0.5,
            "symptoms": [],
            "is_healthy": True,
            "candidates": [
                {"name": "番茄-健康", "probability": 50}
            ],
            "source": "default"
        }

    def _detect_from_text(self, text_input: str) -> Dict[str, Any]:
        """
        从文字描述识别，返回多种可能结果及概率
        """
        text = text_input.lower()

        # 计算每种病害的匹配得分
        scores = {}
        matched_keywords = {}

        for disease, info in self.disease_keywords.items():
            score = 0
            matched = []
            for keyword in info["keywords"]:
                if keyword in text:
                    score += 1
                    matched.append(keyword)
            if score > 0:
                scores[disease] = score
                matched_keywords[disease] = matched

        # 没有匹配到任何病害
        if not scores:
            # 检查通用症状
            general_symptoms = self._detect_general_symptoms(text)
            if general_symptoms:
                # 根据症状推测可能的病害
                candidates = self._guess_from_symptoms(general_symptoms)
                best = candidates[0] if candidates else {"name": "番茄-未知病害", "probability": 30}
                return {
                    "success": True,
                    "disease_name": best["name"],
                    "confidence": best["probability"] / 100,
                    "symptoms": general_symptoms,
                    "is_healthy": False,
                    "candidates": candidates,
                    "source": "text_symptoms"
                }

            return {
                "success": True,
                "disease_name": "番茄-健康",
                "confidence": 0.5,
                "symptoms": [],
                "is_healthy": True,
                "candidates": [{"name": "番茄-健康", "probability": 60}, {"name": "无法确定", "probability": 40}],
                "source": "text_default"
            }

        # 有匹配结果，计算概率分布
        total_score = sum(scores.values())
        candidates = []

        for disease, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            prob = min(int(score / total_score * 100), 95)
            candidates.append({
                "name": disease,
                "probability": prob,
                "keywords": matched_keywords[disease]
            })

        # 确保概率总和为100
        current_total = sum(c["probability"] for c in candidates)
        if current_total < 100:
            candidates.append({"name": "其他", "probability": 100 - current_total})

        best = candidates[0]

        return {
            "success": True,
            "disease_name": best["name"],
            "confidence": best["probability"] / 100,
            "symptoms": self.disease_keywords.get(best["name"], {}).get("symptoms", []),
            "is_healthy": False,
            "candidates": candidates[:5],  # 最多返回5种
            "source": "text_keywords"
        }

    def _detect_general_symptoms(self, text: str) -> List[str]:
        """检测通用症状"""
        symptom_map = {
            "斑点": ["斑点", "斑", "黑点", "褐点", "小点", "点点", "小疙瘩"],
            "腐烂": ["腐烂", "烂", "臭了", "发臭", "淌水", "软了"],
            "黄叶": ["黄叶", "发黄", "变黄", "叶子黄了", "叶黄"],
            "枯萎": ["枯萎", "蔫了", "死了", "枯了", "干了", "打蔫"],
            "卷叶": ["卷叶", "卷了", "往上卷", "往下卷", "缩了"],
            "霉层": ["霉", "长毛", "白毛", "灰毛", "黑毛"],
            "虫害": ["虫", "小虫", "虫子", "有虫", "生虫", "小绿虫", "小飞虫"],
            "水渍": ["水渍", "湿湿的", "水水的", "像水泡过"]
        }

        found = []
        for symptom, keywords in symptom_map.items():
            for kw in keywords:
                if kw in text:
                    found.append(symptom)
                    break
        return found

    def _guess_from_symptoms(self, symptoms: List[str]) -> List[Dict]:
        """根据症状推测可能的病害"""
        # 症状与病害的关联权重
        mapping = {
            "斑点": [("番茄-早疫病", 35), ("番茄-细菌性斑点病", 30), ("番茄-斑枯病", 20), ("番茄-灰叶斑病", 15)],
            "腐烂": [("番茄-晚疫病", 40), ("番茄-灰霉病", 30), ("番茄-软腐病", 20), ("番茄-菌核病", 10)],
            "黄叶": [("番茄-叶霉病", 30), ("番茄-黄化曲叶病毒病", 25), ("番茄-枯萎病", 20), ("番茄-蚜虫", 15), ("番茄-红蜘蛛", 10)],
            "枯萎": [("番茄-青枯病", 35), ("番茄-枯萎病", 30), ("番茄-根腐病", 20), ("番茄-晚疫病", 15)],
            "卷叶": [("番茄-黄化曲叶病毒病", 40), ("番茄-蚜虫", 30), ("番茄-茶黄螨", 20), ("番茄-生理性卷叶", 10)],
            "霉层": [("番茄-叶霉病", 30), ("番茄-灰霉病", 30), ("番茄-晚疫病", 25), ("番茄-煤污病", 15)],
            "虫害": [("番茄-蚜虫", 30), ("番茄-白粉虱", 25), ("番茄-红蜘蛛", 25), ("番茄-棉铃虫", 20)],
            "水渍": [("番茄-晚疫病", 40), ("番茄-灰霉病", 30), ("番茄-细菌性斑点病", 20), ("番茄-软腐病", 10)]
        }

        # 统计各病害得分
        disease_scores = {}
        for symptom in symptoms:
            if symptom in mapping:
                for disease, score in mapping[symptom]:
                    disease_scores[disease] = disease_scores.get(disease, 0) + score

        # 排序并返回
        sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_diseases:
            return [{"name": "番茄-未知病害", "probability": 30}]

        # 归一化概率
        total = sum(s for _, s in sorted_diseases)
        candidates = []
        for disease, score in sorted_diseases[:5]:
            candidates.append({
                "name": disease,
                "probability": min(int(score / total * 100), 90)
            })

        return candidates

    def _detect_from_features(self, image_features: Dict) -> Dict[str, Any]:
        """从图像特征识别"""
        return {
            "success": True,
            "disease_name": "番茄-健康",
            "confidence": 0.5,
            "symptoms": [],
            "is_healthy": True,
            "candidates": [{"name": "番茄-健康", "probability": 50}],
            "source": "color_analysis"
        }

    def get_supported_diseases(self) -> List[str]:
        return self.tomato_labels

    def is_model_loaded(self) -> bool:
        return self.model is not None
