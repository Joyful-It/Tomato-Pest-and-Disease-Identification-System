"""
文件名: database_service.py
功能描述: 数据库服务封装，提供数据访问接口
作者: ZT
日期: 2026/6/16
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL
from database.models import User, DiagnosisRecord, UserMemory


class DatabaseService:
    """
    数据库服务类
    封装数据库操作，提供统一的数据访问接口
    """

    def __init__(self):
        """初始化数据库服务"""
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    # ==================== 用户相关操作 ====================

    def get_user(self, user_id: int) -> Optional[User]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户对象或 None
        """
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def get_or_create_default_user(self) -> User:
        """
        获取或创建默认用户

        Returns:
            用户对象
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == "default").first()
            if not user:
                user = User(
                    username="default",
                    phone="",
                    location="",
                    latitude=0.0,
                    longitude=0.0
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def update_user_location(
        self,
        user_id: int,
        location: str,
        latitude: float,
        longitude: float
    ) -> bool:
        """
        更新用户位置信息

        Args:
            user_id: 用户ID
            location: 位置描述
            latitude: 纬度
            longitude: 经度

        Returns:
            是否更新成功
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.location = location
                user.latitude = latitude
                user.longitude = longitude
                user.updated_at = datetime.now()
                session.commit()
                return True
            return False
        finally:
            session.close()

    # ==================== 诊断记录相关操作 ====================

    def create_diagnosis_record(
        self,
        user_id: int,
        image_path: Optional[str] = None,
        text_input: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> DiagnosisRecord:
        """
        创建诊断记录

        Args:
            user_id: 用户ID
            image_path: 图片路径
            text_input: 文字输入
            location: 位置
            latitude: 纬度
            longitude: 经度

        Returns:
            诊断记录对象
        """
        session = self.get_session()
        try:
            record = DiagnosisRecord(
                user_id=user_id,
                image_path=image_path,
                text_input=text_input,
                location=location,
                latitude=latitude,
                longitude=longitude
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        finally:
            session.close()

    def update_diagnosis_result(
        self,
        record_id: int,
        **kwargs
    ) -> bool:
        """
        更新诊断结果

        Args:
            record_id: 记录ID
            **kwargs: 要更新的字段和值

        Returns:
            是否更新成功
        """
        session = self.get_session()
        try:
            record = session.query(DiagnosisRecord).filter(
                DiagnosisRecord.id == record_id
            ).first()
            if record:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_user_diagnosis_history(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[DiagnosisRecord]:
        """
        获取用户诊断历史

        Args:
            user_id: 用户ID
            limit: 返回记录数限制

        Returns:
            诊断记录列表
        """
        session = self.get_session()
        try:
            return session.query(DiagnosisRecord)\
                .filter(DiagnosisRecord.user_id == user_id)\
                .order_by(DiagnosisRecord.created_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    # ==================== 用户记忆相关操作 ====================

    def add_user_memory(
        self,
        user_id: int,
        memory_type: str,
        content: str,
        extra_data: Optional[Dict] = None
    ) -> UserMemory:
        """
        添加用户记忆

        Args:
            user_id: 用户ID
            memory_type: 记忆类型
            content: 记忆内容
            extra_data: 元数据

        Returns:
            记忆对象
        """
        session = self.get_session()
        try:
            memory = UserMemory(
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                extra_data=extra_data or {}
            )
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory
        finally:
            session.close()

    def get_user_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        limit: int = 20
    ) -> List[UserMemory]:
        """
        获取用户记忆

        Args:
            user_id: 用户ID
            memory_type: 记忆类型过滤
            limit: 返回记录数限制

        Returns:
            记忆列表
        """
        session = self.get_session()
        try:
            query = session.query(UserMemory).filter(UserMemory.user_id == user_id)
            if memory_type:
                query = query.filter(UserMemory.memory_type == memory_type)
            return query.order_by(UserMemory.created_at.desc()).limit(limit).all()
        finally:
            session.close()

    def get_user_memory_summary(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户记忆摘要

        Args:
            user_id: 用户ID

        Returns:
            记忆摘要字典
        """
        memories = self.get_user_memories(user_id, limit=50)

        summary = {
            "total_memories": len(memories),
            "preferences": [],
            "history": [],
            "knowledge": []
        }

        for memory in memories:
            if memory.memory_type == "preference":
                summary["preferences"].append(memory.content)
            elif memory.memory_type == "history":
                summary["history"].append(memory.content)
            elif memory.memory_type == "knowledge":
                summary["knowledge"].append(memory.content)

        return summary