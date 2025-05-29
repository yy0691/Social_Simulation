"""
增强的本地聊天系统
不依赖外部LLM，使用智能逻辑生成真实的AI成员对话
"""

import random
import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from modules.simulation import Agent, AgentPersonality, AgentOccupation
from modules.shared.database import ChatMessage, Agents

class PersonalityTrait(Enum):
    """性格特征"""
    EXTROVERTED = "外向型"
    INTROVERTED = "内向型"
    OPTIMISTIC = "乐观开朗"
    ANALYTICAL = "分析型"
    CREATIVE = "创造型"
    SUPPORTIVE = "支持型"
    LEADERSHIP = "领导型"
    REALISTIC = "现实主义"

@dataclass
class ConversationPattern:
    """对话模式"""
    greeting_styles: List[str]
    response_styles: List[str]
    topic_interests: Dict[str, float]
    speaking_frequency: float
    response_delay_range: Tuple[float, float]
    conversation_starters: List[str]
    agreement_phrases: List[str]
    disagreement_phrases: List[str]
    question_styles: List[str]

class EnhancedLocalChatSystem:
    """增强的本地聊天系统"""
    
    def __init__(self):
        self.agent_profiles = {}
        self.conversation_memory = {}
        self.topic_keywords = self._init_topic_keywords()
        self.personality_patterns = self._init_personality_patterns()
        self.response_templates = self._init_response_templates()
        
    def _init_topic_keywords(self) -> Dict[str, List[str]]:
        """初始化话题关键词"""
        return {
            "social": ["聊天", "交流", "朋友", "社交", "聚会", "活动", "见面", "认识"],
            "health": ["健康", "身体", "运动", "锻炼", "医生", "病", "药", "治疗", "养生"],
            "education": ["学习", "教育", "书", "知识", "课程", "培训", "技能", "成长"],
            "work": ["工作", "职业", "事业", "项目", "任务", "同事", "老板", "薪水"],
            "art": ["艺术", "画", "音乐", "创作", "设计", "美", "文化", "展览"],
            "community": ["社群", "社区", "邻居", "建设", "发展", "改善", "合作", "团结"],
            "daily": ["天气", "吃饭", "睡觉", "购物", "家务", "日常", "生活", "休息"],
            "future": ["未来", "计划", "目标", "梦想", "希望", "期待", "发展", "改变"],
            "technology": ["科技", "电脑", "手机", "网络", "软件", "程序", "数字", "智能"],
            "entertainment": ["娱乐", "游戏", "电影", "电视", "音乐", "小说", "休闲", "放松"]
        }
    
    def _init_personality_patterns(self) -> Dict[str, ConversationPattern]:
        """初始化性格对话模式"""
        return {
            "外向型": ConversationPattern(
                greeting_styles=[
                    "大家好！我是{name}，很高兴见到大家！",
                    "嗨！{name}来了，今天心情特别好！",
                    "哈喽！我是{name}，有什么有趣的事情要分享吗？"
                ],
                response_styles=[
                    "哇，{speaker}说得太对了！我完全同意！",
                    "这个想法太棒了！我想补充一点...",
                    "我也有类似的经历！让我来分享一下..."
                ],
                topic_interests={"social": 0.9, "entertainment": 0.8, "community": 0.7},
                speaking_frequency=0.8,
                response_delay_range=(2.0, 8.0),
                conversation_starters=[
                    "大家最近都在忙什么呢？",
                    "有没有人想一起组织个活动？",
                    "今天的天气真不错，适合出去走走！"
                ],
                agreement_phrases=[
                    "说得太好了！", "我完全赞成！", "这个主意棒极了！"
                ],
                disagreement_phrases=[
                    "我觉得可能还有其他角度...", "不过我想到了另一种可能..."
                ],
                question_styles=[
                    "大家觉得呢？", "你们有什么想法？", "我们可以一起讨论一下吗？"
                ]
            ),
            
            "内向型": ConversationPattern(
                greeting_styles=[
                    "我是{name}，很高兴能参与这个讨论。",
                    "大家好，我是{name}，我想分享一些想法。",
                    "我是{name}，听了大家的讨论很有启发。"
                ],
                response_styles=[
                    "我仔细想了想，{speaker}的观点很有道理。",
                    "从我的角度来看，这个问题可能...",
                    "我觉得我们需要深入思考一下..."
                ],
                topic_interests={"education": 0.8, "art": 0.7, "technology": 0.6},
                speaking_frequency=0.4,
                response_delay_range=(8.0, 20.0),
                conversation_starters=[
                    "我最近在思考一个问题...",
                    "有个想法想和大家分享...",
                    "我观察到一个有趣的现象..."
                ],
                agreement_phrases=[
                    "这个观点很深刻。", "我认为这很有道理。", "这让我想到了..."
                ],
                disagreement_phrases=[
                    "我有一些不同的看法...", "或许我们可以从另一个角度考虑..."
                ],
                question_styles=[
                    "大家怎么看？", "这个问题值得深思。", "我想听听其他人的意见。"
                ]
            ),
            
            "乐观开朗": ConversationPattern(
                greeting_styles=[
                    "大家好！我是{name}，今天又是美好的一天！",
                    "嗨！{name}在这里，满满的正能量送给大家！",
                    "哈喽！我是{name}，让我们一起创造美好的回忆吧！"
                ],
                response_styles=[
                    "太棒了！{speaker}总是能带来好想法！",
                    "这听起来很有希望！我们一定能做到！",
                    "我相信只要大家一起努力，一切都会变好的！"
                ],
                topic_interests={"social": 0.9, "community": 0.8, "future": 0.8},
                speaking_frequency=0.7,
                response_delay_range=(3.0, 10.0),
                conversation_starters=[
                    "今天有什么好消息要分享吗？",
                    "我们来聊聊开心的事情吧！",
                    "生活中总有值得感恩的事情！"
                ],
                agreement_phrases=[
                    "太好了！", "这真是个好消息！", "我就知道会成功的！"
                ],
                disagreement_phrases=[
                    "虽然有挑战，但我相信我们能克服！", "困难只是暂时的，未来会更好！"
                ],
                question_styles=[
                    "大家觉得这样会很棒吧？", "我们一起努力怎么样？", "这不是很令人兴奋吗？"
                ]
            ),
            
            "分析型": ConversationPattern(
                greeting_styles=[
                    "我是{name}，让我们理性地分析一下这个问题。",
                    "大家好，我是{name}，我想从数据角度来看这个话题。",
                    "我是{name}，我觉得我们需要系统性地思考这个问题。"
                ],
                response_styles=[
                    "根据{speaker}的观点，我们可以进一步分析...",
                    "这个想法有其合理性，但我们也要考虑...",
                    "让我们从逻辑角度来梳理一下..."
                ],
                topic_interests={"work": 0.8, "technology": 0.8, "education": 0.7},
                speaking_frequency=0.6,
                response_delay_range=(5.0, 15.0),
                conversation_starters=[
                    "我们来分析一下这个问题的根本原因...",
                    "从数据来看，我们可以得出...",
                    "让我们系统性地思考这个问题..."
                ],
                agreement_phrases=[
                    "这个分析很到位。", "逻辑很清晰。", "数据支持这个结论。"
                ],
                disagreement_phrases=[
                    "但是我们还需要考虑其他因素...", "数据可能还不够充分...", "这个假设需要验证..."
                ],
                question_styles=[
                    "我们有相关的数据吗？", "这个结论的依据是什么？", "我们如何验证这个想法？"
                ]
            ),
            
            "创造型": ConversationPattern(
                greeting_styles=[
                    "大家好！我是{name}，我有一些创意想法要分享！",
                    "嗨！{name}来了，带着满脑子的奇思妙想！",
                    "哈喽！我是{name}，让我们一起发挥想象力吧！"
                ],
                response_styles=[
                    "哇！{speaker}的想法激发了我的灵感！",
                    "这让我想到了一个更有趣的可能性...",
                    "我们可以在这个基础上创新一下..."
                ],
                topic_interests={"art": 0.9, "entertainment": 0.8, "future": 0.7},
                speaking_frequency=0.7,
                response_delay_range=(4.0, 12.0),
                conversation_starters=[
                    "我想到了一个很酷的创意...",
                    "如果我们换个角度思考会怎样？",
                    "让我们来头脑风暴一下！"
                ],
                agreement_phrases=[
                    "这个创意太棒了！", "想象力真丰富！", "这很有创新性！"
                ],
                disagreement_phrases=[
                    "或许我们可以更大胆一些...", "这个想法还可以更有创意..."
                ],
                question_styles=[
                    "我们能不能更有创意一些？", "有没有更有趣的方法？", "大家还有什么奇思妙想？"
                ]
            )
        }
    
    def _init_response_templates(self) -> Dict[str, List[str]]:
        """初始化回复模板"""
        return {
            "agreement": [
                "我完全同意{speaker}的观点！",
                "{speaker}说得很对，我也是这么想的。",
                "是的，{speaker}总结得很好！",
                "我支持{speaker}的想法！"
            ],
            "addition": [
                "在{speaker}的基础上，我想补充一点...",
                "除了{speaker}提到的，我觉得还有...",
                "{speaker}说得很好，我想再加一个角度...",
                "基于{speaker}的想法，我们还可以考虑..."
            ],
            "question": [
                "关于{speaker}提到的，我想问一下...",
                "{speaker}的想法很有趣，不过我想了解...",
                "听了{speaker}的分享，我有个疑问...",
                "对于{speaker}的观点，我想深入了解..."
            ],
            "experience": [
                "{speaker}的话让我想起了我的经历...",
                "我也有类似的体验，{speaker}说得很对...",
                "听了{speaker}的分享，我想到了...",
                "我的经历和{speaker}说的很相似..."
            ],
            "professional": [
                "从{occupation}的角度来看，{speaker}的观点...",
                "作为{occupation}，我对{speaker}的想法...",
                "基于我的专业经验，{speaker}提到的...",
                "从专业角度，{speaker}的建议..."
            ]
        }
    
    def initialize_agent_profiles(self, agents: List[Agent]):
        """初始化AI成员档案"""
        for agent in agents:
            self.agent_profiles[agent.id] = self._create_enhanced_profile(agent)
    
    def _create_enhanced_profile(self, agent: Agent) -> Dict[str, Any]:
        """创建增强的成员档案"""
        # 根据性格确定对话模式
        personality_key = agent.personality
        if personality_key not in self.personality_patterns:
            personality_key = "外向型"  # 默认
        
        pattern = self.personality_patterns[personality_key]
        
        # 根据职业调整话题兴趣
        occupation_interests = self._get_occupation_interests(agent.occupation)
        
        # 合并兴趣
        combined_interests = pattern.topic_interests.copy()
        for topic, score in occupation_interests.items():
            combined_interests[topic] = combined_interests.get(topic, 0.5) + score * 0.3
        
        return {
            "agent_id": agent.id,
            "name": agent.name,
            "personality": agent.personality,
            "occupation": agent.occupation,
            "age": agent.age,
            "interests": agent.interests,
            "conversation_pattern": pattern,
            "topic_interests": combined_interests,
            "last_message_time": None,
            "conversation_count_today": 0,
            "recent_topics": [],
            "mood": "neutral",
            "energy_level": random.uniform(0.6, 1.0)
        }
    
    def _get_occupation_interests(self, occupation: str) -> Dict[str, float]:
        """根据职业获取话题兴趣"""
        occupation_map = {
            "教师": {"education": 0.8, "social": 0.6, "community": 0.7},
            "医生": {"health": 0.9, "community": 0.6, "work": 0.7},
            "工程师": {"technology": 0.8, "work": 0.7, "education": 0.5},
            "艺术家": {"art": 0.9, "entertainment": 0.7, "future": 0.6},
            "商人": {"work": 0.8, "community": 0.6, "future": 0.7},
            "学生": {"education": 0.8, "social": 0.7, "entertainment": 0.6},
            "退休人员": {"health": 0.7, "community": 0.8, "daily": 0.6},
            "自由职业者": {"work": 0.6, "art": 0.7, "future": 0.6}
        }
        return occupation_map.get(occupation, {"social": 0.5, "community": 0.5})
    
    async def process_user_message(self, user_message: str, db: Session) -> List[Dict[str, Any]]:
        """处理用户消息，生成AI成员回复"""
        
        # 分析消息
        topic_category = self._analyze_message_topic(user_message)
        sentiment = self._analyze_message_sentiment(user_message)
        
        # 选择参与的成员
        participating_agents = self._select_participating_agents(user_message, topic_category, sentiment)
        
        responses = []
        conversation_context = []
        
        for i, (agent_id, participation_score) in enumerate(participating_agents):
            profile = self.agent_profiles[agent_id]
            
            # 计算回复延迟
            delay = self._calculate_response_delay(profile, i, participation_score)
            
            # 生成回复
            response = await self._generate_enhanced_response(
                profile, user_message, topic_category, conversation_context, i == 0
            )
            
            if response:
                responses.append({
                    "agent_id": agent_id,
                    "agent_name": profile["name"],
                    "response": response,
                    "delay": delay,
                    "participation_score": participation_score,
                    "response_type": "enhanced_local"
                })
                
                # 添加到对话上下文
                conversation_context.append(f"{profile['name']}: {response}")
                
                # 更新成员状态
                self._update_agent_state(profile, user_message, response, topic_category)
        
        return responses
    
    def _analyze_message_topic(self, message: str) -> str:
        """分析消息话题"""
        message_lower = message.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return "social"  # 默认社交话题
    
    def _analyze_message_sentiment(self, message: str) -> str:
        """分析消息情感"""
        positive_words = ["好", "棒", "喜欢", "开心", "高兴", "满意", "成功", "希望", "美好"]
        negative_words = ["不好", "糟糕", "讨厌", "难过", "失望", "失败", "问题", "困难"]
        question_words = ["吗", "呢", "如何", "怎么", "什么", "为什么", "？"]
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        question_count = sum(1 for word in question_words if word in message_lower)
        
        if question_count > 0:
            return "questioning"
        elif positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _select_participating_agents(self, message: str, topic_category: str, sentiment: str) -> List[Tuple[str, float]]:
        """选择参与对话的成员"""
        candidates = []
        
        for agent_id, profile in self.agent_profiles.items():
            score = self._calculate_participation_score(profile, message, topic_category, sentiment)
            if score > 0.3:  # 参与阈值
                candidates.append((agent_id, score))
        
        # 按分数排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 限制参与人数
        max_participants = self._determine_max_participants(message, topic_category)
        return candidates[:max_participants]
    
    def _calculate_participation_score(self, profile: Dict[str, Any], message: str, topic_category: str, sentiment: str) -> float:
        """计算参与分数"""
        base_score = 0.5
        
        # 话题兴趣
        topic_interest = profile["topic_interests"].get(topic_category, 0.3)
        base_score += topic_interest * 0.4
        
        # 性格影响
        personality = profile["personality"]
        if personality in ["外向型", "乐观开朗"]:
            base_score += 0.2
        elif personality == "内向型":
            base_score -= 0.1
        
        # 能量水平
        base_score *= profile["energy_level"]
        
        # 今日对话次数影响
        if profile["conversation_count_today"] > 5:
            base_score *= 0.8
        
        # 随机因素
        base_score *= random.uniform(0.8, 1.2)
        
        return max(0, min(1, base_score))
    
    def _determine_max_participants(self, message: str, topic_category: str) -> int:
        """确定最大参与人数"""
        if "大家" in message or "所有人" in message:
            return 6
        elif topic_category in ["community", "social"]:
            return random.randint(3, 5)
        else:
            return random.randint(2, 4)
    
    def _calculate_response_delay(self, profile: Dict[str, Any], order: int, participation_score: float) -> float:
        """计算回复延迟"""
        pattern = profile["conversation_pattern"]
        base_delay = random.uniform(*pattern.response_delay_range)
        
        # 发言顺序影响
        order_delay = order * random.uniform(2, 5)
        
        # 参与度影响
        participation_modifier = 2.0 - participation_score
        
        total_delay = (base_delay + order_delay) * participation_modifier
        return max(1.0, min(60.0, total_delay))
    
    async def _generate_enhanced_response(self, profile: Dict[str, Any], user_message: str, 
                                        topic_category: str, conversation_context: List[str], 
                                        is_first_speaker: bool) -> str:
        """生成增强的回复"""
        
        pattern = profile["conversation_pattern"]
        name = profile["name"]
        personality = profile["personality"]
        occupation = profile["occupation"]
        
        if is_first_speaker:
            # 第一个发言者
            response = self._generate_first_response(profile, user_message, topic_category)
        else:
            # 后续发言者
            response = self._generate_follow_up_response(profile, user_message, conversation_context, topic_category)
        
        # 添加个性化元素
        response = self._add_personality_touch(response, profile, topic_category)
        
        return response
    
    def _generate_first_response(self, profile: Dict[str, Any], user_message: str, topic_category: str) -> str:
        """生成第一个回复"""
        pattern = profile["conversation_pattern"]
        name = profile["name"]
        
        # 选择问候风格
        greeting = random.choice(pattern.greeting_styles).format(name=name)
        
        # 根据话题生成内容
        content = self._generate_topic_response(profile, user_message, topic_category)
        
        # 可能添加问题
        if random.random() < 0.4:
            question = random.choice(pattern.question_styles)
            return f"{greeting} {content} {question}"
        else:
            return f"{greeting} {content}"
    
    def _generate_follow_up_response(self, profile: Dict[str, Any], user_message: str, 
                                   conversation_context: List[str], topic_category: str) -> str:
        """生成跟进回复"""
        if not conversation_context:
            return self._generate_first_response(profile, user_message, topic_category)
        
        last_speaker_msg = conversation_context[-1]
        last_speaker = last_speaker_msg.split(":")[0] if ":" in last_speaker_msg else "前面的朋友"
        
        # 选择回复类型
        response_types = ["agreement", "addition", "question", "experience", "professional"]
        response_type = random.choice(response_types)
        
        # 生成基础回复
        if response_type == "agreement":
            base_response = random.choice(self.response_templates["agreement"]).format(speaker=last_speaker)
        elif response_type == "addition":
            base_response = random.choice(self.response_templates["addition"]).format(speaker=last_speaker)
        elif response_type == "question":
            base_response = random.choice(self.response_templates["question"]).format(speaker=last_speaker)
        elif response_type == "experience":
            base_response = random.choice(self.response_templates["experience"]).format(speaker=last_speaker)
        else:  # professional
            base_response = random.choice(self.response_templates["professional"]).format(
                speaker=last_speaker, occupation=profile["occupation"]
            )
        
        # 添加具体内容
        content = self._generate_topic_response(profile, user_message, topic_category)
        
        return f"我是{profile['name']}，{base_response} {content}"
    
    def _generate_topic_response(self, profile: Dict[str, Any], user_message: str, topic_category: str) -> str:
        """根据话题生成回复内容"""
        personality = profile["personality"]
        occupation = profile["occupation"]
        
        topic_responses = {
            "social": [
                "我觉得多交流真的很重要，能让我们更好地了解彼此。",
                "社交活动总是能带来很多乐趣和新的想法。",
                "和大家在一起聊天是我最喜欢的事情之一。"
            ],
            "health": [
                "健康确实是最重要的，我们都应该多关注自己的身体。",
                "保持良好的生活习惯对每个人都很重要。",
                "我觉得心理健康和身体健康同样重要。"
            ],
            "education": [
                "学习是一个终身的过程，我们都应该保持好奇心。",
                "教育不仅仅是知识的传授，更是思维的培养。",
                "我相信每个人都有自己独特的学习方式。"
            ],
            "work": [
                "工作虽然有挑战，但也能带来成就感。",
                "我觉得工作和生活的平衡很重要。",
                "团队合作总是能产生更好的结果。"
            ],
            "art": [
                "艺术能够表达我们内心深处的情感。",
                "创造力是人类最宝贵的天赋之一。",
                "美的事物总是能让人心情愉悦。"
            ],
            "community": [
                "我们的社群就像一个大家庭，需要每个人的参与。",
                "社区建设需要大家共同努力。",
                "邻里和谐是幸福生活的基础。"
            ],
            "future": [
                "对未来充满期待总是让人兴奋。",
                "我相信只要努力，未来一定会更美好。",
                "规划未来很重要，但也要享受当下。"
            ]
        }
        
        responses = topic_responses.get(topic_category, topic_responses["social"])
        base_response = random.choice(responses)
        
        # 根据性格调整
        if personality == "乐观开朗":
            base_response = base_response.replace("重要", "非常重要").replace("好", "特别好")
        elif personality == "分析型":
            base_response = f"从理性角度来看，{base_response}"
        elif personality == "创造型":
            base_response = f"我觉得我们可以更有创意地{base_response}"
        
        return base_response
    
    def _add_personality_touch(self, response: str, profile: Dict[str, Any], topic_category: str) -> str:
        """添加个性化元素"""
        personality = profile["personality"]
        
        # 添加表情符号或语气词
        if personality == "乐观开朗":
            if random.random() < 0.3:
                response += " 😊"
        elif personality == "外向型":
            if random.random() < 0.2:
                response += "！"
        
        # 根据能量水平调整语气
        if profile["energy_level"] > 0.8:
            response = response.replace("。", "！")
        
        return response
    
    def _update_agent_state(self, profile: Dict[str, Any], user_message: str, response: str, topic_category: str):
        """更新成员状态"""
        profile["last_message_time"] = datetime.now()
        profile["conversation_count_today"] += 1
        
        # 更新最近话题
        if topic_category not in profile["recent_topics"]:
            profile["recent_topics"].append(topic_category)
            if len(profile["recent_topics"]) > 5:
                profile["recent_topics"] = profile["recent_topics"][-5:]
        
        # 调整能量水平
        if profile["conversation_count_today"] > 3:
            profile["energy_level"] *= 0.95
        
        # 更新对话记忆
        if profile["agent_id"] not in self.conversation_memory:
            self.conversation_memory[profile["agent_id"]] = []
        
        self.conversation_memory[profile["agent_id"]].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": response,
            "topic_category": topic_category
        })

# 创建全局实例
enhanced_local_chat = EnhancedLocalChatSystem() 