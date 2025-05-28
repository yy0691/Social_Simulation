"""
数据库配置模块
配置SQLite数据库连接和SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 数据库文件路径
DATABASE_URL = "sqlite:///./ai_community_game.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # SQLite特有配置
    echo=False  # 关闭SQL语句显示
)

# 创建Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    """
    获取数据库会话
    用于FastAPI的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    """
    初始化数据库表
    """
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

# 数据库模型定义
class CommunityStats(Base):
    """
    社群统计数据表
    存储社群的实时状态信息
    """
    __tablename__ = "community_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    population = Column(Integer, default=0, comment="社群人口数量")
    happiness = Column(Float, default=50.0, comment="幸福指数(0-100)")
    health = Column(Float, default=50.0, comment="健康度(0-100)")
    education = Column(Float, default=50.0, comment="教育水平(0-100)")
    economy = Column(Float, default=50.0, comment="经济状况(0-100)")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后更新时间")

class Agents(Base):
    """
    AI智能体表
    存储社群中的AI居民信息
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), unique=True, index=True, comment="智能体唯一标识")
    name = Column(String(50), unique=True, index=True, comment="智能体名称")
    personality = Column(String(50), comment="性格类型")
    occupation = Column(String(50), comment="职业")
    age = Column(Integer, comment="年龄")
    interests = Column(Text, comment="兴趣爱好(JSON格式)")
    happiness = Column(Float, default=50.0, comment="快乐度(0-100)")
    health = Column(Float, default=50.0, comment="健康度(0-100)")
    education = Column(Float, default=50.0, comment="教育水平(0-100)")
    wealth = Column(Float, default=50.0, comment="财富(0-100)")
    social_connections = Column(Float, default=50.0, comment="社交关系(0-100)")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    last_active = Column(DateTime, default=datetime.utcnow, comment="最后活跃时间")

# 为兼容性添加别名
Agent = Agents

class GameEvents(Base):
    """
    游戏事件记录表
    存储游戏中发生的各种事件
    """
    __tablename__ = "game_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, comment="事件唯一标识")
    title = Column(String(200), comment="事件标题")
    description = Column(Text, comment="事件详细描述")
    event_type = Column(String(50), index=True, comment="事件类型")
    impact_happiness = Column(Float, default=0.0, comment="对快乐度的影响")
    impact_health = Column(Float, default=0.0, comment="对健康度的影响")
    impact_education = Column(Float, default=0.0, comment="对教育的影响")
    impact_economy = Column(Float, default=0.0, comment="对经济的影响")
    timestamp = Column(DateTime, default=datetime.utcnow, comment="事件发生时间")
    triggered_by = Column(String(50), comment="触发者")
    duration_hours = Column(Float, default=1.0, comment="持续时间(小时)")
    
    def __repr__(self):
        return f"<GameEvent(id={self.event_id}, title={self.title}, type={self.event_type})>"

class Event(Base):
    """
    事件记录表（保留旧版本兼容性）
    存储社群中发生的各种事件
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(30), index=True, comment="事件类型：user_command/ai_action/system_event")
    description = Column(Text, comment="事件详细描述")
    impact = Column(Text, comment="影响数据(JSON格式)")
    timestamp = Column(DateTime, default=datetime.utcnow, comment="事件发生时间")
    
    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, description={self.description})>"

class User(Base):
    """
    用户表
    存储游戏用户信息
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, comment="用户名")
    display_name = Column(String(100), comment="显示名称")
    avatar_url = Column(String(255), comment="头像URL")
    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")
    last_login = Column(DateTime, comment="最后登录时间")
    is_active = Column(Boolean, default=True, comment="是否激活")

class ChatMessage(Base):
    """
    聊天消息表
    存储聊天记录
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, comment="消息内容")
    sender_type = Column(String(20), index=True, comment="发送者类型：user/agent/system")
    sender_name = Column(String(100), comment="发送者名称")
    timestamp = Column(DateTime, default=datetime.utcnow, comment="发送时间")
    is_system = Column(Boolean, default=False, comment="是否为系统消息")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender={self.sender_name}, type={self.sender_type})>"

# 导出所有模型
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    "init_db",
    "CommunityStats",
    "Agent",
    "Agents", 
    "Event",
    "GameEvents",
    "User",
    "ChatMessage"
]