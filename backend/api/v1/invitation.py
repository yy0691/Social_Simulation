"""
邀请系统API - 处理社群成员邀请好友功能
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import uuid
import secrets
import string

from modules.shared.database import (
    get_db, 
    Invitation, 
    ExternalUser, 
    Friendship, 
    CommunityMembership,
    Agents,
    ChatMessage
)
from modules.simulation import community_simulation
from modules.llm import response_generator

router = APIRouter(prefix="/invitation", tags=["invitation"])

# 请求模型
class InvitationCreateRequest(BaseModel):
    """创建邀请请求模型"""
    inviter_agent_name: str
    invitee_email: EmailStr
    invitee_name: str
    invitation_message: Optional[str] = "欢迎加入我们的AI社群！"

class InvitationResponseRequest(BaseModel):
    """回应邀请请求模型"""
    invitation_code: str
    response: str  # "accept" 或 "reject"
    response_message: Optional[str] = ""

class FriendshipCreateRequest(BaseModel):
    """建立好友关系请求模型"""
    agent_name_1: str
    agent_name_2: str

# 响应模型
class InvitationResponse(BaseModel):
    """邀请信息响应模型"""
    id: int
    invitation_code: str
    inviter_name: str
    invitee_email: str
    invitee_name: str
    invitation_message: str
    status: str
    expires_at: datetime
    created_at: datetime

def generate_invitation_code() -> str:
    """生成唯一的邀请码"""
    # 生成8位随机字符串
    letters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(letters) for _ in range(8))

@router.post("/send")
async def send_invitation(
    request: InvitationCreateRequest,
    db: Session = Depends(get_db)
):
    """
    社群成员发送邀请给外部好友
    """
    try:
        # 1. 验证邀请者是否为有效的社群成员
        inviter_agent = db.query(Agents).filter(
            Agents.name == request.inviter_agent_name,
            Agents.is_active == True
        ).first()
        
        if not inviter_agent:
            raise HTTPException(status_code=404, detail=f"未找到社群成员: {request.inviter_agent_name}")
        
        # 2. 检查是否已经存在待处理的邀请
        existing_invitation = db.query(Invitation).filter(
            Invitation.inviter_agent_id == inviter_agent.agent_id,
            Invitation.invitee_email == request.invitee_email,
            Invitation.status == "pending"
        ).first()
        
        if existing_invitation:
            raise HTTPException(status_code=400, detail="已经存在待处理的邀请")
        
        # 3. 创建或更新外部用户记录
        external_user = db.query(ExternalUser).filter(
            ExternalUser.email == request.invitee_email
        ).first()
        
        if not external_user:
            external_user = ExternalUser(
                email=request.invitee_email,
                name=request.invitee_name,
                status="pending"
            )
            db.add(external_user)
        else:
            external_user.name = request.invitee_name
            external_user.status = "invited"
            external_user.last_updated = datetime.utcnow()
        
        # 4. 创建邀请记录
        invitation_code = generate_invitation_code()
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7天后过期
        
        invitation = Invitation(
            invitation_code=invitation_code,
            inviter_agent_id=inviter_agent.agent_id,
            inviter_name=inviter_agent.name,
            invitee_email=request.invitee_email,
            invitee_name=request.invitee_name,
            invitation_message=request.invitation_message,
            status="pending",
            expires_at=expires_at
        )
        
        db.add(invitation)
        db.commit()
        
        # 5. 生成AI居民的邀请消息并发送到聊天室
        await send_invitation_to_chat(inviter_agent, request, invitation_code, db)
        
        return {
            "success": True,
            "message": "邀请发送成功",
            "data": {
                "invitation_code": invitation_code,
                "inviter_name": inviter_agent.name,
                "invitee_name": request.invitee_name,
                "expires_at": expires_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发送邀请失败: {str(e)}")

@router.get("/list")
async def get_invitations(
    agent_name: Optional[str] = Query(None, description="按邀请者筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    limit: int = Query(20, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    获取邀请列表
    """
    try:
        query = db.query(Invitation)
        
        if agent_name:
            query = query.filter(Invitation.inviter_name == agent_name)
        
        if status:
            query = query.filter(Invitation.status == status)
        
        invitations = query.order_by(Invitation.created_at.desc()).limit(limit).all()
        
        invitation_list = []
        for inv in invitations:
            invitation_list.append({
                "id": inv.id,
                "invitation_code": inv.invitation_code,
                "inviter_name": inv.inviter_name,
                "invitee_email": inv.invitee_email,
                "invitee_name": inv.invitee_name,
                "invitation_message": inv.invitation_message,
                "status": inv.status,
                "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                "created_at": inv.created_at.isoformat(),
                "responded_at": inv.responded_at.isoformat() if inv.responded_at else None
            })
        
        return {
            "success": True,
            "data": {
                "invitations": invitation_list,
                "total": len(invitation_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取邀请列表失败: {str(e)}")

@router.post("/respond")
async def respond_to_invitation(
    request: InvitationResponseRequest,
    db: Session = Depends(get_db)
):
    """
    回应邀请（接受或拒绝）
    """
    try:
        # 1. 查找邀请记录
        invitation = db.query(Invitation).filter(
            Invitation.invitation_code == request.invitation_code,
            Invitation.status == "pending"
        ).first()
        
        if not invitation:
            raise HTTPException(status_code=404, detail="邀请不存在或已过期")
        
        # 2. 检查邀请是否过期
        if invitation.expires_at and datetime.utcnow() > invitation.expires_at:
            invitation.status = "expired"
            db.commit()
            raise HTTPException(status_code=400, detail="邀请已过期")
        
        # 3. 更新邀请状态
        if request.response.lower() == "accept":
            invitation.status = "accepted"
            
            # 创建社群成员记录
            membership = CommunityMembership(
                member_id=f"human_{invitation.invitee_email}",
                member_name=invitation.invitee_name,
                member_type="human",
                status="active",
                join_method="invitation",
                invited_by=invitation.inviter_agent_id
            )
            db.add(membership)
            
            # 更新外部用户状态
            external_user = db.query(ExternalUser).filter(
                ExternalUser.email == invitation.invitee_email
            ).first()
            if external_user:
                external_user.status = "joined"
            
            # 在聊天室发送欢迎消息
            await send_welcome_message(invitation, db)
            
            response_message = f"{invitation.invitee_name} 已接受邀请，加入了社群！"
            
        elif request.response.lower() == "reject":
            invitation.status = "rejected"
            response_message = f"{invitation.invitee_name} 已拒绝邀请"
        else:
            raise HTTPException(status_code=400, detail="无效的回应类型")
        
        invitation.responded_at = datetime.utcnow()
        db.commit()
        
        # 通知邀请者
        await notify_inviter_about_response(invitation, request.response, db)
        
        return {
            "success": True,
            "message": response_message,
            "data": {
                "invitation_code": invitation.invitation_code,
                "status": invitation.status,
                "responded_at": invitation.responded_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理邀请回应失败: {str(e)}")

@router.get("/check/{invitation_code}")
async def check_invitation(
    invitation_code: str,
    db: Session = Depends(get_db)
):
    """
    检查邀请状态
    """
    try:
        invitation = db.query(Invitation).filter(
            Invitation.invitation_code == invitation_code
        ).first()
        
        if not invitation:
            raise HTTPException(status_code=404, detail="邀请不存在")
        
        # 检查是否过期
        is_expired = False
        if invitation.expires_at and datetime.utcnow() > invitation.expires_at:
            is_expired = True
            if invitation.status == "pending":
                invitation.status = "expired"
                db.commit()
        
        return {
            "success": True,
            "data": {
                "invitation_code": invitation.invitation_code,
                "inviter_name": invitation.inviter_name,
                "invitee_name": invitation.invitee_name,
                "invitation_message": invitation.invitation_message,
                "status": invitation.status,
                "is_expired": is_expired,
                "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None,
                "created_at": invitation.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查邀请状态失败: {str(e)}")

@router.post("/friendship/create")
async def create_friendship(
    request: FriendshipCreateRequest,
    db: Session = Depends(get_db)
):
    """
    在两个社群成员之间建立好友关系
    """
    try:
        # 验证两个成员都存在
        agent1 = db.query(Agents).filter(Agents.name == request.agent_name_1).first()
        agent2 = db.query(Agents).filter(Agents.name == request.agent_name_2).first()
        
        if not agent1 or not agent2:
            raise HTTPException(status_code=404, detail="其中一个或两个成员不存在")
        
        if agent1.agent_id == agent2.agent_id:
            raise HTTPException(status_code=400, detail="不能与自己建立好友关系")
        
        # 检查是否已存在好友关系
        existing_friendship = db.query(Friendship).filter(
            ((Friendship.agent_id_1 == agent1.agent_id) & (Friendship.agent_id_2 == agent2.agent_id)) |
            ((Friendship.agent_id_1 == agent2.agent_id) & (Friendship.agent_id_2 == agent1.agent_id))
        ).first()
        
        if existing_friendship:
            raise HTTPException(status_code=400, detail="好友关系已存在")
        
        # 创建好友关系
        friendship = Friendship(
            agent_id_1=agent1.agent_id,
            agent_name_1=agent1.name,
            agent_id_2=agent2.agent_id,
            agent_name_2=agent2.name,
            friendship_level=75.0,  # 初始友谊等级
            status="active"
        )
        
        db.add(friendship)
        db.commit()
        
        # 在聊天室发送好友建立消息
        await announce_new_friendship(agent1, agent2, db)
        
        return {
            "success": True,
            "message": f"{agent1.name} 和 {agent2.name} 已成为好友",
            "data": {
                "friendship_id": friendship.id,
                "agent_name_1": friendship.agent_name_1,
                "agent_name_2": friendship.agent_name_2,
                "friendship_level": friendship.friendship_level
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"建立好友关系失败: {str(e)}")

@router.get("/friendships")
async def get_friendships(
    agent_name: Optional[str] = Query(None, description="查看特定成员的好友"),
    db: Session = Depends(get_db)
):
    """
    获取好友关系列表
    """
    try:
        query = db.query(Friendship).filter(Friendship.status == "active")
        
        if agent_name:
            query = query.filter(
                (Friendship.agent_name_1 == agent_name) | 
                (Friendship.agent_name_2 == agent_name)
            )
        
        friendships = query.order_by(Friendship.established_at.desc()).all()
        
        friendship_list = []
        for friendship in friendships:
            friendship_list.append({
                "id": friendship.id,
                "agent_name_1": friendship.agent_name_1,
                "agent_name_2": friendship.agent_name_2,
                "friendship_level": friendship.friendship_level,
                "established_at": friendship.established_at.isoformat(),
                "last_interaction": friendship.last_interaction.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "friendships": friendship_list,
                "total": len(friendship_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取好友关系失败: {str(e)}")

@router.get("/members")
async def get_community_members(
    member_type: Optional[str] = Query(None, description="按成员类型筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取社群成员列表
    """
    try:
        query = db.query(CommunityMembership)
        
        if member_type:
            query = query.filter(CommunityMembership.member_type == member_type)
        
        if status:
            query = query.filter(CommunityMembership.status == status)
        
        members = query.order_by(CommunityMembership.joined_at.desc()).all()
        
        member_list = []
        for member in members:
            member_list.append({
                "id": member.id,
                "member_id": member.member_id,
                "member_name": member.member_name,
                "member_type": member.member_type,
                "status": member.status,
                "join_method": member.join_method,
                "invited_by": member.invited_by,
                "joined_at": member.joined_at.isoformat(),
                "last_active": member.last_active.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "members": member_list,
                "total": len(member_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员列表失败: {str(e)}")

# 辅助函数
async def send_invitation_to_chat(agent, request, invitation_code, db: Session):
    """发送邀请消息到聊天室"""
    try:
        invitation_message = f"我想邀请我的好友 {request.invitee_name} 加入我们的社群！邀请码是：{invitation_code}。{request.invitation_message}"
        
        chat_message = ChatMessage(
            content=invitation_message,
            sender_type="agent",
            sender_name=agent.name,
            timestamp=datetime.utcnow()
        )
        
        db.add(chat_message)
        db.commit()
        
        print(f"✅ {agent.name} 发送了邀请消息到聊天室")
        
    except Exception as e:
        print(f"❌ 发送邀请消息失败: {str(e)}")

async def send_welcome_message(invitation, db: Session):
    """发送欢迎新成员的消息"""
    try:
        welcome_message = f"🎉 欢迎 {invitation.invitee_name} 加入我们的AI社群！感谢 {invitation.inviter_name} 的邀请。"
        
        system_message = ChatMessage(
            content=welcome_message,
            sender_type="system",
            sender_name="系统消息",
            timestamp=datetime.utcnow(),
            is_system=True
        )
        
        db.add(system_message)
        db.commit()
        
        print(f"✅ 发送了欢迎 {invitation.invitee_name} 的消息")
        
    except Exception as e:
        print(f"❌ 发送欢迎消息失败: {str(e)}")

async def notify_inviter_about_response(invitation, response, db: Session):
    """通知邀请者关于邀请回应"""
    try:
        if response.lower() == "accept":
            notify_message = f"好消息！{invitation.invitee_name} 接受了我的邀请，已经加入了我们的社群！"
        else:
            notify_message = f"{invitation.invitee_name} 暂时无法加入我们的社群，但我会继续邀请其他朋友的。"
        
        notification = ChatMessage(
            content=notify_message,
            sender_type="agent",
            sender_name=invitation.inviter_name,
            timestamp=datetime.utcnow()
        )
        
        db.add(notification)
        db.commit()
        
        print(f"✅ 通知了 {invitation.inviter_name} 关于邀请回应")
        
    except Exception as e:
        print(f"❌ 发送通知消息失败: {str(e)}")

async def announce_new_friendship(agent1, agent2, db: Session):
    """宣布新的好友关系"""
    try:
        announcement = f"🤝 {agent1.name} 和 {agent2.name} 成为了好朋友！我们的社群关系更加紧密了。"
        
        system_message = ChatMessage(
            content=announcement,
            sender_type="system", 
            sender_name="系统消息",
            timestamp=datetime.utcnow(),
            is_system=True
        )
        
        db.add(system_message)
        db.commit()
        
        print(f"✅ 宣布了 {agent1.name} 和 {agent2.name} 的好友关系")
        
    except Exception as e:
        print(f"❌ 发送好友关系宣布失败: {str(e)}") 