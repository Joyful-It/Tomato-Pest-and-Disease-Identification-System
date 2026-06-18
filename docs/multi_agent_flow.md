# 多智能体协作流程图

## 架构概览

本项目采用 **Supervisor + Specialist Agents** 模式，实现多智能体协作的番茄病虫害诊断系统。

## 流程图

```mermaid
graph TD
    A[用户输入<br/>图像/文本] --> B[病害检测模型]
    B --> C{Supervisor Agent}

    C -->|任务分解| D[任务队列]

    D -->|优先级排序| E1[DiseaseAgent<br/>病害知识分析]
    D -->|优先级排序| E2[WeatherAgent<br/>天气影响分析]
    D -->|优先级排序| E3[SoilAgent<br/>土壤状况分析]
    D -->|优先级排序| E4[IrrigationAgent<br/>灌溉需求分析]
    D -->|优先级排序| E5[SafetyAgent<br/>安全用药建议]
    D -->|优先级排序| E6[CalendarAgent<br/>农事日历]
    D -->|优先级排序| E7[MemoryAgent<br/>用户记忆管理]

    E1 -->|asyncio.gather| F[结果聚合]
    E2 -->|asyncio.gather| F
    E3 -->|asyncio.gather| F
    E4 -->|asyncio.gather| F
    E5 -->|asyncio.gather| F
    E6 -->|asyncio.gather| F
    E7 -->|asyncio.gather| F

    F --> G[LLMService<br/>生成综合建议]
    G --> H[诊断结果返回]
    H --> I[(诊断记录存储)]

    J[用户追问] --> K{获取诊断记录}
    K -->|找到记录| L[构建对话上下文]
    K -->|未找到| M[返回错误]
    L --> N{LLM 可用?}
    N -->|是| O[LLM 生成回答]
    N -->|否| P[RAG 知识库检索]
    O --> Q[追问回答返回]
    P --> Q

    H -.->|用户可继续追问| J

    style A fill:#e1f5fe
    style H fill:#e8f5e8
    style C fill:#fff3e0
    style G fill:#f3e5f5
    style J fill:#fce4ec
    style Q fill:#e8f5e8
```

## 流程说明

### 主流程（诊断）

```
用户输入 → 病害检测 → Supervisor 分解任务 → 7个Agent并行执行 → 结果聚合 → 生成建议 → 诊断结果返回
```

### 追问流程（Chat）

```
用户追问 → 获取诊断记录 → 构建对话上下文 → LLM生成回答（或RAG降级） → 追问回答返回
```

## 智能体清单

| 智能体 | 文件 | 职责 |
|--------|------|------|
| `SupervisorAgent` | `supervisor.py` | 中央编排：任务分解、优先级排序、并行调度 |
| `DiseaseAgent` | `disease_agent.py` | 病害知识分析（集成 RAG） |
| `WeatherAgent` | `weather_agent.py` | 气象影响分析 |
| `SoilAgent` | `soil_agent.py` | 土壤状况分析 |
| `IrrigationAgent` | `irrigation_agent.py` | 灌溉需求分析 |
| `SafetyAgent` | `safety_agent.py` | 农药推荐与安全审计 |
| `CalendarAgent` | `calendar_agent.py` | 农事日历与提醒 |
| `MemoryAgent` | `memory_agent.py` | 用户长期记忆管理 |

## 关键接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/diagnosis` | POST | 创建诊断（主流程） |
| `/chat` | POST | 用户追问（基于诊断结果） |

## 技术特点

- **并发模型**: `asyncio.gather` 并行执行
- **LLM 集成**: LangChain + 智谱 GLM-4
- **降级策略**: LLM 不可用时回退到 RAG/规则引擎
- **上下文关联**: 追问系统基于诊断记录构建对话上下文

## 相关文件

- `agents/supervisor.py` - Supervisor Agent 实现
- `agents/base_agent.py` - Agent 基类定义
- `api/routes.py` - API 路由（包含诊断和追问接口）
- `services/llm_service.py` - LLM 服务
