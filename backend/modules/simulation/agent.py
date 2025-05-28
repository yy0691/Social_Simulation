"""
AI居民代理模块
定义AI社群中每个居民的属性、行为和状态
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import uuid
from datetime import datetime

class AgentPersonality(Enum):
    """居民性格类型"""
    OPTIMISTIC = "乐观开朗"
    REALISTIC = "现实主义"
    CREATIVE = "创造型"
    ANALYTICAL = "分析型"
    SOCIAL = "社交型"
    INTROVERT = "内向型"
    LEADER = "领导型"
    SUPPORTER = "支持型"

class AgentOccupation(Enum):
    """居民职业类型"""
    TEACHER = "教师"
    DOCTOR = "医生"
    ENGINEER = "工程师"
    ARTIST = "艺术家"
    MERCHANT = "商人"
    FARMER = "农民"
    STUDENT = "学生"
    RESEARCHER = "研究员"
    CHEF = "厨师"
    BUILDER = "建筑工人"

@dataclass
class AgentMemory:
    """居民记忆系统"""
    event_description: str
    timestamp: datetime
    importance: int  # 1-5，重要程度
    emotion: str     # 情绪反应
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_description": self.event_description,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "emotion": self.emotion
        }

@dataclass
class AgentStats:
    """居民个人统计数据"""
    happiness: int = 50      # 个人快乐度 0-100
    health: int = 50         # 个人健康度 0-100
    education: int = 50      # 个人教育水平 0-100
    wealth: int = 50         # 个人财富 0-100
    social_connections: int = 50  # 社交关系 0-100
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "happiness": self.happiness,
            "health": self.health,
            "education": self.education,
            "wealth": self.wealth,
            "social_connections": self.social_connections
        }
    
    def update_stats(self, changes: Dict[str, int]):
        """更新统计数据"""
        for stat, change in changes.items():
            if hasattr(self, stat):
                current_value = getattr(self, stat)
                new_value = max(0, min(100, current_value + change))
                setattr(self, stat, new_value)

class Agent:
    """AI居民代理类"""
    
    def __init__(
        self,
        name: str,
        age: int = None,
        personality: AgentPersonality = None,
        occupation: AgentOccupation = None,
        interests: List[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age or random.randint(18, 80)
        self.personality = personality or random.choice(list(AgentPersonality))
        self.occupation = occupation or random.choice(list(AgentOccupation))
        self.interests = interests or self._generate_random_interests()
        
        # 状态数据
        self.stats = AgentStats()
        self.memories: List[AgentMemory] = []
        self.relationships: Dict[str, int] = {}  # agent_id -> relationship_strength
        
        # 行为参数
        self.last_activity_time = datetime.now()
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_active = True
        
        # 根据职业和性格调整初始属性
        self._initialize_stats_by_profile()
    
    def _generate_random_interests(self) -> List[str]:
        """生成随机兴趣爱好"""
        all_interests = [
            "阅读", "音乐", "艺术", "体育", "科技", "烹饪", "园艺", "旅行",
            "电影", "游戏", "摄影", "写作", "手工艺", "科学", "历史", "哲学"
        ]
        return random.sample(all_interests, random.randint(2, 5))
    
    def _initialize_stats_by_profile(self):
        """根据职业和性格初始化属性"""
        # 根据职业调整属性
        occupation_modifiers = {
            AgentOccupation.TEACHER: {"education": 20, "social_connections": 15},
            AgentOccupation.DOCTOR: {"health": 25, "wealth": 15, "education": 15},
            AgentOccupation.ENGINEER: {"education": 20, "wealth": 10},
            AgentOccupation.ARTIST: {"happiness": 15, "education": 10},
            AgentOccupation.MERCHANT: {"wealth": 20, "social_connections": 10},
            AgentOccupation.FARMER: {"health": 15, "happiness": 10},
            AgentOccupation.STUDENT: {"education": 15, "happiness": 5},
            AgentOccupation.RESEARCHER: {"education": 25, "wealth": 5},
            AgentOccupation.CHEF: {"happiness": 15, "health": 10},
            AgentOccupation.BUILDER: {"health": 20, "wealth": 5}
        }
        
        # 根据性格调整属性
        personality_modifiers = {
            AgentPersonality.OPTIMISTIC: {"happiness": 20, "social_connections": 10},
            AgentPersonality.REALISTIC: {"health": 10, "wealth": 10},
            AgentPersonality.CREATIVE: {"happiness": 15, "education": 10},
            AgentPersonality.ANALYTICAL: {"education": 15, "wealth": 5},
            AgentPersonality.SOCIAL: {"social_connections": 25, "happiness": 10},
            AgentPersonality.INTROVERT: {"health": 10, "education": 10},
            AgentPersonality.LEADER: {"social_connections": 20, "wealth": 10},
            AgentPersonality.SUPPORTER: {"happiness": 10, "social_connections": 15}
        }
        
        # 应用职业修饰符
        if self.occupation in occupation_modifiers:
            self.stats.update_stats(occupation_modifiers[self.occupation])
        
        # 应用性格修饰符
        if self.personality in personality_modifiers:
            self.stats.update_stats(personality_modifiers[self.personality])
    
    def add_memory(self, event_description: str, importance: int = 3, emotion: str = "中性"):
        """添加记忆"""
        memory = AgentMemory(
            event_description=event_description,
            timestamp=datetime.now(),
            importance=importance,
            emotion=emotion
        )
        self.memories.append(memory)
        
        # 只保留最近100条记忆
        if len(self.memories) > 100:
            self.memories = sorted(self.memories, key=lambda m: (m.importance, m.timestamp))[-100:]
    
    def get_recent_memories(self, count: int = 5) -> List[AgentMemory]:
        """获取最近的记忆"""
        return sorted(self.memories, key=lambda m: m.timestamp, reverse=True)[:count]
    
    def get_important_memories(self, count: int = 3) -> List[AgentMemory]:
        """获取重要记忆"""
        return sorted(self.memories, key=lambda m: m.importance, reverse=True)[:count]
    
    def update_relationship(self, other_agent_id: str, change: int):
        """更新与其他居民的关系"""
        current_strength = self.relationships.get(other_agent_id, 0)
        new_strength = max(-100, min(100, current_strength + change))
        self.relationships[other_agent_id] = new_strength
    
    def react_to_event(self, event_description: str, event_impact: Dict[str, int]) -> Dict[str, Any]:
        """对事件做出反应"""
        # 根据性格和职业计算反应强度
        reaction_intensity = self._calculate_reaction_intensity(event_impact)
        
        # 生成情绪反应
        emotion = self._generate_emotional_response(event_impact, reaction_intensity)
        
        # 更新个人状态
        personal_impact = self._calculate_personal_impact(event_impact, reaction_intensity)
        self.stats.update_stats(personal_impact)
        
        # 添加记忆
        self.add_memory(event_description, reaction_intensity, emotion)
        
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "reaction_intensity": reaction_intensity,
            "emotion": emotion,
            "personal_impact": personal_impact,
            "comment": self._generate_comment(event_description, emotion)
        }
    
    def _calculate_reaction_intensity(self, event_impact: Dict[str, int]) -> int:
        """计算对事件的反应强度"""
        # 基于事件影响的绝对值
        total_impact = sum(abs(value) for value in event_impact.values())
        
        # 根据性格调整
        personality_multipliers = {
            AgentPersonality.OPTIMISTIC: 0.8,
            AgentPersonality.REALISTIC: 1.0,
            AgentPersonality.CREATIVE: 1.2,
            AgentPersonality.ANALYTICAL: 0.9,
            AgentPersonality.SOCIAL: 1.1,
            AgentPersonality.INTROVERT: 0.7,
            AgentPersonality.LEADER: 1.3,
            AgentPersonality.SUPPORTER: 1.0
        }
        
        multiplier = personality_multipliers.get(self.personality, 1.0)
        intensity = int(total_impact * multiplier / 10)
        
        return max(1, min(5, intensity))
    
    def _generate_emotional_response(self, event_impact: Dict[str, int], intensity: int) -> str:
        """生成情绪反应"""
        # 计算整体影响趋势
        total_positive = sum(max(0, value) for value in event_impact.values())
        total_negative = sum(min(0, value) for value in event_impact.values())
        
        if total_positive > abs(total_negative):
            if intensity >= 4:
                return "非常高兴"
            elif intensity >= 3:
                return "高兴"
            else:
                return "满意"
        elif abs(total_negative) > total_positive:
            if intensity >= 4:
                return "非常担忧"
            elif intensity >= 3:
                return "担忧"
            else:
                return "不满"
        else:
            return "平静"
    
    def _calculate_personal_impact(self, event_impact: Dict[str, int], intensity: int) -> Dict[str, int]:
        """计算事件对个人的影响"""
        personal_impact = {}
        
        # 根据职业相关性调整影响
        occupation_relevance = {
            "education": {
                AgentOccupation.TEACHER: 1.5,
                AgentOccupation.STUDENT: 1.3,
                AgentOccupation.RESEARCHER: 1.4
            },
            "health": {
                AgentOccupation.DOCTOR: 1.5,
                AgentOccupation.FARMER: 1.2,
                AgentOccupation.BUILDER: 1.3
            },
            "economy": {
                AgentOccupation.MERCHANT: 1.5,
                AgentOccupation.ENGINEER: 1.3,
                AgentOccupation.ARTIST: 1.2
            }
        }
        
        for stat, impact in event_impact.items():
            if stat in ["happiness", "health", "education", "wealth"]:
                stat_name = stat if stat != "economy" else "wealth"
                
                # 基础影响
                base_impact = impact * (intensity / 5.0)
                
                # 应用职业相关性
                if stat in occupation_relevance and self.occupation in occupation_relevance[stat]:
                    base_impact *= occupation_relevance[stat][self.occupation]
                
                personal_impact[stat_name] = int(base_impact * 0.5)  # 个人影响通常比社群影响小
        
        return personal_impact
    
    def _generate_comment(self, event_description: str, emotion: str) -> str:
        """生成对事件的简短评论"""
        emotion_responses = {
            "非常高兴": ["太棒了！", "这真是个好消息！", "我很兴奋！"],
            "高兴": ["不错！", "这很好。", "我很满意。"],
            "满意": ["还可以。", "这样挺好的。", "我觉得不错。"],
            "平静": ["好吧。", "知道了。", "我明白了。"],
            "不满": ["这不太好。", "我有些担心。", "希望能改善。"],
            "担忧": ["这让我很担心。", "情况不太妙。", "我们需要小心。"],
            "非常担忧": ["这太糟糕了！", "我很害怕！", "必须要做些什么！"]
        }
        
        responses = emotion_responses.get(emotion, ["好的。"])
        return random.choice(responses)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "personality": self.personality.value,
            "occupation": self.occupation.value,
            "interests": self.interests,
            "stats": self.stats.to_dict(),
            "is_active": self.is_active,
            "last_activity_time": self.last_activity_time.isoformat(),
            "memory_count": len(self.memories),
            "relationship_count": len(self.relationships)
        }
    
    def get_profile_summary(self) -> str:
        """获取个人资料摘要"""
        return f"{self.name}，{self.age}岁，{self.occupation.value}，性格{self.personality.value}，兴趣爱好：{', '.join(self.interests[:3])}" 