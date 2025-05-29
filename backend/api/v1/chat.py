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

# 添加全局状态跟踪
active_generations = {}  # 跟踪正在生成回复的AI居民

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
    发送聊天消息并触发AI居民回复 - 优化：立即响应，异步处理
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
        
        # 快速生成AI助手回复（简化版，不依赖社群数据）
        ai_response = generate_quick_ai_response(message)
        if ai_response:
            ai_message = ChatMessage(
                content=ai_response,
                sender_type="ai",
                sender_name="AI助手",
                timestamp=datetime.now()
            )
            db.add(ai_message)
            db.commit()
            print(f"🤖 AI助手快速回复: {ai_response}")
        
        # 立即启动异步AI居民处理（不等待）
        asyncio.create_task(process_ai_residents_async(message, db))
        
        # 立即返回响应，不等待AI居民处理完成
        return {
            "success": True,
            "message": "消息发送成功",
            "data": {
                "user_message": message,
                "ai_response": ai_response,
                "agents_processing": "异步处理中...",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ 发送消息失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

def generate_quick_ai_response(message: str) -> str:
    """生成快速AI助手回复，不依赖复杂的社群数据查询"""
    message_lower = message.lower()
    
    # 基于关键词的快速回复
    if any(word in message_lower for word in ["你好", "大家好", "hello", "hi"]):
        responses = [
            "大家好！欢迎来到AI社群聊天室！居民们马上就会来和你聊天的！",
            "嗨！很高兴见到你！让我们等等看居民们会怎么回应吧！",
            "你好！欢迎来到这个温馨的社群！"
        ]
        return random.choice(responses)
    
    elif any(word in message_lower for word in ["怎么样", "如何", "建议"]):
        responses = [
            "这是个很好的问题！居民们可能会有不同的见解。",
            "让我们听听大家的想法和经验分享吧！",
            "相信居民们会给出很好的建议！"
        ]
        return random.choice(responses)
    
    elif any(word in message_lower for word in ["分享", "聊聊", "讨论"]):
        responses = [
            "很棒的话题！大家一定很乐意分享自己的想法。",
            "这种交流很有意义！期待听到大家的分享。",
            "好主意！让我们一起来讨论这个话题吧！"
        ]
        return random.choice(responses)
    
    else:
        responses = [
            "有意思的话题！让我们看看居民们会怎么回应。",
            "这个问题很不错！居民们应该会有很多想法。",
            "期待听到大家的不同观点！"
        ]
        return random.choice(responses)

async def process_ai_residents_async(message: str, db: Session):
    """异步处理AI居民回复 - 重新设计：并行生成+实时流式传输"""
    try:
        # 初始化AI成员档案（如果需要）
        if not smart_chat_handler.agent_profiles:
            agents = db.query(Agents).all()
            if agents:
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
                    agent.stats.happiness = int(agent_data.happiness)
                    agent.stats.health = int(agent_data.health) 
                    agent.stats.education = int(agent_data.education)
                    agent.stats.wealth = int(agent_data.wealth)
                    agent.stats.social_connections = int(agent_data.social_connections)
                    agent.id = agent_data.agent_id
                    agent_objects.append(agent)
                
                smart_chat_handler.initialize_agent_profiles(agent_objects)
                print(f"✅ 智能聊天系统初始化了 {len(agent_objects)} 个AI成员档案")
        
        # 获取参与对话的居民（不生成LLM，只是准备参数）
        participating_agents = await smart_chat_handler.get_participating_agents_info(message, db)
        print(f"🎭 选择了 {len(participating_agents)} 个AI居民参与对话")
        
        # 立即为每个居民启动独立的生成和流式传输任务
        tasks = []
        for agent_info in participating_agents:
            # 为每个居民创建完全独立的异步任务
            task = asyncio.create_task(
                process_single_agent_realtime(agent_info, message, db)
            )
            tasks.append(task)
            
        # 不等待任务完成，让它们完全并行运行
        # 每个居民将独立生成LLM并实时流式传输
        asyncio.gather(*tasks, return_exceptions=True)
        
    except Exception as e:
        print(f"❌ 异步处理AI居民回复失败: {str(e)}")

async def process_single_agent_realtime(agent_info: dict, user_message: str, db: Session):
    """单个AI居民的实时生成和流式传输"""
    agent_name = agent_info["agent_name"]
    
    try:
        # 立即标记该居民开始生成
        active_generations[agent_name] = {
            "status": "generating",
            "start_time": datetime.now().isoformat(),
            "content": "",
            "progress": 0.0,
            "is_streaming": False
        }
        print(f"🎭 {agent_name} 开始实时生成回复...")
        
        # 短暂的个性化延迟
        delay = agent_info.get("delay", 0.5)
        await asyncio.sleep(min(delay, 2.0))
        
        # 立即切换到流式传输状态
        active_generations[agent_name]["status"] = "streaming"
        active_generations[agent_name]["is_streaming"] = True
        print(f"📡 {agent_name} 开始实时LLM生成和流式传输")
        
        # 实时调用LLM生成，边生成边流式传输
        await generate_and_stream_llm_response(agent_name, agent_info, user_message, db)
        
    except Exception as e:
        print(f"❌ {agent_name} 实时处理失败: {str(e)}")
        if agent_name in active_generations:
            active_generations[agent_name]["status"] = "error"
            active_generations[agent_name]["error"] = str(e)

async def generate_and_stream_llm_response(agent_name: str, agent_info: dict, user_message: str, db: Session):
    """实时生成LLM回复并流式传输"""
    try:
        # 使用smart_chat_handler实时生成LLM回复
        llm_response = await smart_chat_handler.generate_single_agent_response(
            agent_info, user_message, db
        )
        
        if not llm_response:
            print(f"❌ {agent_name} LLM生成失败")
            active_generations[agent_name]["status"] = "error"
            return
            
        print(f"✅ {agent_name} LLM生成成功，开始逐字符流式传输")
        
        # 立即开始逐字符流式传输
        full_response = llm_response["response"]
        
        # 模拟真实的逐字符生成过程
        for i, char in enumerate(full_response):
            if agent_name not in active_generations:
                break
                
            # 实时更新当前内容
            active_generations[agent_name]["content"] += char
            active_generations[agent_name]["current_pos"] = i + 1
            active_generations[agent_name]["progress"] = (i + 1) / len(full_response)
            
            # 模拟打字速度
            char_delay = 0.02 + (0.01 * (1 if char in '，。！？' else 0.5))
            await asyncio.sleep(char_delay)
            
        # 流式传输完成，保存到数据库
        agent_message = ChatMessage(
            content=full_response,
            sender_type="agent",
            sender_name=agent_name,
            timestamp=datetime.now()
        )
        
        # 创建新的数据库会话
        from modules.shared.database import SessionLocal
        local_db = SessionLocal()
        try:
            local_db.add(agent_message)
            local_db.commit()
            print(f"💾 {agent_name} 回复已保存到数据库")
            
            # 标记完成
            active_generations[agent_name] = {
                "status": "completed",
                "start_time": active_generations[agent_name]["start_time"],
                "content": full_response,
                "progress": 1.0,
                "completed_time": datetime.now().isoformat()
            }
            
            # 3秒后清理状态
            asyncio.create_task(cleanup_generation_status(agent_name, 3.0))
            
        except Exception as e:
            print(f"❌ 保存 {agent_name} 回复失败: {str(e)}")
            local_db.rollback()
            active_generations[agent_name]["status"] = "error"
        finally:
            local_db.close()
            
    except Exception as e:
        print(f"❌ {agent_name} LLM生成和流式传输失败: {str(e)}")
        if agent_name in active_generations:
            active_generations[agent_name]["status"] = "error"

async def cleanup_generation_status(agent_name: str, delay: float):
    """清理生成状态"""
    await asyncio.sleep(delay)
    if agent_name in active_generations:
        del active_generations[agent_name]
        print(f"🧹 清理了 {agent_name} 的生成状态")

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

@router.get("/agent-status")
async def get_agent_status():
    """获取AI居民回复状态"""
    return {
        "success": True,
        "data": {
            "active_generations": active_generations,
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/stream/{agent_name}")
async def stream_agent_response(agent_name: str, db: Session = Depends(get_db)):
    """真正的实时流式传输AI居民回复"""
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    print(f"🎬 收到 {agent_name} 的流式传输请求")
    
    async def generate_stream():
        last_pos = 0
        wait_count = 0
        max_wait = 150  # 增加等待时间到15秒
        sent_waiting = False
        
        try:
            while wait_count < max_wait:
                # 检查该居民是否有正在生成的回复
                if agent_name in active_generations:
                    generation_info = active_generations[agent_name]
                    current_content = generation_info.get("content", "")
                    status = generation_info.get("status", "")
                    
                    print(f"📊 {agent_name} 状态: {status}, 内容长度: {len(current_content)}")
                    
                    # 如果有新内容需要传输
                    if len(current_content) > last_pos:
                        new_chars = current_content[last_pos:]
                        
                        # 逐字符发送新内容
                        for i, char in enumerate(new_chars):
                            chunk_data = {
                                "type": "content",
                                "char": char,
                                "progress": generation_info.get("progress", 0),
                                "agent_name": agent_name,
                                "total_length": len(current_content)
                            }
                            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                            await asyncio.sleep(0.01)  # 很短的延迟，保证顺序
                        
                        last_pos = len(current_content)
                    
                    # 检查是否完成
                    if status == "completed":
                        print(f"✅ {agent_name} 流式传输完成")
                        yield f"data: {json.dumps({'type': 'complete', 'agent_name': agent_name}, ensure_ascii=False)}\n\n"
                        break
                    elif status == "error":
                        print(f"❌ {agent_name} 生成出错")
                        yield f"data: {json.dumps({'type': 'error', 'agent_name': agent_name}, ensure_ascii=False)}\n\n"
                        break
                        
                else:
                    # 如果还没有开始生成，发送等待信号（只发送一次）
                    if not sent_waiting:
                        print(f"⏳ {agent_name} 等待开始生成...")
                        yield f"data: {json.dumps({'type': 'waiting', 'agent_name': agent_name}, ensure_ascii=False)}\n\n"
                        sent_waiting = True
                
                wait_count += 1
                await asyncio.sleep(0.1)  # 100ms检查一次新内容
            
            # 超时处理
            if wait_count >= max_wait:
                print(f"⏰ {agent_name} 流式传输超时")
                yield f"data: {json.dumps({'type': 'timeout', 'agent_name': agent_name}, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            print(f"❌ {agent_name} 流式传输异常: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'agent_name': agent_name, 'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
            "X-Accel-Buffering": "no"  # 禁用nginx缓冲，提高实时性
        }
    )