# 🍅 番茄卫士 - AI 病虫害智能诊断系统

基于多 Agent 协作和 RAG 知识库的番茄病虫害智能诊断系统。

## 功能特点

- 🔍 **智能识别** - 支持文字描述和图片上传识别病虫害
- 📊 **多概率分析** - 返回多种可能的病症及概率
- 🌤️ **天气结合** - 结合当地天气给出防治建议
- 🌱 **土壤分析** - 根据河南各地土壤性质分析
- 💬 **对话追问** - 支持多轮对话，结合历史上下文
- 📚 **RAG 知识库** - 内置番茄病虫害和土壤知识

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 前端依赖
cd frontend
npm install
```

### 2. 下载向量模型

向量模型文件较大（约 184MB），需要单独下载：

**下载地址：** [BAAI/bge-small-zh](https://huggingface.co/BAAI/bge-small-zh)

下载后将模型文件放在项目**同级目录**的 `向量模型` 文件夹中：

```
项目父目录/
├── 向量模型/
│   ├── config.json
│   ├── model.safetensors
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   └── ...
└── project/          # 本项目
    ├── main.py
    └── ...
```

### 3. 构建 RAG 知识库索引

```bash
cd project
python rag/build_single.py
```

### 4. 启动项目

```bash
python start.py
```

访问 http://localhost:3000

## 项目结构

```
project/
├── main.py                 # FastAPI 主入口
├── config.py               # 配置文件
├── model.py                # LLM 模型配置
├── start.py                # 一键启动脚本
├── requirements.txt        # Python 依赖
│
├── agents/                 # 智能体层
│   ├── supervisor.py       # 任务调度
│   ├── disease_agent.py    # 病害知识 Agent
│   ├── weather_agent.py    # 天气 Agent
│   └── ...
│
├── models/                 # 模型层
│   ├── disease_detector.py # 病虫害识别
│   └── ...
│
├── services/               # 服务层
│   ├── llm_service.py      # LLM 服务
│   └── ...
│
├── rag/                    # RAG 知识库
│   ├── rag_system.py       # RAG 核心系统
│   ├── build_single.py     # 索引构建脚本
│   └── vector_db/          # 向量数据库（自动生成）
│
├── rag知识库/              # 知识库文档
│   ├── 土壤性质与番茄病虫害.txt
│   └── ...
│
├── api/                    # API 路由
├── database/               # 数据库
└── frontend/               # Vue.js 前端
```

## 配置说明

### LLM 配置

编辑 `config.py` 或 `model.py`：

```python
LLM_API_KEY = "你的API Key"
LLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.7"
```

### 彩云天气 API

编辑 `services/weather_service.py`：

```python
self.api_key = "你的彩云API Key"
```

## 使用说明

1. **定位** - 点击"获取当前位置"或手动输入地区
2. **选择土质** - 系统自动推断或手动选择
3. **描述症状** - 输入文字描述或上传图片
4. **查看结果** - 系统返回多种可能的病症及概率
5. **追问** - 可以继续提问获取更详细的建议

## 技术栈

- **后端**：FastAPI + SQLAlchemy + LangChain
- **前端**：Vue.js 3 + Vite + Axios
- **LLM**：智谱 AI GLM-4
- **向量模型**：BAAI/bge-small-zh
- **向量数据库**：FAISS
- **天气 API**：彩云天气

## 许可证

本项目仅供学习和研究使用。
