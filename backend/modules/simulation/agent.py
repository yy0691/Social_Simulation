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
    
    def can_invite_friends(self) -> bool:
        """检查是否可以邀请朋友"""
        # 活跃的居民才能邀请朋友
        if not self.is_active:
            return False
        
        # 社交连接度高的居民更容易邀请朋友
        if self.stats.social_connections < 30:
            return False
        
        # 性格外向的居民更愿意邀请朋友
        social_personalities = [
            AgentPersonality.SOCIAL,
            AgentPersonality.OPTIMISTIC,
            AgentPersonality.LEADER
        ]
        
        if self.personality in social_personalities:
            return True
        
        # 其他性格的居民有一定概率邀请朋友
        return random.random() > 0.7
    
    def generate_invitation_message(self, friend_name: str) -> str:
        """生成个性化的邀请消息"""
        # 根据性格生成不同风格的邀请消息
        personality_templates = {
            AgentPersonality.OPTIMISTIC: [
                f"嗨！{friend_name}，我觉得你会很喜欢我们这个充满活力的社群！",
                f"亲爱的{friend_name}，来加入我们吧！这里有很多有趣的朋友！",
                f"{friend_name}，我们社群的氛围特别好，你一定会爱上这里的！"
            ],
            AgentPersonality.SOCIAL: [
                f"{friend_name}，我想邀请你加入我们的社群！这里有很多志同道合的朋友。",
                f"嗨{friend_name}！我们社群经常组织各种活动，你要不要一起参加？",
                f"{friend_name}，我觉得你会和我们社群的其他成员相处得很好！"
            ],
            AgentPersonality.LEADER: [
                f"{friend_name}，我们社群正在发展壮大，我想邀请你这样的人才加入！",
                f"亲爱的{friend_name}，我们社群需要更多像你这样优秀的成员。",
                f"{friend_name}，我相信你能为我们社群带来新的活力和想法！"
            ],
            AgentPersonality.CREATIVE: [
                f"{friend_name}，我们社群是一个充满创意和想象力的地方，你会喜欢的！",
                f"嗨{friend_name}！我们社群有很多有创意的项目，你要不要来看看？",
                f"{friend_name}，我觉得你的创意思维会让我们社群更加精彩！"
            ],
            AgentPersonality.ANALYTICAL: [
                f"{friend_name}，我分析了一下，我们社群的环境很适合你的发展。",
                f"亲爱的{friend_name}，从各个方面来看，我们社群都是一个不错的选择。",
                f"{friend_name}，我们社群有完善的体系和合理的规划，你会感兴趣的。"
            ]
        }
        
        # 根据职业添加专业相关的邀请内容
        occupation_additions = {
            AgentOccupation.TEACHER: "我们经常举办教育相关的讨论。",
            AgentOccupation.DOCTOR: "这里有很多关注健康生活的朋友。",
            AgentOccupation.ENGINEER: "我们社群有不少技术交流的机会。",
            AgentOccupation.ARTIST: "这里有很多热爱艺术的创作者。",
            AgentOccupation.MERCHANT: "我们经常讨论商业和经济话题。",
            AgentOccupation.CHEF: "这里有很多美食爱好者！",
            AgentOccupation.RESEARCHER: "我们社群鼓励知识分享和研究讨论。"
        }
        
        # 获取基础邀请消息
        templates = personality_templates.get(self.personality, [
            f"{friend_name}，我想邀请你加入我们的社群！",
            f"嗨{friend_name}！来和我们一起生活吧！",
            f"{friend_name}，我觉得你会喜欢我们社群的！"
        ])
        
        base_message = random.choice(templates)
        
        # 添加职业相关内容
        if self.occupation in occupation_additions:
            occupation_addition = occupation_additions[self.occupation]
            base_message += f" {occupation_addition}"
        
        # 添加兴趣相关内容
        if self.interests:
            common_interests = random.sample(self.interests, min(2, len(self.interests)))
            if len(common_interests) == 1:
                base_message += f" 我们都对{common_interests[0]}很感兴趣！"
            elif len(common_interests) == 2:
                base_message += f" 我们都喜欢{common_interests[0]}和{common_interests[1]}！"
        
        return base_message
    
    def should_make_friends_with(self, other_agent: 'Agent') -> bool:
        """判断是否应该与另一个居民成为朋友"""
        if not self.is_active or not other_agent.is_active:
            return False
        
        if self.id == other_agent.id:
            return False
        
        # 已经是朋友了就不需要重复建立关系
        if other_agent.id in self.relationships and self.relationships[other_agent.id] > 50:
            return False
        
        # 计算兼容性分数
        compatibility_score = self._calculate_compatibility(other_agent)
        
        # 兼容性分数高于60就可以成为朋友
        return compatibility_score > 60
    
    def _calculate_compatibility(self, other_agent: 'Agent') -> float:
        """计算与另一个居民的兼容性分数"""
        score = 50.0  # 基础分数
        
        # 年龄相近加分
        age_diff = abs(self.age - other_agent.age)
        if age_diff <= 5:
            score += 15
        elif age_diff <= 10:
            score += 10
        elif age_diff <= 15:
            score += 5
        
        # 职业相关性
        occupation_compatibility = {
            AgentOccupation.TEACHER: [AgentOccupation.STUDENT, AgentOccupation.RESEARCHER],
            AgentOccupation.DOCTOR: [AgentOccupation.TEACHER, AgentOccupation.RESEARCHER],
            AgentOccupation.ENGINEER: [AgentOccupation.RESEARCHER, AgentOccupation.BUILDER],
            AgentOccupation.ARTIST: [AgentOccupation.CHEF, AgentOccupation.TEACHER],
            AgentOccupation.MERCHANT: [AgentOccupation.FARMER, AgentOccupation.BUILDER],
            AgentOccupation.CHEF: [AgentOccupation.FARMER, AgentOccupation.ARTIST],
            AgentOccupation.RESEARCHER: [AgentOccupation.TEACHER, AgentOccupation.DOCTOR, AgentOccupation.ENGINEER]
        }
        
        if (self.occupation in occupation_compatibility and 
            other_agent.occupation in occupation_compatibility[self.occupation]):
            score += 15
        
        # 性格兼容性
        personality_compatibility = {
            AgentPersonality.OPTIMISTIC: [AgentPersonality.SOCIAL, AgentPersonality.CREATIVE],
            AgentPersonality.SOCIAL: [AgentPersonality.OPTIMISTIC, AgentPersonality.LEADER],
            AgentPersonality.LEADER: [AgentPersonality.SOCIAL, AgentPersonality.ANALYTICAL],
            AgentPersonality.CREATIVE: [AgentPersonality.OPTIMISTIC, AgentPersonality.ARTIST],
            AgentPersonality.ANALYTICAL: [AgentPersonality.REALISTIC, AgentPersonality.RESEARCHER],
            AgentPersonality.INTROVERT: [AgentPersonality.SUPPORTER, AgentPersonality.REALISTIC]
        }
        
        if (self.personality in personality_compatibility and 
            other_agent.personality in personality_compatibility[self.personality]):
            score += 20
        
        # 共同兴趣加分
        common_interests = set(self.interests) & set(other_agent.interests)
        score += len(common_interests) * 5
        
        # 社交能力加分
        avg_social = (self.stats.social_connections + other_agent.stats.social_connections) / 2
        score += (avg_social - 50) * 0.3
        
        return min(100, max(0, score))
    
    def get_friendship_potential_friends(self, all_agents: List['Agent']) -> List['Agent']:
        """获取有潜力成为朋友的居民列表"""
        potential_friends = []
        
        for agent in all_agents:
            if self.should_make_friends_with(agent):
                potential_friends.append(agent)
        
        # 按兼容性分数排序
        potential_friends.sort(key=lambda a: self._calculate_compatibility(a), reverse=True)
        
        # 只返回前5个最兼容的
        return potential_friends[:5]
    
    def initiate_invitation_behavior(self, all_agents: List['Agent']) -> Dict[str, Any]:
        """主动发起邀请行为"""
        if not self.can_invite_friends():
            return {"can_invite": False, "reason": "不符合邀请条件"}
        
        # 检查最近是否已经邀请过朋友
        recent_invitation_memory = [m for m in self.memories[-10:] 
                                   if "邀请" in m.event_description and 
                                   (datetime.now() - m.timestamp).days < 3]
        
        if recent_invitation_memory:
            return {"can_invite": False, "reason": "最近已经邀请过朋友"}
        
        # 生成虚拟好友信息（模拟现实中的朋友）
        virtual_friends = self._generate_virtual_friends()
        
        if not virtual_friends:
            return {"can_invite": False, "reason": "暂时没有想邀请的朋友"}
        
        # 选择一个朋友进行邀请
        selected_friend = random.choice(virtual_friends)
        invitation_message = self.generate_invitation_message(selected_friend["name"])
        
        # 添加到记忆中
        self.add_memory(f"我邀请了朋友{selected_friend['name']}加入社群", importance=4, emotion="期待")
        
        return {
            "can_invite": True,
            "friend_info": selected_friend,
            "invitation_message": invitation_message,
            "inviter_name": self.name
        }
    
    def _generate_virtual_friends(self) -> List[Dict[str, str]]:
        """生成虚拟朋友信息"""
        # 基于居民的职业和兴趣生成相关的朋友
        friend_pool = []
        
        # 基于职业的朋友
        occupation_friends = {
            AgentOccupation.TEACHER: ["张老师", "李同事", "王教授"],
            AgentOccupation.DOCTOR: ["林医生", "陈护士", "刘主任"],
            AgentOccupation.ENGINEER: ["吴工程师", "赵技术员", "钱架构师"],
            AgentOccupation.ARTIST: ["孙画家", "周设计师", "郑雕塑家"],
            AgentOccupation.MERCHANT: ["冯老板", "卫经理", "蒋商人"],
            AgentOccupation.FARMER: ["袁农夫", "韩菜农", "杨果农"],
            AgentOccupation.STUDENT: ["朱同学", "秦学友", "尤室友"],
            AgentOccupation.RESEARCHER: ["许研究员", "何博士", "吕学者"],
            AgentOccupation.CHEF: ["施大厨", "张烘焙师", "孔面点师"],
            AgentOccupation.BUILDER: ["严工人", "华建筑师", "金装修工"]
        }
        
        if self.occupation in occupation_friends:
            for friend_name in occupation_friends[self.occupation]:
                friend_pool.append({
                    "name": friend_name,
                    "email": f"{friend_name.lower().replace('老师','').replace('医生','').replace('工程师','').replace('老板','').replace('同学','').replace('大厨','')}@email.com",
                    "relationship": "同事"
                })
        
        # 基于兴趣的朋友
        interest_friends = {
            "阅读": ["书友小明", "文学爱好者小红"],
            "音乐": ["音乐人小李", "乐器老师小张"],
            "艺术": ["画家朋友", "艺术收藏家"],
            "体育": ["健身伙伴", "运动队友"],
            "科技": ["程序员朋友", "科技达人"],
            "烹饪": ["美食博主", "厨艺老师"],
            "园艺": ["园艺师", "植物爱好者"],
            "旅行": ["旅行达人", "背包客朋友"],
            "摄影": ["摄影师朋友", "影像工作者"]
        }
        
        for interest in self.interests[:2]:  # 只考虑前两个兴趣
            if interest in interest_friends:
                for friend_name in interest_friends[interest]:
                    friend_pool.append({
                        "name": friend_name,
                        "email": f"{friend_name.replace(' ','').lower()}@email.com",
                        "relationship": f"{interest}爱好者"
                    })
        
        # 随机选择1-3个朋友
        if friend_pool:
            return random.sample(friend_pool, min(3, len(friend_pool)))
        else:
            # 默认朋友
            return [
                {"name": "老朋友小王", "email": "xiaowang@email.com", "relationship": "老朋友"},
                {"name": "邻居小李", "email": "xiaoli@email.com", "relationship": "邻居"}
            ] 