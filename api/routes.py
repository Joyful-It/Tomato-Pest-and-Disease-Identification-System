"""
文件名: routes.py
功能描述: FastAPI 路由定义，处理所有 API 请求
作者: ZT
日期: 2026/6/16
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime

from .schemas import (
    DiagnosisRequest,
    DiagnosisResponse,
    LocationRequest,
    LocationResponse,
    HistoryResponse,
    UserProfileResponse,
    HealthResponse,
    DiseaseResult,
    AgentResult
)

from services.llm_service import LLMService
from services.database_service import DatabaseService
from services.location_service import LocationService
from services.weather_service import WeatherService
from services.soil_service import SoilService

from models.image_processor import ImageProcessor
from models.text_processor import TextProcessor
from models.disease_detector import DiseaseDetector

from agents import (
    SupervisorAgent,
    DiseaseAgent,
    WeatherAgent,
    SoilAgent,
    IrrigationAgent,
    SafetyAgent,
    CalendarAgent,
    MemoryAgent
)

# 创建路由器
router = APIRouter()

# 初始化服务
llm_service = LLMService()
db_service = DatabaseService()
location_service = LocationService()
weather_service = WeatherService()
soil_service = SoilService()

# 初始化模型处理器
image_processor = ImageProcessor()
text_processor = TextProcessor()
disease_detector = DiseaseDetector()

# 初始化 Agents
supervisor_agent = SupervisorAgent(llm_service)
disease_agent = DiseaseAgent(llm_service)
weather_agent = WeatherAgent(llm_service)
soil_agent = SoilAgent(llm_service)
irrigation_agent = IrrigationAgent(llm_service)
safety_agent = SafetyAgent(llm_service)
calendar_agent = CalendarAgent(llm_service)
memory_agent = MemoryAgent(llm_service)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    Returns:
        服务状态信息
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.post("/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(
    request: DiagnosisRequest,
    file: Optional[UploadFile] = File(None)
):
    """
    创建诊断请求

    Args:
        request: 诊断请求
        file: 上传的图片文件（可选）

    Returns:
        诊断结果
    """
    try:
        # 获取或创建默认用户
        user = db_service.get_or_create_default_user()

        # 处理位置信息
        location_result = await location_service.resolve_location(
            browser_location=request.browser_location,
            manual_location=request.location,
            client_ip=None  # TODO: 从请求中获取客户端 IP
        )

        latitude = location_result.get("latitude", request.latitude or 0)
        longitude = location_result.get("longitude", request.longitude or 0)
        location = location_result.get("location", request.location or "")

        # 创建诊断记录
        diagnosis_record = db_service.create_diagnosis_record(
            user_id=user.id,
            image_path=None,  # 图片路径稍后更新
            text_input=request.text_input,
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        # 处理图片
        image_analysis = None
        image_path = None
        if file:
            # 保存图片
            image_path = f"uploads/{diagnosis_record.id}_{file.filename}"
            with open(image_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 处理图片
            image_result = await image_processor.process_image(image_path)
            if image_result.get("success"):
                image_analysis = image_result

                # 更新诊断记录的图片路径
                db_service.update_diagnosis_result(
                    diagnosis_record.id,
                    image_path=image_path
                )

        # 处理文本
        text_analysis = None
        if request.text_input:
            text_result = await text_processor.process_text(request.text_input)
            if text_result.get("success"):
                text_analysis = text_result

        # 病虫害识别
        disease_result = await disease_detector.detect(
            image_path or "",
            image_analysis.get("features") if image_analysis else None
        )

        # 构建上下文
        context = {
            "user_id": user.id,
            "image_analysis": image_analysis,
            "text_analysis": text_analysis,
            "text_input": request.text_input,
            "disease_result": disease_result,
            "latitude": latitude,
            "longitude": longitude,
            "location": location
        }

        # 使用 Supervisor Agent 调度任务
        supervisor_result = await supervisor_agent.analyze(context)
        tasks = supervisor_result.get("tasks", [])

        # 准备 Agent 字典
        agents = {
            "disease_agent": disease_agent,
            "weather_agent": weather_agent,
            "soil_agent": soil_agent,
            "irrigation_agent": irrigation_agent,
            "safety_agent": safety_agent,
            "calendar_agent": calendar_agent,
            "memory_agent": memory_agent
        }

        # 执行所有 Agent 分析
        agent_results = await supervisor_agent.dispatch_tasks(tasks, agents, context)

        # 提取各 Agent 结果
        weather_result = agent_results.get("weather_agent", {})
        soil_result = agent_results.get("soil_agent", {})
        irrigation_result = agent_results.get("irrigation_agent", {})
        safety_result = agent_results.get("safety_agent", {})
        calendar_result = agent_results.get("calendar_agent", {})
        memory_result = agent_results.get("memory_agent", {})

        # 更新上下文，添加 Agent 结果
        context.update({
            "weather_data": weather_result.get("weather_data", {}),
            "weather_analysis": weather_result.get("impact_analysis", {}),
            "soil_data": soil_result,
            "irrigation_advice": irrigation_result,
            "safety_advice": safety_result
        })

        # 生成最终建议
        final_advice = await llm_service.generate_final_advice(
            disease_result=disease_result,
            weather_analysis=weather_result.get("impact_analysis", {}),
            soil_analysis=soil_result.get("analysis", {}),
            irrigation_advice=irrigation_result.get("advice", ""),
            safety_advice=safety_result.get("medication_advice", ""),
            calendar_advice=calendar_result.get("farming_calendar", {}),
            user_memory=memory_result.get("personalized_advice", "")
        )

        # 更新诊断记录
        db_service.update_diagnosis_result(
            diagnosis_record.id,
            disease_result=disease_result,
            weather_analysis=weather_result,
            soil_analysis=soil_result,
            irrigation_advice=irrigation_result,
            safety_advice=safety_result,
            calendar_advice=calendar_result,
            final_advice=final_advice
        )

        # 构建响应
        return DiagnosisResponse(
            success=True,
            diagnosis_id=diagnosis_record.id,
            disease_result=DiseaseResult(
                disease_name=disease_result.get("disease_name", "未知"),
                confidence=disease_result.get("confidence", 0),
                symptoms=disease_result.get("symptoms", []),
                is_healthy=disease_result.get("is_healthy", False),
                source=disease_result.get("source", "model")
            ),
            weather_analysis=AgentResult(
                success=weather_result.get("success", False),
                analysis=weather_result.get("impact_analysis", {}).get("analysis"),
                advice=weather_result.get("advice")
            ),
            soil_analysis=AgentResult(
                success=soil_result.get("success", False),
                analysis=soil_result.get("disease_relation"),
                advice=soil_result.get("improvement_advice")
            ),
            irrigation_advice=AgentResult(
                success=irrigation_result.get("success", False),
                analysis=irrigation_result.get("irrigation_needs", {}).get("analysis"),
                advice=irrigation_result.get("advice")
            ),
            safety_advice=AgentResult(
                success=safety_result.get("success", False),
                analysis=safety_result.get("safety_analysis"),
                advice=safety_result.get("medication_advice")
            ),
            calendar_advice=AgentResult(
                success=calendar_result.get("success", False),
                analysis=calendar_result.get("farming_calendar", {}).get("arrangement"),
                advice=calendar_result.get("farming_reminders")
            ),
            memory_analysis=AgentResult(
                success=memory_result.get("success", False),
                analysis=memory_result.get("history_patterns", {}).get("analysis"),
                advice=memory_result.get("personalized_advice")
            ),
            final_advice=final_advice
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/location", response_model=LocationResponse)
async def resolve_location(request: LocationRequest):
    """
    解析位置信息

    Args:
        request: 位置请求

    Returns:
        位置信息
    """
    try:
        browser_location = None
        if request.latitude and request.longitude:
            browser_location = {
                "latitude": request.latitude,
                "longitude": request.longitude
            }

        result = await location_service.resolve_location(
            browser_location=browser_location,
            manual_location=request.location,
            client_ip=request.ip_address
        )

        return LocationResponse(
            success=result.get("success", False),
            location=result.get("location"),
            latitude=result.get("latitude"),
            longitude=result.get("longitude"),
            source=result.get("source"),
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
async def get_diagnosis_history(limit: int = 10):
    """
    获取诊断历史

    Args:
        limit: 返回记录数限制

    Returns:
        历史记录列表
    """
    try:
        user = db_service.get_or_create_default_user()
        records = db_service.get_user_diagnosis_history(user.id, limit)

        history = []
        for record in records:
            history.append({
                "id": record.id,
                "date": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "disease_name": record.disease_result.get("disease_name", "未知") if record.disease_result else "未知",
                "location": record.location,
                "text_input": record.text_input
            })

        return HistoryResponse(
            success=True,
            records=history,
            total=len(history)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile():
    """
    获取用户档案

    Returns:
        用户档案信息
    """
    try:
        user = db_service.get_or_create_default_user()
        profile = memory_agent.get_user_profile(user.id)

        return UserProfileResponse(
            success=True,
            user_info=profile.get("user_info"),
            statistics=profile.get("statistics"),
            recent_diagnoses=profile.get("recent_diagnoses", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diseases")
async def get_supported_diseases():
    """
    获取支持识别的病害列表

    Returns:
        病害列表
    """
    return {
        "success": True,
        "diseases": disease_detector.get_supported_diseases()
    }


@router.get("/model/status")
async def get_model_status():
    """
    获取模型状态

    Returns:
        模型加载状态
    """
    return {
        "success": True,
        "model_loaded": disease_detector.is_model_loaded(),
        "supported_diseases": len(disease_detector.get_supported_diseases())
    }
