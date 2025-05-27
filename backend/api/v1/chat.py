"""
AI社群模拟小游戏 - 聊天API路由
处理聊天消息的发送和获取
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from modules.shared.database import get_db, ChatMessage, User
from modules.ai.chat_handler import ChatHandler

router = APIRouter(prefix="/chat", tags=["chat"])

# 请求/响应模型
class ChatMessageRequest(BaseModel):
    content: str
    sender_type: str = "user"  # "user" 或 "ai"
    sender_name: Optional[str] = "玩家"

class ChatMessageResponse(BaseModel):
    id: int
    content: str
    sender_type: str
    sender_name: str
    timestamp: str
    is_system: bool = False

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int
    page: int
    page_size: int

# 初始化聊天处理器
chat_handler = ChatHandler()

@router.get("/messages", response_model=ChatHistoryResponse)
async def get_chat_messages(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取聊天记录
    
    参数:
    - page: 页码 (从1开始)
    - page_size: 每页消息数量 (默认50)
    
    返回:
    - messages: 聊天消息列表
    - total: 总消息数
    - page: 当前页码
    - page_size: 每页大小
    """
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询消息总数
        total = db.query(ChatMessage).count()
        
        # 查询消息列表 (按时间倒序)
        messages = db.query(ChatMessage)\
                    .order_by(ChatMessage.timestamp.desc())\
                    .offset(offset)\
                    .limit(page_size)\
                    .all()
        
        # 转换为响应格式
        message_list = []
        for msg in reversed(messages):  # 反转顺序，让最新的在前面
            message_list.append(ChatMessageResponse(
                id=msg.id,
                content=msg.content,
                sender_type=msg.sender_type,
                sender_name=msg.sender_name,
                timestamp=msg.timestamp.isoformat(),
                is_system=msg.is_system
            ))
        
        return ChatHistoryResponse(
            messages=message_list,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取聊天记录失败: {str(e)}"
        )

@router.post("/send", response_model=ChatMessageResponse)
async def send_chat_message(
    message_request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    发送聊天消息
    
    参数:
    - content: 消息内容
    - sender_type: 发送者类型 ("user" 或 "ai")
    - sender_name: 发送者名称
    
    返回:
    - 新创建的消息信息
    """
    try:
        # 创建用户消息
        user_message = ChatMessage(
            content=message_request.content,
            sender_type=message_request.sender_type,
            sender_name=message_request.sender_name,
            timestamp=datetime.now(),
            is_system=False
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # 如果是用户消息，生成AI回复
        ai_response = None
        if message_request.sender_type == "user":
            try:
                # 获取AI回复
                ai_content = await chat_handler.generate_response(
                    message_request.content,
                    db
                )
                
                # 创建AI回复消息
                ai_message = ChatMessage(
                    content=ai_content,
                    sender_type="ai",
                    sender_name="AI助手",
                    timestamp=datetime.now(),
                    is_system=False
                )
                
                db.add(ai_message)
                db.commit()
                db.refresh(ai_message)
                
                ai_response = ChatMessageResponse(
                    id=ai_message.id,
                    content=ai_message.content,
                    sender_type=ai_message.sender_type,
                    sender_name=ai_message.sender_name,
                    timestamp=ai_message.timestamp.isoformat(),
                    is_system=ai_message.is_system
                )
                
            except Exception as ai_error:
                print(f"AI回复生成失败: {str(ai_error)}")
                # 即使AI回复失败，也要返回用户消息
        
        # 返回用户消息
        user_response = ChatMessageResponse(
            id=user_message.id,
            content=user_message.content,
            sender_type=user_message.sender_type,
            sender_name=user_message.sender_name,
            timestamp=user_message.timestamp.isoformat(),
            is_system=user_message.is_system
        )
        
        # 如果有AI回复，添加到响应中 (这里简化，只返回用户消息)
        return user_response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"发送消息失败: {str(e)}"
        )

@router.delete("/messages/{message_id}")
async def delete_chat_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    删除聊天消息
    
    参数:
    - message_id: 消息ID
    """
    try:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=404,
                detail="消息不存在"
            )
        
        db.delete(message)
        db.commit()
        
        return {"message": "消息删除成功", "id": message_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除消息失败: {str(e)}"
        )

@router.delete("/messages")
async def clear_chat_history(db: Session = Depends(get_db)):
    """
    清空聊天记录
    """
    try:
        deleted_count = db.query(ChatMessage).delete()
        db.commit()
        
        return {
            "message": "聊天记录清空成功",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"清空聊天记录失败: {str(e)}"
        )

@router.get("/stats")
async def get_chat_stats(db: Session = Depends(get_db)):
    """
    获取聊天统计信息
    """
    try:
        total_messages = db.query(ChatMessage).count()
        user_messages = db.query(ChatMessage).filter(ChatMessage.sender_type == "user").count()
        ai_messages = db.query(ChatMessage).filter(ChatMessage.sender_type == "ai").count()
        
        # 获取最近消息
        recent_message = db.query(ChatMessage)\
                          .order_by(ChatMessage.timestamp.desc())\
                          .first()
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "last_message_time": recent_message.timestamp.isoformat() if recent_message else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取聊天统计失败: {str(e)}"
        ) 