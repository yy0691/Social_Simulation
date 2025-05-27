from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from modules.shared.database import get_db, CommunityStats, Agent, Event

router = APIRouter(tags=["community"])

@router.get("/community/status")
async def get_community_status(db: Session = Depends(get_db)):
    stats = db.query(CommunityStats).first()
    if not stats:
        raise HTTPException(status_code=404, detail="社群统计数据未找到")
    
    return {
        "population": stats.population,
        "happiness": stats.happiness,
        "activity": stats.activity,
        "resources": stats.resources,
        "last_updated": stats.last_updated.isoformat()
    }

@router.get("/community/agents")  
async def get_agents_list(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    
    return {
        "agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "personality": agent.personality,
                "role": agent.role,
                "mood": agent.mood,
                "activity_level": agent.activity_level,
                "created_at": agent.created_at.isoformat(),
                "last_active": agent.last_active.isoformat() if agent.last_active else None
            }
            for agent in agents
        ],
        "total_count": len(agents)
    }

@router.get("/community/events")
async def get_events_history(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "events": [
            {
                "id": event.id,
                "type": event.event_type,
                "description": event.description,
                "impact": json.loads(event.impact) if event.impact else {},
                "timestamp": event.timestamp.isoformat()
            }
            for event in events
        ],
        "limit": limit,
        "offset": offset
    }

@router.get("/community/stats/summary")
async def get_stats_summary(db: Session = Depends(get_db)):
    stats = db.query(CommunityStats).first()
    agents_count = db.query(Agent).count()
    events_count = db.query(Event).count()
    
    if not stats:
        raise HTTPException(status_code=404, detail="统计数据未找到")
    
    return {
        "community_stats": {
            "population": stats.population,
            "happiness": stats.happiness,
            "activity": stats.activity,
            "resources": stats.resources
        },
        "totals": {
            "agents": agents_count,
            "events": events_count
        },
        "last_updated": stats.last_updated.isoformat()
    }