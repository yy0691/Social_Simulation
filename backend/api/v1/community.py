from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from datetime import datetime

from modules.shared.database import get_db, CommunityStats, Agents, GameEvents
from modules.simulation import community_simulation, Agent, GameEvent, EventImpact, EventType
from modules.llm import response_generator, command_parser, ParsedCommand

router = APIRouter(tags=["community"])

@router.get("/community/status")
async def get_community_status():
    """获取社群状态"""
    try:
        stats = await community_simulation.get_community_stats()
        simulation_status = community_simulation.get_simulation_status()
        
        return {
            "success": True,
            "data": {
                "population": stats["population"],
                "happiness": stats["happiness"],
                "health": stats["health"],
                "education": stats["education"],
                "economy": stats["economy"],
                "simulation": simulation_status,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取社群状态失败: {str(e)}")

@router.get("/community/agents")  
async def get_agents_list():
    """获取居民列表"""
    try:
        agents = community_simulation.get_all_agents()
        
        agents_data = []
        for agent in agents:
            agent_dict = agent.to_dict()
            # 添加最近记忆
            recent_memories = agent.get_recent_memories(3)
            agent_dict["recent_memories"] = [mem.to_dict() for mem in recent_memories]
            agents_data.append(agent_dict)
        
        return {
            "success": True,
            "data": {
                "agents": agents_data,
                "total_count": len(agents_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取居民列表失败: {str(e)}")

@router.get("/community/agents/{agent_id}")
async def get_agent_detail(agent_id: str):
    """获取居民详细信息"""
    try:
        agent = community_simulation.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="居民未找到")
        
        agent_data = agent.to_dict()
        
        # 添加详细记忆
        recent_memories = agent.get_recent_memories(10)
        important_memories = agent.get_important_memories(5)
        
        agent_data.update({
            "recent_memories": [mem.to_dict() for mem in recent_memories],
            "important_memories": [mem.to_dict() for mem in important_memories],
            "relationships": agent.relationships,
            "conversation_history": agent.conversation_history[-10:] if agent.conversation_history else []
        })
        
        return {
            "success": True,
            "data": agent_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取居民详情失败: {str(e)}")

@router.get("/community/events")
async def get_events_history(limit: int = 10):
    """获取事件历史"""
    try:
        events = await community_simulation.get_recent_events(limit)
        
        return {
            "success": True,
            "data": {
                "events": events,
                "total_count": len(events)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取事件历史失败: {str(e)}")

@router.post("/community/events/trigger")
async def trigger_custom_event(
    title: str,
    description: str,
    event_type: str,
    happiness_impact: int = 0,
    health_impact: int = 0,
    education_impact: int = 0,
    economy_impact: int = 0,
    duration_hours: int = 1
):
    """触发自定义事件"""
    try:
        # 验证事件类型
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的事件类型")
        
        # 创建事件影响
        impact = EventImpact(
            happiness=happiness_impact,
            health=health_impact,
            education=education_impact,
            economy=economy_impact
        )
        
        # 创建自定义事件
        event = community_simulation.event_generator.create_custom_event(
            title=title,
            description=description,
            event_type=event_type_enum,
            impact=impact,
            triggered_by="player",
            duration_hours=duration_hours
        )
        
        # 应用事件
        result = await community_simulation.apply_event(event)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发事件失败: {str(e)}")

@router.post("/community/simulation/start")
async def start_simulation():
    """启动模拟"""
    try:
        await community_simulation.start_simulation()
        
        return {
            "success": True,
            "message": "模拟已启动",
            "data": community_simulation.get_simulation_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动模拟失败: {str(e)}")

@router.post("/community/simulation/stop")
async def stop_simulation():
    """停止模拟"""
    try:
        await community_simulation.stop_simulation()
        
        return {
            "success": True,
            "message": "模拟已停止",
            "data": community_simulation.get_simulation_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止模拟失败: {str(e)}")

@router.get("/community/simulation/status")
async def get_simulation_status():
    """获取模拟运行状态"""
    try:
        status = community_simulation.get_simulation_status()
        
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模拟状态失败: {str(e)}")

@router.get("/community/stats/summary")
async def get_stats_summary():
    """获取统计数据摘要"""
    try:
        stats = await community_simulation.get_community_stats()
        simulation_status = community_simulation.get_simulation_status()
        recent_events = await community_simulation.get_recent_events(5)
        
        return {
            "success": True,
            "data": {
                "community_stats": stats,
                "simulation_status": simulation_status,
                "recent_events": recent_events,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计摘要失败: {str(e)}") 