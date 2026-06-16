# 番茄病虫害识别系统

基于多 Agent 协作的番茄病虫害智能诊断系统，为农户提供专业的病虫害识别和防治建议。

## 功能特点

- 🖼️ **图片识别**：上传番茄图片，AI 自动识别病虫害类型
- 💬 **文字描述**：支持文字输入症状描述
- 🌤️ **天气分析**：结合天气信息分析病虫害影响
- 🌱 **土壤分析**：基于位置信息分析土壤状况
- 💧 **灌溉建议**：提供科学的灌溉方案
- 💊 **安全用药**：推荐安全的农药使用方案
- 📅 **种植日历**：生成农事提醒和种植计划
- 🧠 **长期记忆**：记录用户历史，提供个性化建议

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：SQLite + SQLAlchemy
- **LLM**：智谱 AI GLM-4
- **图像处理**：Pillow
- **Agent 框架**：自定义 Agent 类

### 前端
- **框架**：Vue.js 3
- **构建工具**：Vite
- **UI 框架**：Bootstrap 5
- **HTTP 客户端**：Axios

## 项目结构

```
project/
├── main.py                     # FastAPI 应用主入口
├── config.py                   # 配置文件
├── model.py                    # LLM 模型配置
├── requirements.txt            # 依赖包列表
├── README.md                   # 项目说明文档
│
├── agents/                     # 智能体层
│   ├── base_agent.py          # Agent 基类
│   ├── supervisor.py          # Supervisor Agent（任务调度）
│   ├── disease_agent.py       # 病害知识 Agent
│   ├── weather_agent.py       # 天气 Agent
│   ├── soil_agent.py          # 土壤分析 Agent
│   ├── irrigation_agent.py    # 灌溉 Agent
│   ├── safety_agent.py        # 安全用药 Agent
│   ├── calendar_agent.py      # 种植日历 Agent
│   └── memory_agent.py        # 记忆 Agent
│
├── models/                     # 模型层
│   ├── image_processor.py     # 图像处理
│   ├── text_processor.py      # 文本处理
│   └── disease_detector.py    # 病虫害识别（预留接口）
│
├── services/                   # 服务层
│   ├── llm_service.py         # LLM 服务
│   ├── weather_service.py     # 天气服务
│   ├── soil_service.py        # 土壤服务
│   ├── location_service.py    # 定位服务
│   └── database_service.py   # 数据库服务
│
├── api/                        # API 路由层
│   ├── routes.py              # 主要路由
│   └── schemas.py             # 请求/响应模型
│
├── database/                   # 数据库
│   ├── models.py              # 数据模型
│   └── init_db.py             # 数据库初始化脚本
│
├── frontend/                   # Vue.js 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/
│       ├── views/
│       ├── components/
│       └── assets/
│
└── docs/                       # 文档目录
    ├── 项目结构.txt
    ├── 需求文档.md
    └── API文档.md
```

## 快速开始

### 1. 安装后端依赖

```bash
cd project
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python main.py
```

后端服务将在 http://localhost:8000 启动

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端开发服务器

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 5. 访问应用

打开浏览器访问 http://localhost:3000

## API 文档

启动后端服务后，可以访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API 接口

### 诊断接口
- `POST /api/diagnosis` - 创建诊断请求
- `GET /api/history` - 获取诊断历史
- `GET /api/user/profile` - 获取用户档案

### 工具接口
- `POST /api/location` - 解析位置信息
- `GET /api/diseases` - 获取支持的病害列表
- `GET /api/model/status` - 获取模型状态

## 配置说明

### LLM 配置

在 `config.py` 中配置智谱 AI 的 API Key：

```python
LLM_API_KEY = "your_api_key"
LLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.7"
```

### 天气 API 配置

配置彩云天气 API Key（可选）：

```python
CAIYUN_API_KEY = "your_caiyun_api_key"
```

## 扩展说明

### 接入训练好的模型

在 `models/disease_detector.py` 中预留了模型接口，训练完成后可以接入：

```python
# 加载模型
self.model = load_your_model()

# 在 detect 方法中使用模型
predictions = self.model.predict(image)
```

### 接入 RAG 知识库

在 `agents/disease_agent.py` 中预留了 RAG 接口：

```python
# 初始化知识库
self.knowledge_base = YourRAGSystem()

# 在 _query_knowledge_base 方法中查询
results = self.knowledge_base.query(disease_name)
```

## 开发说明

- 作者：ZT
- 日期：2026/6/16
- Python 版本：3.12+

## 许可证

本项目仅供学习和研究使用。
