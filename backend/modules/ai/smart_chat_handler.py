"""
智能聊天处理器
使用LLM根据AI成员性格特征生成参与性回复
"""

import random
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from modules.simulation import Agent, AgentPersonality, AgentOccupation
from modules.shared.database import ChatMessage, Agents
from modules.llm import response_generator

class SmartChatHandler:
    """智能聊天处理器 - 使用LLM生成参与性回复"""
    
    def __init__(self):
        self.agent_profiles = {}
        self.conversation_memory = {}
        self.topic_keywords = self._init_topic_keywords()
        self.response_cache = {}
        
    def _init_topic_keywords(self) -> Dict[str, List[str]]:
        """初始化话题关键词"""
        return {
            "social": ["聊天", "交流", "朋友", "社交", "聚会", "活动", "见面", "认识", "大家", "一起"],
            "health": ["健康", "身体", "运动", "锻炼", "医生", "病", "药", "治疗", "养生", "营养"],
            "education": ["学习", "教育", "书", "知识", "课程", "培训", "技能", "成长", "读书", "分享会"],
            "work": ["工作", "职业", "事业", "项目", "任务", "同事", "老板", "薪水", "压力", "经验"],
            "art": ["艺术", "画", "音乐", "创作", "设计", "美", "文化", "展览", "创意", "灵感"],
            "community": ["社群", "社区", "邻居", "建设", "发展", "改善", "合作", "团结", "努力", "共同"],
            "daily": ["天气", "吃饭", "睡觉", "购物", "家务", "日常", "生活", "休息", "出去", "走走"],
            "future": ["未来", "计划", "目标", "梦想", "希望", "期待", "发展", "改变", "明天", "以后"],
            "technology": ["科技", "电脑", "手机", "网络", "软件", "程序", "数字", "智能", "技术", "系统"],
            "entertainment": ["娱乐", "游戏", "电影", "电视", "音乐", "小说", "休闲", "放松", "有趣", "好玩"],
            "business": ["商业", "生意", "经营", "市场", "客户", "品牌", "销售", "利润", "投资", "创业"]
        }
    
    def initialize_agent_profiles(self, agents: List[Agent]):
        """初始化AI成员档案"""
        for agent in agents:
            self.agent_profiles[agent.id] = {
                "name": agent.name,
                "personality": agent.personality,
                "occupation": agent.occupation,
                "age": agent.age,
                "interests": agent.interests,
                "stats": agent.stats,
                "last_message_time": None,
                "conversation_count_today": 0,
                "recent_topics": [],
                "current_mood": "neutral",
                "energy_level": random.uniform(0.7, 1.0)
            }
    
    async def process_user_message(self, user_message: str, db: Session) -> List[Dict[str, Any]]:
        """处理用户消息，生成AI成员回复"""
        
        # 分析消息主题
        topic_category = self._analyze_message_topic(user_message)
        
        # 获取对话上下文
        conversation_context = self._get_recent_conversation_context(db)
        
        # 选择参与的成员
        participating_agents = self._select_participating_agents(user_message, topic_category)
        
        responses = []
        
        for i, (agent_id, participation_score) in enumerate(participating_agents):
            profile = self.agent_profiles[agent_id]
            
            # 计算回复延迟
            delay = self._calculate_response_delay(profile, i, participation_score)
            
            # 使用LLM生成智能回复
            response = await self._generate_llm_response(
                profile, user_message, topic_category, conversation_context
            )
            
            if response and not self._is_duplicate_response(response, profile["name"]):
                responses.append({
                    "agent_id": agent_id,
                    "agent_name": profile["name"],
                    "response": response,
                    "delay": delay,
                    "participation_score": participation_score,
                    "response_type": "llm_generated"
                })
                
                # 更新成员状态
                self._update_agent_state(profile, user_message, response, topic_category)
                
                # 缓存回复，避免重复
                self._cache_response(response, profile["name"])
        
        return responses
    
    def _analyze_message_topic(self, message: str) -> str:
        """分析消息主题"""
        message_lower = message.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return "social"
    
    def _get_recent_conversation_context(self, db: Session, limit: int = 5) -> List[str]:
        """获取最近的对话上下文"""
        try:
            recent_messages = db.query(ChatMessage)\
                               .filter(ChatMessage.sender_type.in_(["user", "agent"]))\
                               .order_by(ChatMessage.timestamp.desc())\
                               .limit(limit)\
                               .all()
            
            context = []
            for msg in reversed(recent_messages):
                if msg.sender_type == "user":
                    context.append(f"玩家: {msg.content}")
                else:
                    context.append(f"{msg.sender_name}: {msg.content}")
            
            return context
        except Exception as e:
            print(f"❌ 获取对话上下文失败: {str(e)}")
            return []
    
    def _select_participating_agents(self, message: str, topic_category: str) -> List[Tuple[str, float]]:
        """选择参与对话的成员"""
        candidates = []
        
        for agent_id, profile in self.agent_profiles.items():
            score = self._calculate_participation_score(profile, message, topic_category)
            if score > 0.3:
                candidates.append((agent_id, score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        max_participants = self._determine_max_participants(message, topic_category)
        return candidates[:max_participants]
    
    def _calculate_participation_score(self, profile: Dict[str, Any], message: str, topic_category: str) -> float:
        """计算参与分数"""
        base_score = 0.6
        
        # 职业兴趣
        occupation_interest = self._get_occupation_topic_interest(profile["occupation"], topic_category)
        base_score += occupation_interest * 0.15
        
        # 性格加成
        personality_bonus = self._get_personality_bonus(profile["personality"], topic_category)
        base_score += personality_bonus * 0.25
        
        # 内容兴趣
        content_interest = self._calculate_content_interest(message, profile)
        base_score += content_interest * 0.2
        
        # 社交倾向
        social_tendency = self._calculate_social_tendency(profile)
        base_score += social_tendency * 0.15
        
        # 能量水平
        base_score *= profile["energy_level"]
        
        # 避免过度活跃
        if profile["conversation_count_today"] > 4:
            base_score *= 0.8
        
        # 随机因素
        base_score *= random.uniform(0.8, 1.2)
        
        return max(0, min(1, base_score))
    
    def _calculate_content_interest(self, message: str, profile: Dict[str, Any]) -> float:
        """计算对消息内容的兴趣"""
        message_lower = message.lower()
        interest_score = 0.0
        
        if any(word in message_lower for word in ["你好", "大家", "最近", "今天", "心情"]):
            interest_score += 0.4
        
        if any(word in message_lower for word in ["帮助", "建议", "想法", "看法"]):
            interest_score += 0.3
        
        if any(word in message_lower for word in ["分享", "经历", "故事"]):
            interest_score += 0.3
        
        return min(0.5, interest_score)
    
    def _calculate_social_tendency(self, profile: Dict[str, Any]) -> float:
        """计算社交倾向"""
        personality = str(profile["personality"])
        social_score = 0.3
        
        if "外向" in personality or "开朗" in personality:
            social_score += 0.3
        elif "内向" in personality:
            social_score += 0.1
        
        age = profile.get("age", 30)
        if age < 25:
            social_score += 0.2
        elif age < 35:
            social_score += 0.1
        
        return min(0.5, social_score)
    
    def _get_occupation_topic_interest(self, occupation: str, topic_category: str) -> float:
        """获取职业对话题的兴趣度"""
        interest_map = {
            "teacher": {"education": 0.9, "social": 0.7, "community": 0.6},
            "doctor": {"health": 0.9, "community": 0.6, "work": 0.5},
            "engineer": {"technology": 0.9, "work": 0.7, "future": 0.6},
            "artist": {"art": 0.9, "entertainment": 0.8, "social": 0.6},
            "merchant": {"business": 0.9, "work": 0.7, "community": 0.6},
            "farmer": {"daily": 0.8, "health": 0.6, "community": 0.6},
            "student": {"education": 0.8, "social": 0.8, "entertainment": 0.7},
            "researcher": {"education": 0.8, "technology": 0.7, "future": 0.6}
        }
        
        occupation_interests = interest_map.get(occupation, {})
        return occupation_interests.get(topic_category, 0.3)
    
    def _get_personality_bonus(self, personality: str, topic_category: str) -> float:
        """获取性格对话题的加成"""
        personality_map = {
            "乐观开朗": {"social": 0.3, "community": 0.2, "future": 0.2},
            "外向型": {"social": 0.3, "entertainment": 0.2, "community": 0.2},
            "内向型": {"education": 0.2, "art": 0.2, "technology": 0.1},
            "分析型": {"work": 0.2, "technology": 0.2, "education": 0.1},
            "创造型": {"art": 0.3, "entertainment": 0.2, "future": 0.1}
        }
        
        personality_bonus = personality_map.get(personality, {})
        return personality_bonus.get(topic_category, 0.0)
    
    def _determine_max_participants(self, message: str, topic_category: str) -> int:
        """确定最大参与人数"""
        if "大家" in message or "所有人" in message:
            return 4
        elif topic_category in ["community", "social"]:
            return random.randint(2, 4)
        else:
            return random.randint(1, 3)
    
    def _calculate_response_delay(self, profile: Dict[str, Any], order: int, participation_score: float) -> float:
        """计算回复延迟 - 极致优化，接近实时回复"""
        # 极大缩短基础延迟
        base_delay = random.uniform(0.2, 1.0)  # 从1-3秒进一步缩短到0.2-1秒
        
        # 几乎消除顺序延迟，让对话更自然
        order_delay = order * random.uniform(0.1, 0.5)  # 从0.5-1.5秒缩短到0.1-0.5秒
        
        # 最小化参与度影响
        participation_modifier = 1.2 - (participation_score * 0.2)  # 进一步减少影响
        
        # 性格微调，但保持快速响应
        if "外向" in str(profile["personality"]) or "乐观" in str(profile["personality"]):
            base_delay *= 0.5  # 外向的人几乎立即回复
        elif "内向" in str(profile["personality"]):
            base_delay *= 1.1  # 内向的人也只是稍微慢一点点
        
        total_delay = (base_delay + order_delay) * participation_modifier
        
        # 限制在极短的范围内，最多3秒
        return max(0.1, min(3.0, total_delay))
    
    async def _generate_llm_response(self, profile: Dict[str, Any], user_message: str, 
                                   topic_category: str, conversation_context: List[str]) -> str:
        """使用LLM生成智能回复 - 重点：参与性而非评价性"""
        max_attempts = 3  # 增加重试次数
        
        for attempt in range(max_attempts):
            try:
                # 调用LLM生成回复
                response = await response_generator.generate_agent_conversation_response(
                    agent_info={
                        "name": profile["name"],
                        "personality": str(profile["personality"]),
                        "occupation": str(profile["occupation"]),
                        "age": profile.get("age", 30),
                        "interests": profile.get("interests", [])
                    },
                    original_topic=user_message,
                    conversation_history=conversation_context,
                    current_conversation=conversation_context,
                    agent_own_history=[],
                    community_stats={"happiness": 70, "health": 70, "education": 70, "economy": 70},
                    recent_events=[],
                    is_first_speaker=len(conversation_context) == 0
                )
                
                if response.get("success") and response.get("agent_response"):
                    content = response["agent_response"].strip()
                    
                    # 验证回复是否符合参与性要求
                    if self._is_participatory_response(content):
                        print(f"✅ {profile['name']} LLM生成成功 (尝试 {attempt + 1})")
                        return content
                    else:
                        print(f"⚠️ {profile['name']} 生成的回复不够参与性 (尝试 {attempt + 1})，重试...")
                        continue
                else:
                    print(f"⚠️ {profile['name']} LLM回复生成失败 (尝试 {attempt + 1})")
                    continue
                
            except Exception as e:
                print(f"❌ {profile['name']} LLM生成回复异常 (尝试 {attempt + 1}): {str(e)}")
                continue
        
        # 如果所有LLM尝试都失败，使用智能后备方案
        print(f"🔄 {profile['name']} LLM方案失败，使用智能后备方案")
        return self._generate_smart_fallback_response(profile, user_message, topic_category, conversation_context)
    
    def _generate_smart_fallback_response(self, profile: Dict[str, Any], user_message: str, 
                                        topic_category: str, conversation_context: List[str]) -> str:
        """生成智能后备回复 - 基于用户消息类型和角色特征"""
        agent_name = profile["name"]
        personality = str(profile["personality"])
        occupation = str(profile["occupation"])
        
        # 分析消息类型并生成相应回复
        message_lower = user_message.lower()
        
        # 问题咨询类
        if any(word in message_lower for word in ["怎么", "如何", "什么", "哪里", "建议", "方法", "经验"]):
            if "放松" in message_lower or "压力" in message_lower:
                responses = [
                    f"我平时压力大的时候会去附近公园走走，特别是早晨的时候空气很清新。",
                    f"我喜欢听音乐放松，有时候也会和朋友聊聊天。",
                    f"我的经验是做些运动比较有效，比如跑步或者游泳。"
                ]
            elif "学习" in message_lower or "技能" in message_lower:
                responses = [
                    f"我觉得制定学习计划很重要，每天抽出固定时间练习。",
                    f"我建议可以找一些在线课程跟着学，边学边实践效果比较好。",
                    f"我的方法是先从基础开始，不要急于求成。"
                ]
            elif "工作" in message_lower or "困难" in message_lower:
                responses = [
                    f"遇到工作问题时，我通常会先梳理一下思路，看看问题出在哪里。",
                    f"我的经验是多和同事交流，有时候换个角度就能找到解决办法。",
                    f"我建议可以把问题拆分成小的部分，逐个解决。"
                ]
            else:
                responses = [
                    f"这个问题挺有意思的，我觉得可以试试从不同角度考虑一下。",
                    f"我的经验是遇到这种情况时，先收集一些相关信息比较好。",
                    f"我建议可以问问身边有经验的朋友，看看他们怎么处理的。"
                ]
        
        # 推荐类
        elif any(word in message_lower for word in ["推荐", "哪里", "什么地方", "好吃", "好玩"]):
            if "吃" in message_lower or "餐厅" in message_lower or "火锅" in message_lower:
                responses = [
                    f"我知道市中心有家川菜馆挺不错的，他们家的麻婆豆腐特别正宗。",
                    f"我经常去学校附近那家小火锅店，老板很实在，料也很新鲜。",
                    f"我推荐试试东街那家面馆，他们的牛肉面分量很足。"
                ]
            elif "玩" in message_lower or "去哪" in message_lower:
                responses = [
                    f"我周末常去公园那边，可以散步也可以划船，环境挺好的。",
                    f"我喜欢去图书馆看书，安静而且还能学到新东西。",
                    f"我建议可以去市博物馆看看，最近有个很有意思的展览。"
                ]
            else:
                responses = [
                    f"这个要看你的喜好了，我个人比较喜欢安静一点的地方。",
                    f"我觉得可以先在网上查查评价，然后再做决定。",
                    f"我的建议是选择离家近一点的，这样比较方便。"
                ]
        
        # 选择决策类
        elif any(word in message_lower for word in ["怎么样", "好不好", "选择", "决定"]):
            responses = [
                f"我觉得这个想法不错，值得试试。",
                f"我个人觉得可以，不过最终还是要看你自己的喜好。",
                f"我的建议是可以先试试看，不合适再调整。"
            ]
        
        # 分享类/感慨类
        elif any(word in message_lower for word in ["最近", "今天", "昨天", "感觉"]):
            responses = [
                f"是啊，我最近也有类似的感受。",
                f"我也注意到了这个情况，确实很有意思。",
                f"我的感觉和你差不多，可能很多人都是这样想的。"
            ]
        
        # 默认回复
        else:
            responses = [
                f"这个话题让我想起了自己的一些经历，确实值得聊聊。",
                f"我对这个也挺感兴趣的，平时偶尔会关注一下。",
                f"我觉得这个角度很有意思，我们可以继续聊聊。"
            ]
        
        # 根据性格特征调整回复
        if "乐观" in personality:
            selected = random.choice(responses)
            selected = selected.replace("。", "！")  # 让乐观的人更有热情
        elif "内向" in personality:
            # 内向的人回复更简洁
            responses = [r for r in responses if len(r) < 50]
            selected = random.choice(responses) if responses else "我也有类似的想法。"
        else:
            selected = random.choice(responses)
        
        return selected
    
    def _create_participatory_prompt(self, profile: Dict[str, Any], user_message: str, 
                                   topic_category: str, conversation_context: List[str]) -> str:
        """创建参与性提示词"""
        return f"""作为{profile['name']}，你必须以真实参与者身份回复，不是旁观评价者。

核心要求：
1. 禁止评价性回复：不说"这个观点很棒"、"讨论很有价值"等空洞评价
2. 必须具体参与：分享具体经验、行为、建议或推荐
3. 使用第一人称：多用"我通常会..."、"我喜欢..."、"我建议..."
4. 提供实质内容：给出具体的方法、地点、经验

你的身份：{profile['name']}，{profile['occupation']}，{profile['personality']}

用户消息："{user_message}"
话题：{topic_category}

请提供30-80字的具体参与性回复："""
    
    def _is_participatory_response(self, response: str) -> bool:
        """检查回复是否具有参与性"""
        # 检查是否包含明显的评价性语言（严格禁止）
        strict_evaluative_phrases = [
            "这个观点很棒", "讨论很有价值", "学到了很多", "很有启发",
            "值得思考", "很有道理", "讨论氛围", "这个话题有意思",
            "讨论很精彩", "分享很棒", "想法很好", "说得很对"
        ]
        
        # 严格检查评价性语言
        for phrase in strict_evaluative_phrases:
            if phrase in response:
                return False
        
        # 检查是否包含参与性语言（好的指标）
        participatory_phrases = [
            "我通常", "我喜欢", "我建议", "我知道", "我经常", "我觉得",
            "我推荐", "我会", "我的经验", "我认为", "我发现", "我试过",
            "我习惯", "我一般", "我常常", "我倾向于", "据我", "在我看来",
            "我个人", "我感觉", "我想", "我见过", "我听说", "我去过"
        ]
        
        # 检查参与性语言
        participatory_score = 0
        for phrase in participatory_phrases:
            if phrase in response:
                participatory_score += 1
        
        # 检查是否包含具体内容（积极指标）
        concrete_indicators = [
            "公园", "跑步", "散步", "运动", "书店", "咖啡厅", "餐厅", "商店",
            "学校", "医院", "市中心", "附近", "地方", "方法", "技巧", "经验",
            "建议", "推荐", "试试", "可以去", "不如", "或者", "比如", "例如",
            "首先", "然后", "最后", "步骤", "计划", "安排", "时间", "周末"
        ]
        
        concrete_score = 0
        for indicator in concrete_indicators:
            if indicator in response:
                concrete_score += 1
        
        # 检查问题回应（积极指标）
        response_indicators = [
            "？", "?", "吗", "呢", "吧", "怎么样", "如何", "哪里", "什么时候",
            "为什么", "怎么", "多少", "哪个", "哪些"
        ]
        
        response_score = 0
        for indicator in response_indicators:
            if indicator in response:
                response_score += 1
        
        # 计算总分
        total_score = participatory_score * 2 + concrete_score + response_score
        
        # 如果包含参与性语言，基本可以认为是参与性回复
        if participatory_score > 0:
            return True
        
        # 如果包含具体内容且有互动元素，也认为是参与性回复
        if concrete_score >= 2 and response_score > 0:
            return True
        
        # 如果回复比较长且包含具体内容，也倾向于认为是参与性的
        if len(response) > 30 and concrete_score >= 1:
            return True
        
        # 检查是否只是简单的赞同或反对（这些也算参与）
        simple_participation = [
            "同意", "赞成", "支持", "不同意", "反对", "觉得不", "不太",
            "确实", "没错", "对的", "是的", "当然", "可能", "也许", "或许"
        ]
        
        for phrase in simple_participation:
            if phrase in response and len(response) > 20:
                return True
        
        # 默认返回false，但标准比之前宽松
        return False
    
    def _is_duplicate_response(self, response: str, agent_name: str) -> bool:
        """检查是否是重复回复"""
        if agent_name not in self.response_cache:
            return False
        
        recent_responses = self.response_cache[agent_name]
        
        if response in recent_responses:
            return True
            
        for cached_response in recent_responses:
            response_words = set(response.replace('，', ' ').replace('。', ' ').split())
            cached_words = set(cached_response.replace('，', ' ').replace('。', ' ').split())
            
            if response_words and cached_words:
                intersection = response_words & cached_words
                union = response_words | cached_words
                similarity = len(intersection) / len(union)
                
                if similarity > 0.7:
                    return True
        
        return False
    
    def _cache_response(self, response: str, agent_name: str):
        """缓存回复"""
        if agent_name not in self.response_cache:
            self.response_cache[agent_name] = []
        
        self.response_cache[agent_name].append(response)
        
        if len(self.response_cache[agent_name]) > 3:
            self.response_cache[agent_name] = self.response_cache[agent_name][-3:]
    
    def _update_agent_state(self, profile: Dict[str, Any], user_message: str, response: str, topic_category: str):
        """更新成员状态"""
        profile["last_message_time"] = datetime.now()
        profile["conversation_count_today"] += 1
        
        if topic_category not in profile["recent_topics"]:
            profile["recent_topics"].append(topic_category)
            if len(profile["recent_topics"]) > 5:
                profile["recent_topics"] = profile["recent_topics"][-5:]
        
        if profile["conversation_count_today"] > 2:
            profile["energy_level"] *= 0.95
    
    async def get_participating_agents_info(self, user_message: str, db: Session) -> List[Dict[str, Any]]:
        """获取参与对话的居民信息（不生成LLM回复）"""
        # 分析消息主题
        topic_category = self._analyze_message_topic(user_message)
        
        # 获取对话上下文
        conversation_context = self._get_recent_conversation_context(db)
        
        # 选择参与的成员
        participating_agents = self._select_participating_agents(user_message, topic_category)
        
        agent_infos = []
        
        for i, (agent_id, participation_score) in enumerate(participating_agents):
            profile = self.agent_profiles[agent_id]
            
            # 计算回复延迟
            delay = self._calculate_response_delay(profile, i, participation_score)
            
            agent_infos.append({
                "agent_id": agent_id,
                "agent_name": profile["name"],
                "profile": profile,
                "delay": delay,
                "participation_score": participation_score,
                "user_message": user_message,
                "topic_category": topic_category,
                "conversation_context": conversation_context
            })
        
        return agent_infos
    
    async def generate_single_agent_response(self, agent_info: Dict[str, Any], user_message: str, db: Session) -> Dict[str, Any]:
        """为单个居民生成LLM回复"""
        try:
            profile = agent_info["profile"]
            topic_category = agent_info["topic_category"]
            conversation_context = agent_info["conversation_context"]
            
            # 使用LLM生成智能回复
            response = await self._generate_llm_response(
                profile, user_message, topic_category, conversation_context
            )
            
            if response and not self._is_duplicate_response(response, profile["name"]):
                # 更新成员状态
                self._update_agent_state(profile, user_message, response, topic_category)
                
                # 缓存回复，避免重复
                self._cache_response(response, profile["name"])
                
                return {
                    "agent_id": agent_info["agent_id"],
                    "agent_name": profile["name"],
                    "response": response,
                    "delay": agent_info["delay"],
                    "participation_score": agent_info["participation_score"],
                    "response_type": "llm_generated"
                }
            
            return None
            
        except Exception as e:
            print(f"❌ 生成 {agent_info['agent_name']} 回复失败: {str(e)}")
            return None

# 创建全局实例
smart_chat_handler = SmartChatHandler() 