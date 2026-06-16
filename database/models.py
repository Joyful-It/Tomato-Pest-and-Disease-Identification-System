"""
文件名: models.py
功能描述: 数据库模型定义，包含用户、诊断记录、记忆等表结构
作者: ZT
日期: 2026/6/16
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 创建基类
Base = declarative_base()


class User(Base):
    """
    用户模型
    存储农户的基本信息和档案
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(100), unique=True, nullable=False, comment="用户名")
    phone = Column(String(20), nullable=True, comment="手机号")
    location = Column(String(200), nullable=True, comment="默认位置（省市区）")
    latitude = Column(Float, nullable=True, comment="纬度")
    longitude = Column(Float, nullable=True, comment="经度")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    diagnoses = relationship("DiagnosisRecord", back_populates="user", lazy="dynamic")
    memories = relationship("UserMemory", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class DiagnosisRecord(Base):
    """
    诊断记录模型
    存储每次病虫害诊断的详细信息
    """
    __tablename__ = "diagnosis_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    image_path = Column(String(500), nullable=True, comment="上传图片路径")
    text_input = Column(Text, nullable=True, comment="用户文字描述")
    disease_result = Column(JSON, nullable=True, comment="病虫害识别结果")
    weather_analysis = Column(JSON, nullable=True, comment="天气分析结果")
    soil_analysis = Column(JSON, nullable=True, comment="土壤分析结果")
    irrigation_advice = Column(JSON, nullable=True, comment="灌溉建议")
    safety_advice = Column(JSON, nullable=True, comment="安全用药建议")
    calendar_advice = Column(JSON, nullable=True, comment="种植日历建议")
    final_advice = Column(Text, nullable=True, comment="最终综合建议")
    location = Column(String(200), nullable=True, comment="诊断时位置")
    latitude = Column(Float, nullable=True, comment="诊断时纬度")
    longitude = Column(Float, nullable=True, comment="诊断时经度")
    created_at = Column(DateTime, default=datetime.now, comment="诊断时间")

    # 关联关系
    user = relationship("User", back_populates="diagnoses")

    def __repr__(self):
        return f"<DiagnosisRecord(id={self.id}, user_id={self.user_id})>"


class UserMemory(Base):
    """
    用户记忆模型
    存储用户的长期记忆和偏好
    """
    __tablename__ = "user_memories"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记忆ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    memory_type = Column(String(50), nullable=False, comment="记忆类型：preference/history/knowledge")
    content = Column(Text, nullable=False, comment="记忆内容")
    metadata = Column(JSON, nullable=True, comment="元数据")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="memories")

    def __repr__(self):
        return f"<UserMemory(id={self.id}, type='{self.memory_type}')>"