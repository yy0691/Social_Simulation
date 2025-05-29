"""
真实AI成员聊天系统
实现更自然、个性化的AI成员发言机制
"""

import random
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from modules.simulation import Agent, AgentPersonality, AgentOccupation
from modules.shared.database import ChatMessage, Agents
from modules.llm import response_generator

class ResponseTiming(Enum):
    """回复时间类型"""
    IMMEDIATE = "immediate"      # 立即回复 (1-3秒)
    QUICK = "quick"             # 快速回复 (3-8秒)
    NORMAL = "normal"           # 正常回复 (8-15秒)
    SLOW = "slow"               # 慢速回复 (15-30秒)
    DELAYED = "delayed"         # 延迟回复 (30-60秒)

@dataclass
class AgentChatProfile:
    """AI成员聊天档案"""
    agent_id: str
    name: str
    personality: str
    occupation: str
    age: int
    interests: List[str]
    
    # 聊天行为特征
    chattiness: float           # 健谈程度 (0-1)
    response_speed: float       # 反应速度 (0-1)
    topic_engagement: Dict[str, float]  # 对不同话题的参与度
    social_energy: float        # 社交能量 (0-1)
    
    # 状态信息
    last_message_time: Optional[datetime] = None
    recent_topics: List[str] = None
    conversation_count_today: int = 0
    current_mood: str = "neutral"

class RealisticChatSystem:
    """真实聊天系统"""
    
    def __init__(self):
        self.agent_profiles: Dict[str, AgentChatProfile] = {}
        self.conversation_memory: Dict[str, List[Dict]] = {}  # agent_id -> conversation history
        self.topic_keywords = {
            "social": ["聚会", "活动", "朋友", "社交", "聊天", "交流"],
            "work": ["工作", "职业", "项目", "任务", "学习", "研究"],
            "health": ["健康", "运动", "医疗", "身体", "锻炼", "养生"],
            "entertainment": ["娱乐", "游戏", "电影", "音乐", "艺术", "创作"],
            "life": ["生活", "日常", "家庭", "购物", "美食", "旅行"],
            "community": ["社群", "邻居", "建设", "发展", "改善", "问题"]
        }
        
    def initialize_agent_profiles(self, agents: List[Agent]):
        """初始化AI成员聊天档案"""
        for agent in agents:
            profile = self._create_agent_profile(agent)
            self.agent_profiles[agent.id] = profile
            self.conversation_memory[agent.id] = []
    
    def _create_agent_profile(self, agent: Agent) -> AgentChatProfile:
        """根据AI成员信息创建聊天档案"""
        
        # 根据性格确定聊天特征
        personality_traits = {
            "乐观开朗": {"chattiness": 0.8, "response_speed": 0.9, "social_energy": 0.9},
            "现实主义": {"chattiness": 0.5, "response_speed": 0.6, "social_energy": 0.6},
            "创造型": {"chattiness": 0.7, "response_speed": 0.7, "social_energy": 0.7},
            "分析型": {"chattiness": 0.4, "response_speed": 0.5, "social_energy": 0.5},
            "社交型": {"chattiness": 0.9, "response_speed": 0.8, "social_energy": 0.9},
            "内向型": {"chattiness": 0.3, "response_speed": 0.4, "social_energy": 0.4},
            "领导型": {"chattiness": 0.7, "response_speed": 0.8, "social_energy": 0.8},
            "支持型": {"chattiness": 0.6, "response_speed": 0.7, "social_energy": 0.7}
        }
        
        # 根据职业确定话题参与度
        occupation_interests = {
            "教师": {"work": 0.9, "social": 0.8, "community": 0.8, "life": 0.7},
            "医生": {"health": 0.9, "work": 0.8, "community": 0.7, "life": 0.6},
            "工程师": {"work": 0.8, "entertainment": 0.6, "life": 0.6, "community": 0.5},
            "艺术家": {"entertainment": 0.9, "social": 0.8, "life": 0.7, "work": 0.6},
            "商人": {"work": 0.8, "social": 0.8, "community": 0.7, "life": 0.7},
            "农民": {"life": 0.8, "health": 0.7, "community": 0.7, "work": 0.6},
            "学生": {"work": 0.7, "social": 0.9, "entertainment": 0.8, "life": 0.7},
            "研究员": {"work": 0.9, "entertainment": 0.5, "life": 0.5, "community": 0.6},
            "厨师": {"life": 0.9, "social": 0.8, "health": 0.7, "entertainment": 0.7},
            "建筑工人": {"work": 0.7, "community": 0.8, "life": 0.7, "social": 0.6}
        }
        
        personality_key = agent.personality.value if hasattr(agent.personality, 'value') else str(agent.personality)
        occupation_key = agent.occupation.value if hasattr(agent.occupation, 'value') else str(agent.occupation)
        
        traits = personality_traits.get(personality_key, {"chattiness": 0.5, "response_speed": 0.5, "social_energy": 0.5})
        topic_engagement = occupation_interests.get(occupation_key, {
            "social": 0.5, "work": 0.5, "health": 0.5, "entertainment": 0.5, "life": 0.5, "community": 0.5
        })
        
        return AgentChatProfile(
            agent_id=agent.id,
            name=agent.name,
            personality=personality_key,
            occupation=occupation_key,
            age=agent.age,
            interests=agent.interests,
            chattiness=traits["chattiness"],
            response_speed=traits["response_speed"],
            topic_engagement=topic_engagement,
            social_energy=traits["social_energy"],
            recent_topics=[]
        )
    
    async def process_user_message(self, user_message: str, db: Session) -> List[Dict[str, Any]]:
        """
        处理用户消息，决定哪些AI成员会回复以及何时回复
        
        Returns:
            List[Dict]: 包含将要发言的AI成员信息和时间安排
        """
        
        # 分析消息话题
        topic_category = self._analyze_message_topic(user_message)
        message_sentiment = self._analyze_message_sentiment(user_message)
        
        # 决定哪些成员会参与对话
        participating_agents = self._select_participating_agents(
            user_message, topic_category, message_sentiment
        )
        
        # 为每个参与的成员安排回复时间
        response_schedule = []
        for i, (agent_id, participation_score) in enumerate(participating_agents):
            profile = self.agent_profiles[agent_id]
            
            # 计算回复延迟
            delay = self._calculate_response_delay(profile, i, participation_score)
            
            # 更新成员状态
            profile.last_message_time = datetime.now()
            profile.conversation_count_today += 1
            if topic_category not in profile.recent_topics:
                profile.recent_topics.append(topic_category)
                if len(profile.recent_topics) > 5:
                    profile.recent_topics.pop(0)
            
            response_schedule.append({
                "agent_id": agent_id,
                "agent_name": profile.name,
                "delay_seconds": delay,
                "participation_score": participation_score,
                "topic_category": topic_category,
                "is_first_responder": i == 0
            })
        
        return response_schedule
    
    def _analyze_message_topic(self, message: str) -> str:
        """分析消息话题类别"""
        topic_scores = {}
        
        for category, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                topic_scores[category] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return "general"
    
    def _analyze_message_sentiment(self, message: str) -> str:
        """简单的情感分析"""
        positive_words = ["好", "棒", "喜欢", "开心", "高兴", "满意", "赞", "优秀", "完美", "太好了"]
        negative_words = ["坏", "差", "讨厌", "生气", "愤怒", "不满", "糟糕", "失望", "难过", "问题"]
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def _select_participating_agents(self, message: str, topic_category: str, sentiment: str) -> List[Tuple[str, float]]:
        """选择参与对话的AI成员"""
        candidates = []
        
        for agent_id, profile in self.agent_profiles.items():
            # 计算参与分数
            participation_score = self._calculate_participation_score(
                profile, message, topic_category, sentiment
            )
            
            # 只有分数超过阈值的成员才会参与
            if participation_score > 0.3:
                candidates.append((agent_id, participation_score))
        
        # 按参与分数排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 限制参与人数（1-4人，根据消息重要性决定）
        max_participants = self._determine_max_participants(message, topic_category)
        
        return candidates[:max_participants]
    
    def _calculate_participation_score(self, profile: AgentChatProfile, message: str, topic_category: str, sentiment: str) -> float:
        """计算AI成员的参与分数"""
        score = 0.0
        
        # 基础健谈程度
        score += profile.chattiness * 0.3
        
        # 话题兴趣度
        topic_interest = profile.topic_engagement.get(topic_category, 0.5)
        score += topic_interest * 0.4
        
        # 社交能量（避免过度活跃）
        if profile.conversation_count_today < 5:
            score += profile.social_energy * 0.2
        else:
            score -= 0.1  # 今天已经说得太多了
        
        # 个人兴趣匹配
        for interest in profile.interests:
            if interest in message:
                score += 0.15
        
        # 性格对情感的反应
        if sentiment == "positive" and profile.personality in ["乐观开朗", "社交型"]:
            score += 0.1
        elif sentiment == "negative" and profile.personality in ["支持型", "领导型"]:
            score += 0.15
        
        # 随机因素（模拟真实的不确定性）
        score += random.uniform(-0.1, 0.1)
        
        # 避免同一个人连续发言太多
        if profile.last_message_time:
            time_since_last = datetime.now() - profile.last_message_time
            if time_since_last < timedelta(minutes=5):
                score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _determine_max_participants(self, message: str, topic_category: str) -> int:
        """确定最大参与人数"""
        # 问题或重要话题会吸引更多人参与
        if "?" in message or "？" in message:
            return random.randint(2, 4)
        elif topic_category in ["community", "social"]:
            return random.randint(2, 3)
        elif len(message) > 50:  # 长消息
            return random.randint(1, 3)
        else:
            return random.randint(1, 2)
    
    def _calculate_response_delay(self, profile: AgentChatProfile, order: int, participation_score: float) -> float:
        """计算回复延迟时间"""
        # 基础延迟（根据反应速度）
        base_delay = (1.0 - profile.response_speed) * 20 + 2  # 2-22秒
        
        # 参与顺序影响（后面的人会等前面的人说完）
        order_delay = order * random.uniform(3, 8)
        
        # 参与分数影响（更感兴趣的人回复更快）
        interest_modifier = (1.0 - participation_score) * 10
        
        # 性格影响
        personality_modifiers = {
            "社交型": 0.7,
            "乐观开朗": 0.8,
            "领导型": 0.8,
            "内向型": 1.5,
            "分析型": 1.3,
            "现实主义": 1.1
        }
        
        personality_modifier = personality_modifiers.get(profile.personality, 1.0)
        
        # 随机因素
        random_factor = random.uniform(0.8, 1.2)
        
        total_delay = (base_delay + order_delay + interest_modifier) * personality_modifier * random_factor
        
        # 限制在合理范围内
        return max(1.0, min(60.0, total_delay))
    
    async def generate_agent_response(self, agent_id: str, original_message: str, topic_category: str, 
                                    conversation_context: List[str], db: Session) -> Dict[str, Any]:
        """生成AI成员的回复"""
        
        profile = self.agent_profiles[agent_id]
        
        # 获取成员的历史对话
        agent_history = self._get_agent_conversation_history(agent_id, db)
        
        # 构建对话上下文
        context_info = self._build_conversation_context(
            profile, original_message, topic_category, conversation_context, agent_history
        )
        
        try:
            # 使用LLM生成回复
            response = await response_generator.generate_agent_conversation_response(
                agent_info={
                    "name": profile.name,
                    "personality": profile.personality,
                    "occupation": profile.occupation,
                    "age": profile.age,
                    "interests": profile.interests
                },
                original_topic=original_message,
                conversation_history=conversation_context,
                current_conversation=conversation_context,
                agent_own_history=agent_history,
                community_stats=await self._get_community_stats(),
                recent_events=await self._get_recent_events(),
                is_first_speaker=len(conversation_context) == 0
            )
            
            if response.get("success"):
                # 解析JSON回复
                try:
                    response_data = json.loads(response.get("content", "{}"))
                    agent_response = response_data.get("agent_response", f"我是{profile.name}，很高兴参与讨论！")
                    response_type = response_data.get("response_type", "general")
                    emotion = response_data.get("emotion", "neutral")
                except json.JSONDecodeError:
                    agent_response = response.get("content", f"我是{profile.name}，很高兴参与讨论！")
                    response_type = "general"
                    emotion = "neutral"
            else:
                # 生成备用回复
                agent_response = self._generate_fallback_response(profile, original_message, topic_category)
                response_type = "fallback"
                emotion = "neutral"
            
            # 更新对话记忆
            self._update_conversation_memory(agent_id, original_message, agent_response, topic_category)
            
            return {
                "success": True,
                "agent_response": agent_response,
                "response_type": response_type,
                "emotion": emotion,
                "agent_info": {
                    "name": profile.name,
                    "personality": profile.personality,
                    "occupation": profile.occupation
                }
            }
            
        except Exception as e:
            print(f"❌ 生成 {profile.name} 的回复失败: {str(e)}")
            return {
                "success": False,
                "agent_response": self._generate_fallback_response(profile, original_message, topic_category),
                "response_type": "error_fallback",
                "emotion": "neutral"
            }
    
    def _get_agent_conversation_history(self, agent_id: str, db: Session, limit: int = 5) -> List[str]:
        """获取AI成员的对话历史"""
        try:
            profile = self.agent_profiles[agent_id]
            messages = db.query(ChatMessage)\
                .filter(ChatMessage.sender_type == "agent")\
                .filter(ChatMessage.sender_name == profile.name)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(limit)\
                .all()
            
            history = []
            for msg in reversed(messages):
                history.append(f"我之前说过: {msg.content}")
            
            return history
        except Exception as e:
            print(f"❌ 获取 {agent_id} 对话历史失败: {str(e)}")
            return []
    
    def _build_conversation_context(self, profile: AgentChatProfile, original_message: str, 
                                  topic_category: str, conversation_context: List[str], 
                                  agent_history: List[str]) -> str:
        """构建对话上下文"""
        context_parts = []
        
        # 原始话题
        context_parts.append(f"原始话题: {original_message}")
        
        # 话题类别
        context_parts.append(f"话题类别: {topic_category}")
        
        # 当前对话
        if conversation_context:
            context_parts.append("当前对话:")
            context_parts.extend(conversation_context[-3:])  # 最近3条
        
        # 自己的历史发言
        if agent_history:
            context_parts.append("我自己之前的发言:")
            context_parts.extend(agent_history[-2:])  # 最近2条
        
        return "\n".join(context_parts)
    
    def _generate_fallback_response(self, profile: AgentChatProfile, original_message: str, topic_category: str) -> str:
        """生成备用回复"""
        
        # 根据话题类别生成不同的回复
        topic_responses = {
            "social": [
                f"我是{profile.name}，这个话题很有意思！我很喜欢和大家交流。",
                f"作为{profile.occupation}，我觉得社交活动对我们社群很重要。我是{profile.name}。",
                f"我是{profile.name}，大家一起讨论这个话题真好！"
            ],
            "work": [
                f"我是{profile.name}，从{profile.occupation}的角度来看，这确实值得关注。",
                f"作为{profile.occupation}，我对这个话题有一些想法。我是{profile.name}。",
                f"我是{profile.name}，工作相关的话题我很感兴趣！"
            ],
            "community": [
                f"我是{profile.name}，社群发展确实需要大家一起努力。",
                f"作为社群的一员，我是{profile.name}，我很关心这个问题。",
                f"我是{profile.name}，我们社群的未来需要大家共同参与！"
            ]
        }
        
        responses = topic_responses.get(topic_category, [
            f"我是{profile.name}，很高兴参与这个讨论！",
            f"作为{profile.occupation}，我想分享一下我的看法。我是{profile.name}。",
            f"我是{profile.name}，这个话题让我想到了很多。"
        ])
        
        return random.choice(responses)
    
    def _update_conversation_memory(self, agent_id: str, user_message: str, agent_response: str, topic_category: str):
        """更新对话记忆"""
        if agent_id not in self.conversation_memory:
            self.conversation_memory[agent_id] = []
        
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "topic_category": topic_category
        }
        
        self.conversation_memory[agent_id].append(memory_entry)
        
        # 保持记忆在合理范围内
        if len(self.conversation_memory[agent_id]) > 20:
            self.conversation_memory[agent_id] = self.conversation_memory[agent_id][-20:]
    
    async def _get_community_stats(self) -> Dict[str, Any]:
        """获取社群统计数据"""
        # 这里应该调用实际的社群统计API
        return {
            "happiness": 60,
            "health": 57,
            "education": 67,
            "economy": 59
        }
    
    async def _get_recent_events(self) -> List[str]:
        """获取最近事件"""
        # 这里应该调用实际的事件API
        return ["社群举办了读书分享会", "新建了一个小花园"]

# 创建全局实例
realistic_chat_system = RealisticChatSystem() 