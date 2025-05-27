"""
数据库初始化脚本
创建表并填充初始测试数据
"""

from .database import init_db, SessionLocal, CommunityStats, Agents, Events
from datetime import datetime

def create_initial_data():
    """
    创建初始测试数据
    """
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_stats = db.query(CommunityStats).first()
        if existing_stats:
            print("数据库已有数据，跳过初始化")
            return
        
        # 1. 创建初始社群统计数据
        initial_stats = CommunityStats(
            population=3,
            happiness_level=75.0,
            activity_level=85.0
        )
        db.add(initial_stats)
        
        # 2. 创建初始AI居民
        agents_data = [
            {
                "name": "居民A",
                "personality": "性格开朗活泼，喜欢社交和组织活动，是社群的快乐源泉",
                "mood": 80.0,
                "status": "active",
                "last_action": "正在准备篝火晚会的零食"
            },
            {
                "name": "居民B",
                "personality": "热爱音乐和舞蹈，富有艺术天赋，经常为大家带来娱乐",
                "mood": 75.0,
                "status": "active", 
                "last_action": "在为篝火晚会准备音乐"
            },
            {
                "name": "居民C",
                "personality": "温和友善，善于倾听和帮助他人，是社群的和谐使者",
                "mood": 70.0,
                "status": "active",
                "last_action": "帮助其他居民解决生活中的小问题"
            }
        ]
        
        for agent_data in agents_data:
            agent = Agents(**agent_data)
            db.add(agent)
        
        # 3. 创建初始事件记录
        events_data = [
            {
                "event_type": "user_command",
                "title": "玩家发起了一场篝火晚会",
                "description": "玩家输入指令，要求社群居民组织一场温馨的篝火晚会",
                "participants": '["居民A", "居民B", "居民C"]',
                "impact_happiness": 15.0,
                "impact_activity": 10.0
            },
            {
                "event_type": "ai_action",
                "title": "社群活跃度提升了10点",
                "description": "由于篝火晚会的举办，整个社群的活跃度显著提升",
                "participants": '["系统"]',
                "impact_happiness": 5.0,
                "impact_activity": 10.0
            },
            {
                "event_type": "system_event",
                "title": "新成员加入了社群",
                "description": "社群的良好氛围吸引了新的居民加入",
                "participants": '["新居民"]',
                "impact_happiness": 3.0,
                "impact_activity": 5.0
            }
        ]
        
        for event_data in events_data:
            event = Events(**event_data)
            db.add(event)
        
        # 提交所有更改
        db.commit()
        print("✅ 初始测试数据创建成功！")
        print(f"   - 社群统计: 人口{initial_stats.population}, 幸福度{initial_stats.happiness_level}%, 活跃度{initial_stats.activity_level}%")
        print(f"   - AI居民: {len(agents_data)}位")
        print(f"   - 历史事件: {len(events_data)}条")
        
    except Exception as e:
        print(f"❌ 初始化数据时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

def reset_database():
    """
    重置数据库（清空所有数据）
    """
    db = SessionLocal()
    
    try:
        # 清空所有表
        db.query(Events).delete()
        db.query(Agents).delete()
        db.query(CommunityStats).delete()
        db.commit()
        print("✅ 数据库已重置")
        
        # 重新创建初始数据
        create_initial_data()
        
    except Exception as e:
        print(f"❌ 重置数据库时发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 初始化数据库表
    init_db()
    
    # 创建初始数据
    create_initial_data() 