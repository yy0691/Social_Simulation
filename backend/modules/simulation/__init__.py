"""
AI社群模拟模块
包含居民代理、事件系统和模拟引擎等核心功能
"""

from .agent import Agent, AgentPersonality, AgentOccupation, AgentStats, AgentMemory
from .events import GameEvent, EventGenerator, EventImpact, EventType, EventSeverity, event_generator
from .engine import CommunitySimulation, community_simulation

__all__ = [
    # 居民代理相关
    "Agent",
    "AgentPersonality",
    "AgentOccupation", 
    "AgentStats",
    "AgentMemory",
    
    # 事件系统相关
    "GameEvent",
    "EventGenerator",
    "EventImpact",
    "EventType",
    "EventSeverity",
    "event_generator",
    
    # 模拟引擎相关
    "CommunitySimulation",
    "community_simulation"
] 