from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import json
from modules.shared.database import get_db, CommunityStats, Event

router = APIRouter(tags=["commands"])

class CommandRequest(BaseModel):
    command: str
    description: str = ""

@router.post("/commands/execute")
async def execute_command(request: CommandRequest, db: Session = Depends(get_db)):
    """执行玩家指令"""
    command = request.command.lower().strip()
    
    # 智能解析指令类型
    impact_type = "neutral"
    happiness_change = 0
    activity_change = 0
    
    positive_keywords = ["聚会", "庆祝", "帮助", "合作", "分享", "开心", "快乐"]
    building_keywords = ["建设", "改进", "装饰", "建造", "修建", "完善"]
    neutral_keywords = ["讨论", "会议", "计划", "思考", "观察"]
    negative_keywords = ["争吵", "冲突", "问题", "困难", "麻烦"]
    
    # 分析指令影响
    if any(keyword in command for keyword in positive_keywords):
        impact_type = "positive"
        happiness_change = 5
        activity_change = 3
    elif any(keyword in command for keyword in building_keywords):
        impact_type = "building"
        happiness_change = 2
        activity_change = 8
    elif any(keyword in command for keyword in neutral_keywords):
        impact_type = "neutral"
        happiness_change = 1
        activity_change = 2
    elif any(keyword in command for keyword in negative_keywords):
        impact_type = "negative"
        happiness_change = -3
        activity_change = -1
    else:
        # 默认轻微正面影响
        happiness_change = 1
        activity_change = 1
    
    # 更新社群统计数据
    stats = db.query(CommunityStats).first()
    if stats:
        stats.happiness = max(0, min(100, stats.happiness + happiness_change))
        stats.activity = max(0, min(100, stats.activity + activity_change))
        stats.last_updated = datetime.now()
        
        # 记录事件
        event = Event(
            event_type=impact_type,
            description=f"玩家执行指令: {request.command}",
            impact=json.dumps({"happiness": happiness_change, "activity": activity_change}),
            timestamp=datetime.now()
        )
        db.add(event)
        db.commit()
        
        return {
            "success": True,
            "command": request.command,
            "impact_type": impact_type,
            "changes": {
                "happiness": happiness_change,
                "activity": activity_change
            },
            "new_stats": {
                "happiness": stats.happiness,
                "activity": stats.activity
            },
            "message": f"指令已执行，影响类型: {impact_type}"
        }
    else:
        raise HTTPException(status_code=404, detail="社群数据未初始化")

@router.get("/commands/history")
async def get_command_history(limit: int = 10, db: Session = Depends(get_db)):
    """获取指令执行历史"""
    events = db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
    
    return {
        "commands": [
            {
                "id": event.id,
                "command": event.description,
                "type": event.event_type,
                "impact": json.loads(event.impact) if event.impact else {},
                "timestamp": event.timestamp.isoformat()
            }
            for event in events if "玩家执行指令" in event.description
        ]
    }