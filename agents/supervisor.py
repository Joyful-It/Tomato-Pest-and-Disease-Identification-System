"""
文件名: supervisor.py
功能描述: Supervisor Agent，负责任务拆解与调度，协调其他 Agent 的工作
作者: ZT
日期: 2026/6/17
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent
    负责任务拆解与调度，协调其他专业 Agent 的工作流程
    """

    def __init__(self, llm_service):
        """
        初始化 Supervisor Agent

        Args:
            llm_service: LLM 服务实例
        """
        super().__init__(llm_service)
        self.task_queue = []
        self.results = {}

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析输入，拆解任务并调度
        如果 LLM 不可用，直接返回默认任务列表

        Args:
            context: 包含图像和文本分析结果的上下文

        Returns:
            任务调度结果
        """
        # 检查 LLM 是否可用
        if not self.llm_service.is_available:
            # LLM 不可用，返回默认任务列表
            tasks = self._get_default_tasks()
            return {
                "success": True,
                "tasks": tasks,
                "total_tasks": len(tasks),
                "mode": "default"
            }

        # LLM 可用，使用 LLM 分析任务
        try:
            analysis_prompt = self._build_analysis_prompt(context)

            system_prompt = """你是一个任务调度专家。根据用户的输入（图像分析和文字描述），
判断需要执行哪些分析任务，并为每个任务生成具体的分析要求。

返回 JSON 格式的任务列表：
{
    "tasks": [
        {
            "agent": "agent_name",
            "priority": 1-5,
            "requirements": "具体分析要求"
        }
    ]
}"""

            response = await self._call_llm(system_prompt, analysis_prompt)

            # 解析任务列表
            tasks = self._parse_tasks(response, context)

            return {
                "success": True,
                "tasks": tasks,
                "total_tasks": len(tasks),
                "mode": "llm"
            }
        except Exception as e:
            print(f"Supervisor Agent 分析失败: {e}")
            # 失败时返回默认任务
            tasks = self._get_default_tasks()
            return {
                "success": True,
                "tasks": tasks,
                "total_tasks": len(tasks),
                "mode": "fallback"
            }

    def _get_default_tasks(self) -> List[Dict[str, Any]]:
        """
        获取默认任务列表（LLM 不可用时使用）

        Returns:
            默认任务列表
        """
        return [
            {"agent": "disease_agent", "priority": 1, "requirements": "分析病虫害信息，从知识库检索相关防治方法"},
            {"agent": "weather_agent", "priority": 2, "requirements": "分析天气对病虫害的影响"},
            {"agent": "soil_agent", "priority": 3, "requirements": "分析土壤状况"},
            {"agent": "irrigation_agent", "priority": 4, "requirements": "提供灌溉建议"},
            {"agent": "safety_agent", "priority": 5, "requirements": "提供安全用药建议"},
            {"agent": "calendar_agent", "priority": 6, "requirements": "提供种植日历建议"},
            {"agent": "memory_agent", "priority": 7, "requirements": "检索用户历史记忆"}
        ]

    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """
        构建分析提示词

        Args:
            context: 上下文信息

        Returns:
            提示词
        """
        parts = ["请分析以下用户输入，确定需要执行的分析任务：\n"]

        if context.get("image_analysis"):
            parts.append(f"图像分析结果：{context['image_analysis']}\n")

        if context.get("text_input"):
            parts.append(f"用户文字描述：{context['text_input']}\n")

        if context.get("disease_result"):
            parts.append(f"病虫害识别结果：{context['disease_result']}\n")

        parts.append("\n可用的 Agent：")
        parts.append("- disease_agent: 病害知识分析（RAG）")
        parts.append("- weather_agent: 天气分析")
        parts.append("- soil_agent: 土壤分析")
        parts.append("- irrigation_agent: 灌溉建议")
        parts.append("- safety_agent: 安全用药")
        parts.append("- calendar_agent: 种植日历")
        parts.append("- memory_agent: 用户记忆")

        return "\n".join(parts)

    def _parse_tasks(self, response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析 LLM 返回的任务列表

        Args:
            response: LLM 响应
            context: 上下文信息

        Returns:
            任务列表
        """
        import json

        # 默认任务列表
        default_tasks = self._get_default_tasks()

        # 检查 response 是否为 None
        if response is None:
            return default_tasks

        try:
            # 尝试解析 JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return data.get("tasks", default_tasks)
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass

        # 如果解析失败，返回默认任务
        return default_tasks

    async def dispatch_tasks(
        self,
        tasks: List[Dict[str, Any]],
        agents: Dict[str, BaseAgent],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分发任务给各个 Agent

        Args:
            tasks: 任务列表
            agents: Agent 字典
            context: 上下文信息

        Returns:
            所有 Agent 的分析结果
        """
        import asyncio

        results = {}

        # 按优先级排序
        sorted_tasks = sorted(tasks, key=lambda x: x.get("priority", 99))

        # 并行执行任务
        async def run_agent(agent_name: str, requirements: str):
            if agent_name in agents:
                agent = agents[agent_name]
                task_context = {
                    **context,
                    "requirements": requirements
                }
                try:
                    result = await agent.analyze(task_context)
                    results[agent_name] = result
                except Exception as e:
                    print(f"Agent {agent_name} 执行失败: {e}")
                    results[agent_name] = {
                        "success": False,
                        "error": str(e)
                    }

        # 创建所有任务的协程
        coroutines = [
            run_agent(task["agent"], task["requirements"])
            for task in sorted_tasks
            if task["agent"] in agents
        ]

        # 并行执行
        await asyncio.gather(*coroutines)

        return results