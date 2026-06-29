"""
文件名: schemas.py
功能描述: API 请求和响应的数据模型定义
作者: ZT
日期: 2026/6/17
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DiagnosisRequest(BaseModel):
    text_input: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None
    browser_location: Optional[Dict[str, float]] = None
    soil_type: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None


class LocationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None


class ChatRequest(BaseModel):
    diagnosis_id: int
    message: str
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class DiseaseCandidate(BaseModel):
    name: str
    probability: int
    keywords: Optional[List[str]] = None


class DiseaseResult(BaseModel):
    disease_name: str
    confidence: float
    symptoms: List[str] = Field(default_factory=list)
    is_healthy: bool = False
    source: str = "model"
    candidates: List[DiseaseCandidate] = Field(default_factory=list)


class AgentResult(BaseModel):
    success: bool
    analysis: Optional[str] = None
    advice: Optional[str] = None
    error: Optional[str] = None


class DiagnosisResponse(BaseModel):
    success: bool
    diagnosis_id: Optional[int] = None
    disease_result: Optional[DiseaseResult] = None
    weather_data: Optional[Dict[str, Any]] = None
    weather_analysis: Optional[AgentResult] = None
    soil_analysis: Optional[AgentResult] = None
    irrigation_advice: Optional[AgentResult] = None
    safety_advice: Optional[AgentResult] = None
    calendar_advice: Optional[AgentResult] = None
    memory_analysis: Optional[AgentResult] = None
    final_advice: Optional[str] = None
    error: Optional[str] = None


class LocationResponse(BaseModel):
    success: bool
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None
    error: Optional[str] = None


class HistoryResponse(BaseModel):
    success: bool
    records: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0


class UserProfileResponse(BaseModel):
    success: bool
    user_info: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    recent_diagnoses: List[Dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: str


class ChatResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    diagnosis_id: Optional[int] = None
    error: Optional[str] = None
