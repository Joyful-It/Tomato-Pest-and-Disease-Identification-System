# 番茄病虫害识别系统 - API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 前缀**: `/api`
- **文档地址**: `http://localhost:8000/docs` (Swagger UI)

## 接口列表

### 1. 健康检查

#### GET /api/health

检查服务状态

**响应示例：**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-06-16T12:00:00"
}
```

---

### 2. 创建诊断

#### POST /api/diagnosis

创建病虫害诊断请求

**请求方式：** `multipart/form-data`

**参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 否 | 上传的图片文件 |
| request | String | 是 | JSON 格式的请求参数 |

**request 参数结构：**
```json
{
  "text_input": "番茄叶子出现黄斑",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "location": "北京市海淀区",
  "browser_location": {
    "latitude": 39.9042,
    "longitude": 116.4074
  }
}
```

**响应示例：**
```json
{
  "success": true,
  "diagnosis_id": 1,
  "disease_result": {
    "disease_name": "番茄-早疫病",
    "confidence": 0.85,
    "symptoms": ["斑点", "变色"],
    "is_healthy": false,
    "source": "model"
  },
  "weather_analysis": {
    "success": true,
    "analysis": "当前天气多云，温度适中...",
    "advice": "建议在晴天进行施药..."
  },
  "soil_analysis": {
    "success": true,
    "analysis": "土壤 pH 值适中...",
    "advice": "建议增施有机肥..."
  },
  "irrigation_advice": {
    "success": true,
    "analysis": "当前土壤湿度适中...",
    "advice": "建议采用滴灌方式..."
  },
  "safety_advice": {
    "success": true,
    "analysis": "推荐使用低毒农药...",
    "advice": "建议使用百菌清..."
  },
  "calendar_advice": {
    "success": true,
    "analysis": "未来一周适合进行病害防治...",
    "advice": null
  },
  "memory_analysis": {
    "success": true,
    "analysis": "该农户最常遇到的病害问题...",
    "advice": "针对该农户的个性化建议..."
  },
  "final_advice": "根据诊断结果，建议采取以下措施：\n1. 病害防治..."
}
```

---

### 3. 获取诊断历史

#### GET /api/history

获取用户的诊断历史记录

**查询参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | Integer | 否 | 10 | 返回记录数限制 |

**响应示例：**
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "date": "2026-06-16 12:00:00",
      "disease_name": "番茄-早疫病",
      "location": "北京市海淀区",
      "text_input": "番茄叶子出现黄斑"
    }
  ],
  "total": 1
}
```

---

### 4. 获取用户档案

#### GET /api/user/profile

获取当前用户的档案信息

**响应示例：**
```json
{
  "success": true,
  "user_info": {
    "id": 1,
    "username": "default",
    "location": "北京市海淀区",
    "created_at": "2026-06-16 10:00:00"
  },
  "statistics": {
    "total_diagnoses": 5,
    "total_memories": 12
  },
  "recent_diagnoses": [
    {
      "date": "2026-06-16",
      "disease": "番茄-早疫病"
    }
  ]
}
```

---

### 5. 解析位置信息

#### POST /api/location

解析用户的位置信息

**请求体：**
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "location": "北京市海淀区",
  "ip_address": "123.456.789.0"
}
```

**响应示例：**
```json
{
  "success": true,
  "location": "中国 北京市 海淀区",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "source": "browser"
}
```

---

### 6. 获取支持的病害列表

#### GET /api/diseases

获取系统支持识别的病害列表

**响应示例：**
```json
{
  "success": true,
  "diseases": [
    "番茄-细菌性斑点病",
    "番茄-早疫病",
    "番茄-晚疫病",
    "番茄-叶霉病",
    "番茄-斑枯病",
    "番茄-红蜘蛛",
    "番茄-花叶病毒病",
    "番茄-黄化曲叶病毒病",
    "番茄-健康"
  ]
}
```

---

### 7. 获取模型状态

#### GET /api/model/status

获取病虫害识别模型的加载状态

**响应示例：**
```json
{
  "success": true,
  "model_loaded": false,
  "supported_diseases": 9
}
```

---

## 错误响应

所有接口在出错时返回统一格式：

```json
{
  "success": false,
  "error": "错误信息",
  "detail": "详细错误描述（可选）"
}
```

**常见 HTTP 状态码：**

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### 使用 cURL 调用诊断接口

```bash
# 上传图片进行诊断
curl -X POST "http://localhost:8000/api/diagnosis" \
  -F "file=@tomato_image.jpg" \
  -F 'request={"text_input":"叶子有黄斑","location":"北京市"}'

# 仅文字描述诊断
curl -X POST "http://localhost:8000/api/diagnosis" \
  -H "Content-Type: application/json" \
  -d '{"text_input":"番茄叶子出现黄色斑点，有腐烂迹象","location":"北京市海淀区"}'

# 获取诊断历史
curl "http://localhost:8000/api/history?limit=5"
```

### 使用 Python 调用

```python
import requests

# 诊断请求
files = {"file": open("tomato.jpg", "rb")}
data = {"request": '{"text_input":"叶子有黄斑","location":"北京市"}'}
response = requests.post("http://localhost:8000/api/diagnosis", files=files, data=data)
result = response.json()

# 获取历史记录
response = requests.get("http://localhost:8000/api/history", params={"limit": 10})
history = response.json()
```

### 使用 JavaScript 调用

```javascript
// 诊断请求
const formData = new FormData();
formData.append('file', imageFile);
formData.append('request', JSON.stringify({
  text_input: '叶子有黄斑',
  location: '北京市'
}));

const response = await fetch('/api/diagnosis', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// 获取历史记录
const historyResponse = await fetch('/api/history?limit=10');
const history = await historyResponse.json();
```
