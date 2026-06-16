"""
文件名: init_db.py
功能描述: 数据库初始化脚本，创建表结构和初始数据
作者: ZT
日期: 2026/6/16
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base, User


def init_database():
    """
    初始化数据库
    创建所有表结构
    """
    print("正在初始化数据库...")

    # 创建引擎
    engine = create_engine(DATABASE_URL, echo=True)

    # 创建所有表
    Base.metadata.create_all(engine)

    print("数据库表创建完成！")

    # 创建会话工厂
    Session = sessionmaker(bind=engine)
    session = Session()

    # 检查是否有默认用户，如果没有则创建
    default_user = session.query(User).filter_by(username="default").first()
    if not default_user:
        default_user = User(
            username="default",
            phone="",
            location="",
            latitude=0.0,
            longitude=0.0
        )
        session.add(default_user)
        session.commit()
        print("创建默认用户完成！")

    session.close()
    print("数据库初始化完成！")


if __name__ == "__main__":
    init_database()