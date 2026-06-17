"""
文件名: schemas.py
功能描述: API 请求和响应的数据模型定义
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 请求模型 ====================

class DiagnosisRequest(BaseModel):
    """
    诊断请求模型
    """
    text_input: Optional[str] = Field(None, description="用户文字描述")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    location: Optional[str] = Field(None, description="位置描述")
    browser_location: Optional[Dict[str, float]] = Field(None, description="浏览器定位结果")

    class Config:
        json_schema_extra = {
            "example": {
                "text_input": "番茄叶子出现黄斑，有腐烂迹象",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "location": "北京市海淀区"
            }
        }


class LocationRequest(BaseModel):
    """
    位置请求模型
    """
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    location: Optional[str] = Field(None, description="手动输入的位置")
    ip_address: Optional[str] = Field(None, description="IP 地址")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "location": "北京市海淀区"
            }
        }


class ChatRequest(BaseModel):
    """
    追问请求模型
    """
    diagnosis_id: int = Field(..., description="诊断记录 ID")
    message: str = Field(..., description="用户追问内容")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis_id": 1,
                "message": "这个病用什么药效果最好？"
            }
        }


# ==================== 响应模型 ====================

class DiseaseResult(BaseModel):
    """
    病虫害识别结果
    """
    disease_name: str = Field(..., description="病害名称")
    confidence: float = Field(..., description="置信度")
    symptoms: List[str] = Field(default_factory=list, description="症状列表")
    is_healthy: bool = Field(False, description="是否健康")
    source: str = Field("model", description="识别来源")


class AgentResult(BaseModel):
    """
    Agent 分析结果
    """
    success: bool = Field(..., description="是否成功")
    analysis: Optional[str] = Field(None, description="分析内容")
    advice: Optional[str] = Field(None, description="建议内容")
    error: Optional[str] = Field(None, description="错误信息")


class DiagnosisResponse(BaseModel):
    """
    诊断响应模型
    """
    success: bool = Field(..., description="是否成功")
    diagnosis_id: Optional[int] = Field(None, description="诊断记录ID")
    disease_result: Optional[DiseaseResult] = Field(None, description="病虫害识别结果")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="天气数据")
    weather_analysis: Optional[AgentResult] = Field(None, description="天气分析")
    soil_analysis: Optional[AgentResult] = Field(None, description="土壤分析")
    irrigation_advice: Optional[AgentResult] = Field(None, description="灌溉建议")
    safety_advice: Optional[AgentResult] = Field(None, description="安全用药建议")
    calendar_advice: Optional[AgentResult] = Field(None, description="种植日历建议")
    memory_analysis: Optional[AgentResult] = Field(None, description="记忆分析")
    final_advice: Optional[str] = Field(None, description="最终综合建议")
    error: Optional[str] = Field(None, description="错误信息")


class LocationResponse(BaseModel):
    """
    位置响应模型
    """
    success: bool = Field(..., description="是否成功")
    location: Optional[str] = Field(None, description="位置描述")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    source: Optional[str] = Field(None, description="定位来源")
    error: Optional[str] = Field(None, description="错误信息")


class HistoryResponse(BaseModel):
    """
    历史记录响应模型
    """
    success: bool = Field(..., description="是否成功")
    records: List[Dict[str, Any]] = Field(default_factory=list, description="历史记录列表")
    total: int = Field(0, description="总记录数")


class UserProfileResponse(BaseModel):
    """
    用户档案响应模型
    """
    success: bool = Field(..., description="是否成功")
    user_info: Optional[Dict[str, Any]] = Field(None, description="用户信息")
    statistics: Optional[Dict[str, Any]] = Field(None, description="统计信息")
    recent_diagnoses: List[Dict[str, Any]] = Field(default_factory=list, description="最近诊断记录")


class HealthResponse(BaseModel):
    """
    健康检查响应模型
    """
    status: str = Field("ok", description="服务状态")
    version: str = Field("1.0.0", description="版本号")
    timestamp: str = Field(..., description="当前时间")


class ChatResponse(BaseModel):
    """
    追问响应模型
    """
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="AI 回复")
    diagnosis_id: Optional[int] = Field(None, description="诊断记录 ID")
    error: Optional[str] = Field(None, description="错误信息")
