"""
AI社群模拟引擎核心模块
整合居民代理、事件系统和社群管理
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import random
import logging
from datetime import datetime, timedelta

from .agent import Agent, AgentPersonality, AgentOccupation
from .events import GameEvent, EventGenerator, EventImpact, event_generator

class CommunitySimulation:
    """AI社群模拟引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, Agent] = {}
        self.event_generator = event_generator
        self.simulation_running = False
        self.last_update = datetime.now()
        
        # 模拟参数
        self.auto_event_interval_hours = 6  # 自动事件生成间隔
        self.agent_interaction_probability = 0.1  # 居民互动概率
        self.stat_decay_rate = 0.5  # 属性自然衰减率（每天）
        
        # 初始化
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """初始化默认居民"""
        default_agents = [
            {"name": "张明", "age": 35, "personality": AgentPersonality.OPTIMISTIC, "occupation": AgentOccupation.TEACHER},
            {"name": "李华", "age": 28, "personality": AgentPersonality.CREATIVE, "occupation": AgentOccupation.ARTIST},
            {"name": "王丽", "age": 42, "personality": AgentPersonality.ANALYTICAL, "occupation": AgentOccupation.DOCTOR},
            {"name": "刘强", "age": 39, "personality": AgentPersonality.LEADER, "occupation": AgentOccupation.ENGINEER},
            {"name": "陈静", "age": 31, "personality": AgentPersonality.SOCIAL, "occupation": AgentOccupation.MERCHANT},
            {"name": "赵勇", "age": 45, "personality": AgentPersonality.REALISTIC, "occupation": AgentOccupation.FARMER},
            {"name": "孙娜", "age": 26, "personality": AgentPersonality.SUPPORTER, "occupation": AgentOccupation.STUDENT},
            {"name": "周杰", "age": 38, "personality": AgentPersonality.INTROVERT, "occupation": AgentOccupation.RESEARCHER}
        ]
        
        for agent_data in default_agents:
            agent = Agent(
                name=agent_data["name"],
                age=agent_data["age"],
                personality=agent_data["personality"],
                occupation=agent_data["occupation"]
            )
            self.agents[agent.id] = agent
    
    async def start_simulation(self):
        """启动模拟"""
        if self.simulation_running:
            self.logger.warning("模拟已在运行中")
            return
        
        self.simulation_running = True
        self.last_update = datetime.now()
        self.logger.info("AI社群模拟已启动")
        
        # 启动后台任务
        asyncio.create_task(self._simulation_loop())
    
    async def stop_simulation(self):
        """停止模拟"""
        self.simulation_running = False
        self.logger.info("AI社群模拟已停止")
    
    async def _simulation_loop(self):
        """模拟主循环"""
        while self.simulation_running:
            try:
                await self._update_simulation()
                await asyncio.sleep(300)  # 每5分钟更新一次
            except Exception as e:
                self.logger.error(f"模拟更新出错: {str(e)}")
                await asyncio.sleep(60)  # 出错后等待1分钟再继续
    
    async def _update_simulation(self):
        """更新模拟状态"""
        now = datetime.now()
        time_delta = now - self.last_update
        hours_passed = time_delta.total_seconds() / 3600
        
        if hours_passed < 0.1:  # 少于6分钟不更新
            return
        
        # 更新社群统计
        await self._update_community_stats()
        
        # 检查是否需要生成随机事件
        if hours_passed >= self.auto_event_interval_hours:
            await self._try_generate_random_event()
        
        self.last_update = now
    
    async def _update_community_stats(self):
        """更新社群整体统计"""
        if not self.agents:
            return
        
        # 计算平均值
        total_happiness = sum(agent.stats.happiness for agent in self.agents.values())
        total_health = sum(agent.stats.health for agent in self.agents.values())
        total_education = sum(agent.stats.education for agent in self.agents.values())
        total_wealth = sum(agent.stats.wealth for agent in self.agents.values())
        
        agent_count = len(self.agents)
        
        community_stats = {
            "population": agent_count,
            "happiness": int(total_happiness / agent_count),
            "health": int(total_health / agent_count),
            "education": int(total_education / agent_count),
            "economy": int(total_wealth / agent_count)  # 使用财富作为经济指标
        }
        
        self.logger.info(f"社群统计更新: {community_stats}")
    
    async def _try_generate_random_event(self):
        """尝试生成随机事件"""
        # 获取当前社群状态
        community_stats = await self.get_community_stats()
        
        # 生成随机事件
        event = self.event_generator.generate_random_event(community_stats)
        if event:
            await self.apply_event(event)
    
    async def get_community_stats(self) -> Dict[str, int]:
        """获取社群统计数据"""
        try:
            if not self.agents:
                return {
                    "population": 0,
                    "happiness": 50,
                    "health": 50,
                    "education": 50,
                    "economy": 50
                }
            
            # 计算平均值
            total_happiness = sum(agent.stats.happiness for agent in self.agents.values())
            total_health = sum(agent.stats.health for agent in self.agents.values())
            total_education = sum(agent.stats.education for agent in self.agents.values())
            total_wealth = sum(agent.stats.wealth for agent in self.agents.values())
            
            agent_count = len(self.agents)
            
            return {
                "population": agent_count,
                "happiness": int(total_happiness / agent_count),
                "health": int(total_health / agent_count),
                "education": int(total_education / agent_count),
                "economy": int(total_wealth / agent_count)
            }
        except Exception as e:
            self.logger.error(f"获取社群统计失败: {str(e)}")
            return {
                "population": len(self.agents),
                "happiness": 50,
                "health": 50,
                "education": 50,
                "economy": 50
            }
    
    async def apply_event(self, event: GameEvent) -> Dict[str, Any]:
        """应用事件到社群"""
        try:
            # 让居民对事件做出反应
            agent_reactions = []
            for agent in self.agents.values():
                if not event.affects_agents or agent.id in event.affects_agents:
                    reaction = agent.react_to_event(event.description, event.impact.to_dict())
                    agent_reactions.append(reaction)
            
            # 添加到事件历史
            self.event_generator.add_event_to_history(event)
            
            self.logger.info(f"事件已应用: {event.title}")
            
            return {
                "success": True,
                "event": event.to_dict(),
                "agent_reactions": agent_reactions,
                "community_impact": event.impact.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"应用事件失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_agents(self) -> List[Agent]:
        """获取所有居民"""
        return list(self.agents.values())
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """根据ID获取居民"""
        return self.agents.get(agent_id)
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """获取模拟状态"""
        return {
            "is_running": self.simulation_running,
            "agent_count": len(self.agents),
            "last_update": self.last_update.isoformat(),
            "auto_event_interval_hours": self.auto_event_interval_hours,
            "recent_event_count": len(self.event_generator.recent_events)
        }
    
    async def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近事件"""
        events = self.event_generator.get_event_history(limit)
        return [event.to_dict() for event in events]

# 全局社群模拟实例
community_simulation = CommunitySimulation() 