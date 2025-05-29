#!/usr/bin/env python3
"""
数据库初始化脚本
重新创建所有数据库表并插入初始数据
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import (
    Base, engine, SessionLocal,
    CommunityStats, Agents, GameEvents, Event, User, ChatMessage,
    ExternalUser, Invitation, Friendship, CommunityMembership
)

def init_database():
    """初始化数据库"""
    print("🔄 开始初始化数据库...")
    
    try:
        # 删除所有表
        print("📋 删除现有表...")
        Base.metadata.drop_all(bind=engine)
        
        # 创建所有表
        print("🏗️ 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        # 创建数据库会话
        db = SessionLocal()
        
        # 插入初始社群统计数据
        print("📊 插入初始社群统计数据...")
        initial_stats = CommunityStats(
            population=8,
            happiness=60.0,
            health=57.0,
            education=67.0,
            economy=59.0,
            last_updated=datetime.utcnow()
        )
        db.add(initial_stats)
        
        # 插入初始AI居民数据
        print("👥 插入初始AI居民数据...")
        initial_agents = [
            {
                "agent_id": "agent_001",
                "name": "张明",
                "personality": "optimistic",
                "occupation": "teacher",
                "age": 35,
                "interests": '["教育", "阅读", "音乐"]',
                "happiness": 65.0,
                "health": 60.0,
                "education": 85.0,
                "wealth": 55.0,
                "social_connections": 70.0
            },
            {
                "agent_id": "agent_002", 
                "name": "李华",
                "personality": "creative",
                "occupation": "artist",
                "age": 28,
                "interests": '["艺术", "绘画", "设计"]',
                "happiness": 70.0,
                "health": 55.0,
                "education": 75.0,
                "wealth": 45.0,
                "social_connections": 60.0
            },
            {
                "agent_id": "agent_003",
                "name": "王丽", 
                "personality": "analytical",
                "occupation": "doctor",
                "age": 42,
                "interests": '["医学", "研究", "健康"]',
                "happiness": 55.0,
                "health": 80.0,
                "education": 90.0,
                "wealth": 75.0,
                "social_connections": 50.0
            },
            {
                "agent_id": "agent_004",
                "name": "刘强",
                "personality": "leader", 
                "occupation": "engineer",
                "age": 39,
                "interests": '["技术", "创新", "管理"]',
                "happiness": 60.0,
                "health": 65.0,
                "education": 80.0,
                "wealth": 70.0,
                "social_connections": 75.0
            },
            {
                "agent_id": "agent_005",
                "name": "陈静",
                "personality": "social",
                "occupation": "merchant", 
                "age": 31,
                "interests": '["商业", "社交", "旅行"]',
                "happiness": 75.0,
                "health": 50.0,
                "education": 60.0,
                "wealth": 80.0,
                "social_connections": 85.0
            },
            {
                "agent_id": "agent_006",
                "name": "赵勇",
                "personality": "realistic",
                "occupation": "farmer",
                "age": 45,
                "interests": '["农业", "自然", "环保"]',
                "happiness": 50.0,
                "health": 70.0,
                "education": 45.0,
                "wealth": 40.0,
                "social_connections": 55.0
            },
            {
                "agent_id": "agent_007",
                "name": "孙娜",
                "personality": "supporter",
                "occupation": "student",
                "age": 26,
                "interests": '["学习", "志愿服务", "运动"]',
                "happiness": 80.0,
                "health": 75.0,
                "education": 70.0,
                "wealth": 30.0,
                "social_connections": 80.0
            },
            {
                "agent_id": "agent_008",
                "name": "周杰",
                "personality": "introvert",
                "occupation": "researcher",
                "age": 38,
                "interests": '["科研", "编程", "阅读"]',
                "happiness": 45.0,
                "health": 40.0,
                "education": 95.0,
                "wealth": 60.0,
                "social_connections": 30.0
            }
        ]
        
        for agent_data in initial_agents:
            agent = Agents(**agent_data)
            db.add(agent)
        
        # 插入初始聊天消息
        print("💬 插入初始聊天消息...")
        welcome_message = ChatMessage(
            content="欢迎来到AI社群模拟小游戏！我是系统助手，很高兴为您服务。",
            sender_type="system",
            sender_name="系统助手",
            is_system=True,
            timestamp=datetime.utcnow()
        )
        db.add(welcome_message)
        
        # 提交所有更改
        db.commit()
        db.close()
        
        print("✅ 数据库初始化完成！")
        print(f"📊 已创建 {len(initial_agents)} 个AI居民")
        print("🎮 游戏已准备就绪！")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise

def verify_database():
    """验证数据库是否正确创建"""
    print("\n🔍 验证数据库...")
    
    try:
        db = SessionLocal()
        
        # 检查社群统计
        stats = db.query(CommunityStats).first()
        if stats:
            print(f"✅ 社群统计: 人口={stats.population}, 幸福度={stats.happiness}")
        else:
            print("❌ 未找到社群统计数据")
        
        # 检查AI居民
        agents = db.query(Agents).all()
        print(f"✅ AI居民数量: {len(agents)}")
        for agent in agents[:3]:  # 显示前3个
            print(f"   - {agent.name} ({agent.occupation})")
        
        # 检查聊天消息
        messages = db.query(ChatMessage).all()
        print(f"✅ 聊天消息数量: {len(messages)}")
        
        db.close()
        print("✅ 数据库验证通过！")
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {str(e)}")
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 AI社群模拟小游戏 - 数据库初始化")
    print("=" * 50)
    
    init_database()
    verify_database()
    
    print("\n🎉 初始化完成！现在可以启动API服务器了。")
    print("运行命令: python main.py") 