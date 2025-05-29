"""
聊天API - 处理聊天消息和居民对话
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import random
import json

from modules.shared.database import get_db, ChatMessage, Invitation, ExternalUser, CommunityMembership, Agents
from modules.simulation import community_simulation
from modules.llm import response_generator
from modules.ai import enhanced_local_chat, smart_chat_handler

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/messages")
async def get_chat_messages(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取聊天消息列表
    包括用户消息、AI助手消息和居民消息
    """
    try:
        # 从数据库获取聊天消息
        messages = db.query(ChatMessage)\
                    .order_by(ChatMessage.timestamp.desc())\
                    .offset(offset)\
                    .limit(limit)\
                    .all()
        
        # 转换为响应格式
        message_list = []
        for msg in reversed(messages):  # 反转以获得正确的时间顺序
            message_data = {
                "id": msg.id,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "sender": msg.sender_name or "系统",
                "isUser": msg.sender_type == "user",
                "isAI": msg.sender_type == "ai",
                "isAgent": msg.sender_type == "agent",
                "isSystem": msg.sender_type == "system"
            }
            message_list.append(message_data)
        
        return {
            "success": True,
            "data": {
                "messages": message_list,
                "total": len(message_list),
                "has_more": len(messages) == limit
            }
        }
        
    except Exception as e:
        print(f"❌ 获取聊天消息失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取聊天消息失败: {str(e)}",
            "data": {"messages": [], "total": 0, "has_more": False}
        }

@router.post("/send")
async def send_message(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    发送聊天消息并触发AI居民回复
    """
    try:
        message = request.get("message", "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        print(f"📝 收到用户消息: {message}")
        
        # 保存用户消息到数据库
        user_message = ChatMessage(
            content=message,
            sender_type="user",
            sender_name="玩家",
            timestamp=datetime.now()
        )
        db.add(user_message)
        db.commit()
        
        # 初始化AI成员档案（如果还没有初始化）
        if not smart_chat_handler.agent_profiles:
            agents = db.query(Agents).all()
            if agents:
                # 转换为Agent对象
                from modules.simulation import Agent
                agent_objects = []
                for agent_data in agents:
                    agent = Agent(
                        name=agent_data.name,
                        age=agent_data.age,
                        personality=agent_data.personality,
                        occupation=agent_data.occupation,
                        interests=agent_data.interests.split(',') if agent_data.interests else []
                    )
                    # 设置从数据库获取的状态
                    agent.stats.happiness = int(agent_data.happiness)
                    agent.stats.health = int(agent_data.health) 
                    agent.stats.education = int(agent_data.education)
                    agent.stats.wealth = int(agent_data.wealth)
                    agent.stats.social_connections = int(agent_data.social_connections)
                    agent.id = agent_data.agent_id  # 使用数据库中的ID
                    agent_objects.append(agent)
                
                smart_chat_handler.initialize_agent_profiles(agent_objects)
                print(f"✅ 智能聊天系统初始化了 {len(agent_objects)} 个AI成员档案")
        
        # 使用智能聊天处理器生成AI成员回复
        agent_responses = await smart_chat_handler.process_user_message(message, db)
        
        print(f"🤖 生成了 {len(agent_responses)} 个AI成员回复")
        
        # 异步处理AI成员回复
        asyncio.create_task(process_agent_responses(agent_responses, db))
        
        # 生成AI助手回复
        ai_response = await generate_ai_assistant_response(message, db)
        if ai_response:
            # 保存AI助手回复
            ai_message = ChatMessage(
                content=ai_response,
                sender_type="ai",
                sender_name="AI助手",
                timestamp=datetime.now()
            )
            db.add(ai_message)
            db.commit()
            print(f"🤖 AI助手回复: {ai_response}")
        
        return {
            "success": True,
            "message": "消息发送成功",
            "data": {
                "user_message": message,
                "ai_response": ai_response,
                "agent_responses_scheduled": len(agent_responses),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ 发送消息失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

async def process_agent_responses(agent_responses: List[dict], db: Session):
    """异步处理AI成员回复"""
    try:
        for response_data in agent_responses:
            # 等待指定的延迟时间
            delay = response_data.get("delay", 5.0)
            await asyncio.sleep(delay)
            
            # 保存AI成员回复到数据库
            agent_message = ChatMessage(
                content=response_data["response"],
                sender_type="agent",
                sender_name=response_data["agent_name"],
                timestamp=datetime.now()
            )
            
            # 创建新的数据库会话
            from modules.shared.database import SessionLocal
            local_db = SessionLocal()
            try:
                local_db.add(agent_message)
                local_db.commit()
                print(f"👤 {response_data['agent_name']} 回复: {response_data['response']}")
            except Exception as e:
                print(f"❌ 保存 {response_data['agent_name']} 回复失败: {str(e)}")
                local_db.rollback()
            finally:
                local_db.close()
                
    except Exception as e:
        print(f"❌ 处理AI成员回复失败: {str(e)}")

async def generate_ai_assistant_response(user_message: str, db: Session) -> Optional[str]:
    """生成AI助手回复"""
    try:
        # 获取社群统计数据
        agents = db.query(Agents).all()
        if not agents:
            return "欢迎来到AI社群！目前还没有居民数据。"
        
        # 计算统计数据
        total_agents = len(agents)
        avg_happiness = sum(agent.happiness for agent in agents) / total_agents
        avg_health = sum(agent.health for agent in agents) / total_agents
        avg_education = sum(agent.education for agent in agents) / total_agents
        avg_wealth = sum(agent.wealth for agent in agents) / total_agents
        
        community_stats = {
            "population": total_agents,
            "happiness": avg_happiness,
            "health": avg_health,
            "education": avg_education,
            "economy": avg_wealth
        }
        
        # 分析用户消息类型
        message_lower = user_message.lower()
        
        # 根据消息内容生成不同类型的回复
        if any(word in message_lower for word in ["你好", "大家好", "hello", "hi"]):
            responses = [
                f"大家好！欢迎来到我们的AI社群！目前有{total_agents}位居民，大家的整体幸福度是{avg_happiness:.1f}%，让我们一起创造更美好的社群生活吧！",
                f"嗨！很高兴见到你！我们社群现在有{total_agents}位活跃的居民，大家都很友善，快来和他们聊聊吧！",
                f"你好！欢迎加入我们温馨的社群！这里有{total_agents}位有趣的居民，他们会很乐意和你交流的！"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["天气", "今天"]):
            responses = [
                f"今天确实是个好天气！看到大家心情都不错，社群的幸福度达到了{avg_happiness:.1f}%呢！适合多出去走走，和邻居们聊聊天。",
                f"是啊！好天气总是让人心情愉悦。我注意到我们社群的居民们今天都很活跃，这样的日子最适合组织一些户外活动了！",
                f"天气好的时候，社群里的氛围也特别好！大家可以趁着好天气多交流，增进邻里感情。"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["活动", "组织", "聚会"]):
            responses = [
                f"组织活动是个很棒的想法！我们社群有{total_agents}位居民，大家都有不同的兴趣爱好，一定能策划出很有意思的活动。",
                f"太好了！社群活动能大大提升大家的幸福度。目前我们的社群活跃度还不错，相信大家都会积极参与的！",
                f"我支持你的想法！多样化的活动能让社群更有活力，也能让居民们更好地发挥各自的特长。"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["健康", "身体", "运动"]):
            responses = [
                f"健康话题很重要！我们社群的整体健康度是{avg_health:.1f}%，还有提升空间。建议大家多参与运动类活动。",
                f"关注健康是很好的习惯！社群里有医生和其他专业人士，大家可以多交流健康心得。",
                f"身体健康是幸福生活的基础。我们可以组织一些健康主题的活动，让大家一起关注身心健康。"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["学习", "教育", "知识"]):
            responses = [
                f"学习交流很有意义！我们社群的教育水平是{avg_education:.1f}%，大家都很重视知识的积累和分享。",
                f"终身学习的理念很棒！社群里有教师和各行各业的专家，是很好的学习资源。",
                f"知识分享能让整个社群受益。建议可以组织读书会或技能分享活动，大家互相学习。"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["工作", "事业", "职业"]):
            responses = [
                f"工作话题大家都很关心！社群里有各种职业的居民，可以互相交流工作经验和心得。",
                f"职业发展确实重要。我们社群的经济状况是{avg_wealth:.1f}%，大家可以分享一些职场智慧。",
                f"工作和生活的平衡很重要。社群里的朋友们可以互相支持，分享职业发展的经验。"
            ]
            return random.choice(responses)
            
        elif any(word in message_lower for word in ["社群", "社区", "建设"]):
            responses = [
                f"社群建设需要大家共同努力！目前我们有{total_agents}位居民，整体发展还不错，但还有很多可以改进的地方。",
                f"我们的社群就像一个大家庭！每个人的参与都很重要，让我们一起创造更美好的社区环境。",
                f"社区发展离不开每个居民的贡献。大家的想法和建议都很宝贵，欢迎多多交流！"
            ]
            return random.choice(responses)
            
        else:
            # 通用回复
            responses = [
                f"这个话题很有意思！我们社群有{total_agents}位居民，大家都很乐意分享自己的想法和经验。",
                f"感谢你的分享！社群里的讨论总是很精彩，每个人都能从中学到新东西。",
                f"很好的话题！我相信居民们会有很多不同的观点，让我们一起听听大家的想法吧！",
                f"有趣的想法！我们社群鼓励开放的讨论，每个人的声音都很重要。"
            ]
            return random.choice(responses)
            
    except Exception as e:
        print(f"❌ 生成AI助手回复失败: {str(e)}")
        return "很高兴和大家聊天！有什么想法都可以分享哦！"

@router.get("/status")
async def get_chat_status(db: Session = Depends(get_db)):
    """获取聊天系统状态"""
    try:
        # 统计消息数量
        total_messages = db.query(ChatMessage).count()
        user_messages = db.query(ChatMessage).filter(ChatMessage.sender_type == "user").count()
        ai_messages = db.query(ChatMessage).filter(ChatMessage.sender_type == "ai").count()
        agent_messages = db.query(ChatMessage).filter(ChatMessage.sender_type == "agent").count()
        
        # 获取最近活跃的AI成员
        recent_agents = db.query(ChatMessage.sender_name)\
                         .filter(ChatMessage.sender_type == "agent")\
                         .filter(ChatMessage.timestamp > datetime.now() - timedelta(hours=24))\
                         .distinct()\
                         .all()
        
        active_agents = [agent[0] for agent in recent_agents]
        
        return {
            "success": True,
            "data": {
                "total_messages": total_messages,
                "user_messages": user_messages,
                "ai_messages": ai_messages,
                "agent_messages": agent_messages,
                "active_agents": active_agents,
                "active_agent_count": len(active_agents),
                "chat_system_status": "smart_chat" if smart_chat_handler.agent_profiles else "not_initialized"
            }
        }
        
    except Exception as e:
        print(f"❌ 获取聊天状态失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取聊天状态失败: {str(e)}",
            "data": {}
        }