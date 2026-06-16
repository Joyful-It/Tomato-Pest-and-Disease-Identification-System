"""
文件名: memory_agent.py
功能描述: 记忆 Agent，负责长期记忆管理和用户档案维护
作者: ZT
日期: 2026/6/16
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from services.database_service import DatabaseService


class MemoryAgent(BaseAgent):
    """
    记忆 Agent
    负责长期记忆管理和用户档案维护
    """

    def __init__(self, llm_service):
        """
        初始化记忆 Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        self.db_service = DatabaseService()

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析和管理用户记忆

        Args:
            context: 包含诊断信息的上下文

        Returns:
            记忆分析结果
        """
        # 获取用户ID
        user_id = context.get("user_id", 1)  # 默认用户

        # 获取用户历史记忆
        user_memories = self.db_service.get_user_memories(user_id)
        memory_summary = self.db_service.get_user_memory_summary(user_id)

        # 获取诊断历史
        diagnosis_history = self.db_service.get_user_diagnosis_history(user_id, limit=5)

        # 分析历史模式
        history_patterns = await self._analyze_history_patterns(
            diagnosis_history, user_memories
        )

        # 生成个性化建议
        personalized_advice = await self._generate_personalized_advice(
            context, history_patterns, memory_summary
        )

        # 保存当前诊断到记忆
        await self._save_diagnosis_to_memory(user_id, context)

        return {
            "success": True,
            "user_id": user_id,
            "memory_summary": memory_summary,
            "history_patterns": history_patterns,
            "personalized_advice": personalized_advice,
            "total_diagnoses": len(diagnosis_history)
        }

    async def _analyze_history_patterns(
        self,
        diagnosis_history: list,
        user_memories: list
    ) -> Dict[str, Any]:
        """
        分析历史诊断模式

        Args:
            diagnosis_history: 诊断历史
            user_memories: 用户记忆

        Returns:
            历史模式分析
        """
        # 统计常见病害
        disease_counts = {}
        for record in diagnosis_history:
            if record.disease_result:
                disease_name = record.disease_result.get("disease_name", "未知")
                disease_counts[disease_name] = disease_counts.get(disease_name, 0) + 1

        # 分析记忆内容
        preferences = []
        knowledge = []
        for memory in user_memories:
            if memory.memory_type == "preference":
                preferences.append(memory.content)
            elif memory.memory_type == "knowledge":
                knowledge.append(memory.content)

        # 使用 LLM 分析模式
        prompt = f"""分析农户的历史诊断记录和偏好：

常见病害：{disease_counts}
用户偏好：{preferences}
历史知识：{knowledge}

请分析：
1. 该农户最常遇到的病害问题
2. 可能存在的种植管理问题
3. 需要特别关注的方面"""

        system_prompt = "你是一个农业数据分析专家，请分析农户的历史诊断模式。"

        response = await self._call_llm(system_prompt, prompt)

        return {
            "common_diseases": disease_counts,
            "user_preferences": preferences,
            "analysis": response
        }

    async def _generate_personalized_advice(
        self,
        context: Dict[str, Any],
        history_patterns: Dict[str, Any],
        memory_summary: Dict[str, Any]
    ) -> str:
        """
        生成个性化建议

        Args:
            context: 当前上下文
            history_patterns: 历史模式
            memory_summary: 记忆摘要

        Returns:
            个性化建议
        """
        current_disease = context.get("disease_result", {}).get("disease_name", "未知")
        common_diseases = history_patterns.get("common_diseases", {})

        prompt = f"""根据农户的历史记录和当前诊断，提供个性化建议：

当前病害：{current_disease}
历史常见病害：{common_diseases}
历史分析：{history_patterns.get('analysis', '')}
用户记忆：{memory_summary}

请提供：
1. 针对该农户的个性化防治建议
2. 基于历史经验的改进措施
3. 预防复发的长期建议
4. 需要特别注意的事项"""

        system_prompt = "你是一个资深农业顾问，请根据农户的历史记录提供个性化建议。"

        return await self._call_llm(system_prompt, prompt)

    async def _save_diagnosis_to_memory(
        self,
        user_id: int,
        context: Dict[str, Any]
    ) -> None:
        """
        保存诊断信息到记忆

        Args:
            user_id: 用户ID
            context: 诊断上下文
        """
        disease_result = context.get("disease_result", {})
        disease_name = disease_result.get("disease_name", "未知")

        # 保存诊断历史
        self.db_service.add_user_memory(
            user_id=user_id,
            memory_type="history",
            content=f"诊断了{disease_name}",
            metadata={
                "disease_name": disease_name,
                "confidence": disease_result.get("confidence", 0),
                "location": context.get("location", "")
            }
        )

        # 如果是新病害，保存为知识
        if disease_name and disease_name != "未知":
            self.db_service.add_user_memory(
                user_id=user_id,
                memory_type="knowledge",
                content=f"番茄{disease_name}的诊断和治疗经验",
                metadata={
                    "disease_name": disease_name,
                    "treatment": context.get("final_advice", "")
                }
            )

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户档案

        Args:
            user_id: 用户ID

        Returns:
            用户档案
        """
        user = self.db_service.get_user(user_id)
        if not user:
            return {"error": "用户不存在"}

        memories = self.db_service.get_user_memories(user_id)
        diagnosis_history = self.db_service.get_user_diagnosis_history(user_id)

        return {
            "user_info": {
                "id": user.id,
                "username": user.username,
                "location": user.location,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            },
            "statistics": {
                "total_diagnoses": len(diagnosis_history),
                "total_memories": len(memories)
            },
            "recent_diagnoses": [
                {
                    "date": record.created_at.strftime("%Y-%m-%d"),
                    "disease": record.disease_result.get("disease_name", "未知") if record.disease_result else "未知"
                }
                for record in diagnosis_history[:5]
            ]
        }