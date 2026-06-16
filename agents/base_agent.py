"""
文件名: base_agent.py
功能描述: Agent 基类，定义所有智能体的通用接口
作者: ZT
日期: 2026/6/16
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from services.llm_service import LLMService


class BaseAgent(ABC):
    """
    Agent 基类
    所有专业智能体都继承此类
    """

    def __init__(self, llm_service: LLMService):
        """
        初始化 Agent

        Args:
            llm_service: LLM 服务实例
        """
        self.llm_service = llm_service
        self.name = self.__class__.__name__

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析任务

        Args:
            context: 上下文信息，包含输入数据和其他 Agent 的分析结果

        Returns:
            分析结果字典
        """
        pass

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用 LLM

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            LLM 回复内容
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await self.llm_service.chat(messages)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        格式化上下文信息

        Args:
            context: 上下文字典

        Returns:
            格式化后的文本
        """
        parts = []
        for key, value in context.items():
            if value is not None:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)
