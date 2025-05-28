"""
事件系统模块
管理AI社群中发生的各种事件和事件生成器
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import uuid
from datetime import datetime, timedelta

class EventType(Enum):
    """事件类型枚举"""
    CELEBRATION = "庆典"
    DISASTER = "灾难"
    DISCOVERY = "发现"
    CONFLICT = "冲突"
    COOPERATION = "合作"
    INNOVATION = "创新"
    ECONOMIC = "经济"
    SOCIAL = "社会"
    EDUCATIONAL = "教育"
    HEALTH = "健康"

class EventSeverity(Enum):
    """事件严重程度"""
    MINOR = "轻微"
    MODERATE = "中等"
    MAJOR = "重大"
    CRITICAL = "关键"

@dataclass
class EventImpact:
    """事件影响数据"""
    happiness: int = 0
    health: int = 0
    education: int = 0
    economy: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "happiness": self.happiness,
            "health": self.health,
            "education": self.education,
            "economy": self.economy
        }
    
    def scale_by_factor(self, factor: float) -> 'EventImpact':
        """按比例缩放影响"""
        return EventImpact(
            happiness=int(self.happiness * factor),
            health=int(self.health * factor),
            education=int(self.education * factor),
            economy=int(self.economy * factor)
        )

@dataclass
class GameEvent:
    """游戏事件类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    event_type: EventType = EventType.SOCIAL
    severity: EventSeverity = EventSeverity.MINOR
    impact: EventImpact = field(default_factory=EventImpact)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_hours: int = 1  # 事件持续时间（小时）
    triggered_by: str = "system"  # 触发者，可以是"system", "player", "agent_id"
    affects_agents: List[str] = field(default_factory=list)  # 受影响的特定居民ID
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "impact": self.impact.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "duration_hours": self.duration_hours,
            "triggered_by": self.triggered_by,
            "affects_agents": self.affects_agents,
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    def is_expired(self) -> bool:
        """检查事件是否已过期"""
        if not self.is_active:
            return True
        end_time = self.timestamp + timedelta(hours=self.duration_hours)
        return datetime.now() > end_time

class EventGenerator:
    """事件生成器"""
    
    def __init__(self):
        self.event_templates = self._init_event_templates()
        self.recent_events: List[GameEvent] = []
        self.event_cooldowns: Dict[EventType, datetime] = {}
    
    def _init_event_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化事件模板"""
        return {
            # 庆典类事件
            "harvest_festival": {
                "title": "丰收节",
                "description": "社群举办盛大的丰收节庆典，居民们载歌载舞，分享丰收的喜悦。",
                "event_type": EventType.CELEBRATION,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=20, health=5, education=0, economy=10),
                "duration_hours": 8
            },
            "founding_day": {
                "title": "建立纪念日",
                "description": "社群庆祝成立周年，举行盛大的纪念活动和游行。",
                "event_type": EventType.CELEBRATION,
                "severity": EventSeverity.MAJOR,
                "impact": EventImpact(happiness=25, health=0, education=5, economy=15),
                "duration_hours": 12
            },
            
            # 灾难类事件
            "heavy_rain": {
                "title": "暴雨来袭",
                "description": "突如其来的暴雨影响了社群的正常生活，部分设施受损。",
                "event_type": EventType.DISASTER,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=-15, health=-10, education=0, economy=-20),
                "duration_hours": 24
            },
            "epidemic_outbreak": {
                "title": "疫情爆发",
                "description": "社群出现传染病疫情，需要紧急应对和隔离措施。",
                "event_type": EventType.DISASTER,
                "severity": EventSeverity.CRITICAL,
                "impact": EventImpact(happiness=-30, health=-40, education=-10, economy=-25),
                "duration_hours": 72
            },
            
            # 发现类事件
            "mineral_discovery": {
                "title": "矿藏发现",
                "description": "探险队在社群附近发现了丰富的矿产资源。",
                "event_type": EventType.DISCOVERY,
                "severity": EventSeverity.MAJOR,
                "impact": EventImpact(happiness=15, health=0, education=10, economy=30),
                "duration_hours": 1
            },
            "ancient_artifact": {
                "title": "古代文物",
                "description": "考古学家在社群中发现了珍贵的古代文物。",
                "event_type": EventType.DISCOVERY,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=10, health=0, education=20, economy=5),
                "duration_hours": 1
            },
            
            # 创新类事件
            "new_technology": {
                "title": "技术突破",
                "description": "社群研究人员取得重大技术突破，将改善生活质量。",
                "event_type": EventType.INNOVATION,
                "severity": EventSeverity.MAJOR,
                "impact": EventImpact(happiness=20, health=15, education=25, economy=20),
                "duration_hours": 1
            },
            "medical_advance": {
                "title": "医疗进步",
                "description": "新的医疗技术和治疗方法被成功应用。",
                "event_type": EventType.INNOVATION,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=15, health=30, education=10, economy=5),
                "duration_hours": 1
            },
            
            # 合作类事件
            "community_project": {
                "title": "社区合作项目",
                "description": "居民们联手开展社区改善项目，加强了彼此的联系。",
                "event_type": EventType.COOPERATION,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=18, health=8, education=12, economy=10),
                "duration_hours": 48
            },
            "volunteer_campaign": {
                "title": "志愿者活动",
                "description": "大规模志愿者活动改善了社群环境和服务质量。",
                "event_type": EventType.COOPERATION,
                "severity": EventSeverity.MINOR,
                "impact": EventImpact(happiness=12, health=10, education=8, economy=5),
                "duration_hours": 24
            },
            
            # 冲突类事件
            "resource_dispute": {
                "title": "资源争议",
                "description": "不同群体对资源分配产生分歧，引发了争论。",
                "event_type": EventType.CONFLICT,
                "severity": EventSeverity.MODERATE,
                "impact": EventImpact(happiness=-20, health=-5, education=0, economy=-15),
                "duration_hours": 36
            },
            "ideological_clash": {
                "title": "理念冲突",
                "description": "社群内部出现理念分歧，导致紧张局势。",
                "event_type": EventType.CONFLICT,
                "severity": EventSeverity.MINOR,
                "impact": EventImpact(happiness=-15, health=0, education=-10, economy=-5),
                "duration_hours": 24
            }
        }
    
    def generate_random_event(self, community_stats: Dict[str, int]) -> Optional[GameEvent]:
        """根据社群状态生成随机事件"""
        # 检查冷却时间
        available_types = self._get_available_event_types()
        if not available_types:
            return None
        
        # 根据社群状态调整事件概率
        event_probabilities = self._calculate_event_probabilities(community_stats, available_types)
        
        # 选择事件类型
        selected_type = self._weighted_random_choice(event_probabilities)
        if not selected_type:
            return None
        
        # 从该类型中选择具体事件
        event_template = self._select_event_template(selected_type, community_stats)
        if not event_template:
            return None
        
        # 生成事件实例
        event = self._create_event_from_template(event_template, community_stats)
        
        # 设置冷却时间
        self._set_event_cooldown(selected_type)
        
        return event
    
    def _get_available_event_types(self) -> List[EventType]:
        """获取可用的事件类型（考虑冷却时间）"""
        now = datetime.now()
        available = []
        
        for event_type in EventType:
            cooldown_end = self.event_cooldowns.get(event_type)
            if cooldown_end is None or now > cooldown_end:
                available.append(event_type)
        
        return available
    
    def _calculate_event_probabilities(
        self, 
        community_stats: Dict[str, int], 
        available_types: List[EventType]
    ) -> Dict[EventType, float]:
        """根据社群状态计算事件概率"""
        base_probabilities = {
            EventType.CELEBRATION: 0.15,
            EventType.DISASTER: 0.10,
            EventType.DISCOVERY: 0.08,
            EventType.CONFLICT: 0.12,
            EventType.COOPERATION: 0.20,
            EventType.INNOVATION: 0.10,
            EventType.ECONOMIC: 0.15,
            EventType.SOCIAL: 0.10
        }
        
        # 根据社群状态调整概率
        happiness = community_stats.get("happiness", 50)
        health = community_stats.get("health", 50)
        education = community_stats.get("education", 50)
        economy = community_stats.get("economy", 50)
        
        adjustments = {}
        
        # 快乐度影响
        if happiness > 70:
            adjustments[EventType.CELEBRATION] = 1.5
            adjustments[EventType.COOPERATION] = 1.3
            adjustments[EventType.CONFLICT] = 0.5
        elif happiness < 30:
            adjustments[EventType.CONFLICT] = 1.8
            adjustments[EventType.DISASTER] = 1.2
            adjustments[EventType.CELEBRATION] = 0.3
        
        # 健康度影响
        if health < 40:
            adjustments[EventType.DISASTER] = adjustments.get(EventType.DISASTER, 1.0) * 1.5
        
        # 教育水平影响
        if education > 60:
            adjustments[EventType.INNOVATION] = 1.8
            adjustments[EventType.DISCOVERY] = 1.4
        
        # 经济状况影响
        if economy < 40:
            adjustments[EventType.ECONOMIC] = 1.6
            adjustments[EventType.CONFLICT] = adjustments.get(EventType.CONFLICT, 1.0) * 1.3
        
        # 应用调整
        adjusted_probabilities = {}
        for event_type in available_types:
            base_prob = base_probabilities.get(event_type, 0.1)
            adjustment = adjustments.get(event_type, 1.0)
            adjusted_probabilities[event_type] = base_prob * adjustment
        
        return adjusted_probabilities
    
    def _weighted_random_choice(self, probabilities: Dict[EventType, float]) -> Optional[EventType]:
        """加权随机选择"""
        if not probabilities:
            return None
        
        total_weight = sum(probabilities.values())
        if total_weight <= 0:
            return None
        
        rand_val = random.random() * total_weight
        current_weight = 0
        
        for event_type, weight in probabilities.items():
            current_weight += weight
            if rand_val <= current_weight:
                return event_type
        
        return list(probabilities.keys())[0]  # 备用选择
    
    def _select_event_template(self, event_type: EventType, community_stats: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """选择事件模板"""
        # 筛选该类型的事件模板
        matching_templates = [
            (key, template) for key, template in self.event_templates.items()
            if template["event_type"] == event_type
        ]
        
        if not matching_templates:
            return None
        
        # 简单随机选择（可以后续增加更复杂的选择逻辑）
        selected_key, selected_template = random.choice(matching_templates)
        return selected_template
    
    def _create_event_from_template(self, template: Dict[str, Any], community_stats: Dict[str, int]) -> GameEvent:
        """根据模板创建事件实例"""
        # 根据社群状态调整事件影响
        impact_scale = self._calculate_impact_scale(community_stats, template["severity"])
        adjusted_impact = template["impact"].scale_by_factor(impact_scale)
        
        return GameEvent(
            title=template["title"],
            description=template["description"],
            event_type=template["event_type"],
            severity=template["severity"],
            impact=adjusted_impact,
            duration_hours=template["duration_hours"],
            triggered_by="system"
        )
    
    def _calculate_impact_scale(self, community_stats: Dict[str, int], severity: EventSeverity) -> float:
        """计算影响缩放比例"""
        # 基础缩放
        base_scales = {
            EventSeverity.MINOR: 0.7,
            EventSeverity.MODERATE: 1.0,
            EventSeverity.MAJOR: 1.4,
            EventSeverity.CRITICAL: 1.8
        }
        
        base_scale = base_scales.get(severity, 1.0)
        
        # 根据社群规模调整（人口越多，影响相对越小）
        population = community_stats.get("population", 100)
        population_factor = max(0.5, min(1.5, 100 / population))
        
        return base_scale * population_factor
    
    def _set_event_cooldown(self, event_type: EventType):
        """设置事件类型冷却时间"""
        cooldown_hours = {
            EventType.CELEBRATION: 48,
            EventType.DISASTER: 72,
            EventType.DISCOVERY: 24,
            EventType.CONFLICT: 36,
            EventType.COOPERATION: 12,
            EventType.INNOVATION: 48,
            EventType.ECONOMIC: 24,
            EventType.SOCIAL: 12
        }
        
        hours = cooldown_hours.get(event_type, 24)
        self.event_cooldowns[event_type] = datetime.now() + timedelta(hours=hours)
    
    def create_custom_event(
        self,
        title: str,
        description: str,
        event_type: EventType,
        impact: EventImpact,
        triggered_by: str = "player",
        duration_hours: int = 1
    ) -> GameEvent:
        """创建自定义事件"""
        return GameEvent(
            title=title,
            description=description,
            event_type=event_type,
            severity=self._calculate_severity_from_impact(impact),
            impact=impact,
            duration_hours=duration_hours,
            triggered_by=triggered_by
        )
    
    def _calculate_severity_from_impact(self, impact: EventImpact) -> EventSeverity:
        """根据影响计算事件严重程度"""
        total_impact = abs(impact.happiness) + abs(impact.health) + abs(impact.education) + abs(impact.economy)
        
        if total_impact >= 80:
            return EventSeverity.CRITICAL
        elif total_impact >= 50:
            return EventSeverity.MAJOR
        elif total_impact >= 20:
            return EventSeverity.MODERATE
        else:
            return EventSeverity.MINOR
    
    def get_event_history(self, limit: int = 20) -> List[GameEvent]:
        """获取事件历史"""
        return sorted(self.recent_events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def add_event_to_history(self, event: GameEvent):
        """添加事件到历史记录"""
        self.recent_events.append(event)
        
        # 保留最近100个事件
        if len(self.recent_events) > 100:
            self.recent_events = self.recent_events[-100:]

# 全局事件生成器实例
event_generator = EventGenerator() 