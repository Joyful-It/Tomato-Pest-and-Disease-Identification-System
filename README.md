# 🍅 AgriMate — 番茄病虫害 AI 智能诊断系统

基于 **Swin Tiny 97.4% 识别 + 多 Agent 协作 + RAG 知识库** 的番茄病虫害智能诊断系统。

## 功能特点

- 🔍 **拍照识别** — 上传番茄叶片照片，Swin Tiny 自动识别 10 种病害，97.4% 准确率
- 📊 **多 Agent 协作** — 7 个 AI 专家并行分析（病害/天气/土壤/灌溉/用药/农事/历史）
- 🌤️ **实时天气** — 结合当地天气给出防治建议
- 📚 **RAG 知识库** — 内置番茄病虫害防治、河南土壤数据
- 💬 **追问对话** — 对诊断结果多轮追问

## 快速开始

### 0. 环境要求

- Python 3.10+
- Node.js 18+
- 建议 Windows / Linux

### 1. 安装后端依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install faiss-cpu -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 设置 LLM API Key

```bash
# Windows PowerShell
$env:LLM_API_KEY="你的DeepSeek-Key"

# 或永久设置
setx LLM_API_KEY "你的DeepSeek-Key"
```

### 3. 放置向量模型

将向量模型文件放在项目**同级目录**的 `向量模型` 文件夹中（从队友处获取，约 470MB）：

```
farming_recogn/
├── 向量模型/           # ← 放这里
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── ...
└── smart-agriculture/  # 本项目
    └── ...
```

如没有本地模型，首次运行会自动从 HuggingFace 下载。

### 4. 构建 RAG 索引

```bash
cd smart-agriculture
python rag/build_single.py
```

### 5. 安装前端依赖

```bash
cd frontend
npm install
```

### 6. 启动

```bash
# 终端 1：后端
cd smart-agriculture
python main.py

# 终端 2：前端
cd smart-agriculture/frontend
npm run dev
```

- 后端：http://localhost:8000 （API 文档：http://localhost:8000/docs）
- 前端：http://localhost:3000

## 项目结构

```
smart-agriculture/
├── main.py                 # FastAPI 主入口
├── config.py               # 配置文件（LLM Key 等）
├── start.py                # 一键启动脚本
├── requirements.txt        # Python 依赖
│
├── agents/                 # 7 个 AI Agent
│   ├── supervisor.py       # 任务调度器
│   ├── disease_agent.py    # 病害知识（结合 RAG）
│   ├── weather_agent.py    # 天气分析
│   ├── soil_agent.py       # 土壤分析
│   ├── irrigation_agent.py # 灌溉建议
│   ├── safety_agent.py     # 用药安全
│   ├── calendar_agent.py   # 农事日历
│   └── memory_agent.py     # 历史记忆
│
├── models/                 # 模型层
│   ├── disease_detector.py # Swin Tiny 病虫害识别
│   ├── image_processor.py  # 图像处理 Pipeline
│   └── text_processor.py   # 文本处理
│
├── services/               # 服务层
│   ├── llm_service.py      # LLM 服务（DeepSeek）
│   ├── database_service.py # 数据库操作
│   ├── weather_service.py  # 彩云天气
│   ├── location_service.py # 定位服务
│   └── soil_service.py     # 土壤数据
│
├── rag/                    # RAG 知识库
│   ├── rag_system.py       # RAG 核心
│   ├── build_single.py     # 索引构建
│   └── file_upload.py      # 文件上传
│
├── rag知识库/              # 知识文档
│   ├── 番茄病虫害.txt
│   ├── 土壤性质与番茄病虫害.txt
│   └── 河南各县土壤情况.txt
│
├── api/                    # API 路由
├── database/               # 数据库层
├── frontend/               # Vue.js 前端
└── docs/                   # 文档
```

## 配置说明

编辑 `config.py`：

```python
LLM_BASE_URL = "https://api.deepseek.com/v1"   # API 地址
LLM_MODEL = "deepseek-chat"                     # 模型名
# 也可用智谱: base_url="https://open.bigmodel.cn/api/paas/v4", model="glm-4"
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 图像识别 | Swin Tiny (97.4% on 15,011 images) |
| 大语言模型 | DeepSeek Chat |
| 向量检索 | FAISS + MiniLM-L12-v2 |
| 后端框架 | FastAPI + SQLAlchemy + SQLite |
| 前端 | Vue 3 + Bootstrap 5 + Vite |

## 模型信息

- 基座模型：microsoft/swin-tiny-patch4-window7-224
- 微调数据：PlantVillage 番茄 10 类（800 张训练）
- 测试数据：15,011 张纯未见数据
- 准确率：**97.4%**
