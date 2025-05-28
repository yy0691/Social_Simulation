from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
import json

from modules.shared.database import get_db, CommunityStats, GameEvents
from modules.simulation import community_simulation, EventImpact, EventType
from modules.llm import response_generator, command_parser

router = APIRouter(tags=["commands"])

class CommandRequest(BaseModel):
    command: str
    description: Optional[str] = ""

class CommandResponse(BaseModel):
    success: bool
    command: str
    understanding: str
    execution_process: str
    result_description: str
    stat_changes: Dict[str, int]
    events_generated: list
    message: str
    command_info: Dict[str, Any]
    ai_response_info: Optional[Dict[str, Any]] = None

@router.post("/commands/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest, db: Session = Depends(get_db)):
    """执行玩家指令"""
    try:
        # 获取当前社群状态
        community_stats = await community_simulation.get_community_stats()
        
        # 使用LLM执行指令
        execution_result = await response_generator.execute_command(
            command_text=request.command,
            community_stats=community_stats
        )
        
        if not execution_result["success"]:
            return CommandResponse(
                success=False,
                command=request.command,
                understanding="指令解析失败",
                execution_process="",
                result_description="",
                stat_changes={},
                events_generated=[],
                message=execution_result["message"],
                command_info=execution_result.get("command_info", {})
            )
        
        # 应用统计变化到模拟系统
        stat_changes = execution_result.get("stat_changes", {})
        if stat_changes:
            # 创建自定义事件来应用变化
            impact = EventImpact(
                happiness=stat_changes.get("happiness", 0),
                health=stat_changes.get("health", 0),
                education=stat_changes.get("education", 0),
                economy=stat_changes.get("economy", 0)
            )
            
            # 根据指令类型确定事件类型
            command_type = execution_result.get("command_info", {}).get("parsed_type", "unknown")
            event_type_mapping = {
                "community_action": EventType.SOCIAL,
                "economic_policy": EventType.ECONOMIC,
                "education_initiative": EventType.EDUCATIONAL,
                "health_program": EventType.HEALTH,
                "infrastructure": EventType.COOPERATION,
                "emergency_response": EventType.DISASTER,
                "research_project": EventType.INNOVATION
            }
            
            event_type = event_type_mapping.get(command_type, EventType.SOCIAL)
            
            # 创建事件
            event = community_simulation.event_generator.create_custom_event(
                title=f"玩家指令：{request.command[:20]}...",
                description=execution_result.get("result_description", "玩家执行了一个指令"),
                event_type=event_type,
                impact=impact,
                triggered_by="player",
                duration_hours=1
            )
            
            # 应用事件到模拟系统
            await community_simulation.apply_event(event)
        
        # 保存指令执行记录到数据库
        try:
            event_record = GameEvents(
                event_id=f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=f"玩家指令：{request.command}",
                description=execution_result.get("execution_process", ""),
                event_type="player_command",
                impact_happiness=stat_changes.get("happiness", 0),
                impact_health=stat_changes.get("health", 0),
                impact_education=stat_changes.get("education", 0),
                impact_economy=stat_changes.get("economy", 0),
                timestamp=datetime.now(),
                triggered_by="player"
            )
            
            db.add(event_record)
            db.commit()
        except Exception as db_error:
            print(f"保存指令记录失败: {str(db_error)}")
        
        return CommandResponse(
            success=True,
            command=request.command,
            understanding=execution_result.get("understanding", ""),
            execution_process=execution_result.get("execution_process", ""),
            result_description=execution_result.get("result_description", ""),
            stat_changes=stat_changes,
            events_generated=execution_result.get("events_generated", []),
            message=execution_result.get("message", "指令执行成功"),
            command_info=execution_result.get("command_info", {}),
            ai_response_info=execution_result.get("ai_response_info")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"指令执行失败: {str(e)}"
        )

@router.get("/commands/parse")
async def parse_command(command: str):
    """解析指令但不执行"""
    try:
        parsed_command = command_parser.parse_command(command)
        is_valid, validation_message = command_parser.validate_command(parsed_command)
        
        return {
            "success": True,
            "data": {
                "original_text": parsed_command.original_text,
                "command_type": parsed_command.command_type.value,
                "action": parsed_command.action,
                "targets": parsed_command.targets,
                "parameters": parsed_command.parameters,
                "urgency": parsed_command.urgency,
                "expected_impact": parsed_command.expected_impact,
                "confidence": parsed_command.confidence,
                "is_valid": is_valid,
                "validation_message": validation_message
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"指令解析失败: {str(e)}"
        )

@router.get("/commands/suggestions")
async def get_command_suggestions(partial_text: str = ""):
    """获取指令建议"""
    try:
        suggestions = command_parser.get_command_suggestions(partial_text)
        
        return {
            "success": True,
            "data": {
                "suggestions": suggestions,
                "partial_text": partial_text
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取建议失败: {str(e)}"
        )

@router.get("/commands/history")
async def get_command_history(limit: int = 10, db: Session = Depends(get_db)):
    """获取指令执行历史"""
    try:
        events = db.query(GameEvents)\
                   .filter(GameEvents.event_type == "player_command")\
                   .order_by(GameEvents.timestamp.desc())\
                   .limit(limit)\
                   .all()
        
        return {
            "success": True,
            "data": {
                "commands": [
                    {
                        "id": event.event_id,
                        "title": event.title,
                        "description": event.description,
                        "impact": {
                            "happiness": event.impact_happiness,
                            "health": event.impact_health,
                            "education": event.impact_education,
                            "economy": event.impact_economy
                        },
                        "timestamp": event.timestamp.isoformat()
                    }
                    for event in events
                ],
                "total_count": len(events)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取指令历史失败: {str(e)}"
        )

@router.get("/commands/stats")
async def get_command_stats(db: Session = Depends(get_db)):
    """获取指令执行统计"""
    try:
        total_commands = db.query(GameEvents)\
                          .filter(GameEvents.event_type == "player_command")\
                          .count()
        
        # 获取最近24小时的指令数量
        from datetime import timedelta
        recent_threshold = datetime.now() - timedelta(hours=24)
        recent_commands = db.query(GameEvents)\
                           .filter(GameEvents.event_type == "player_command")\
                           .filter(GameEvents.timestamp >= recent_threshold)\
                           .count()
        
        # 获取LLM客户端状态
        llm_status = response_generator.get_client_status()
        
        return {
            "success": True,
            "data": {
                "total_commands_executed": total_commands,
                "recent_commands_24h": recent_commands,
                "llm_client_status": llm_status,
                "simulation_status": community_simulation.get_simulation_status()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        )