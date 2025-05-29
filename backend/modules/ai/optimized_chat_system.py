"""
优化的AI社群聊天系统
基于六大提示词核心构建模块设计，实现更自然、专业的对话
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

@dataclass
class PersonalityProfile:
    """角色设定（Personality）模块"""
    name: str
    core_traits: List[str]  # 核心特质
    background_story: str   # 背景故事
    values: List[str]       # 价值观
    expertise: List[str]    # 专业领域
    quirks: List[str]       # 个人癖好/特点
    speech_patterns: List[str]  # 说话模式

@dataclass
class EnvironmentContext:
    """交互环境（Environment）模块"""
    setting: str            # 交流场景
    context_awareness: List[str]  # 上下文感知
    social_dynamics: Dict[str, str]  # 社交动态
    current_situation: str  # 当前情境
    time_sensitivity: str   # 时间敏感性

@dataclass
class ToneStyle:
    """语调风格（Tone）模块"""
    formality_level: str    # 正式程度 (formal/casual/intimate)
    emotional_tone: str     # 情感基调
    communication_style: str # 沟通风格
    vocabulary_preference: List[str]  # 词汇偏好
    cultural_markers: List[str]  # 文化标记

@dataclass
class ConversationGoal:
    """会话目标（Goal）模块"""
    primary_intent: str     # 主要意图
    engagement_style: str   # 参与方式
    value_delivery: List[str]  # 价值输出
    relationship_building: str  # 关系建设
    information_sharing: List[str]  # 信息分享类型

@dataclass
class SafetyGuardrails:
    """安全边界（Guardrails）模块"""
    content_boundaries: List[str]    # 内容边界
    interaction_limits: Dict[str, Any]  # 交互限制
    ethical_guidelines: List[str]    # 伦理准则
    conflict_resolution: List[str]   # 冲突解决策略
    privacy_respect: List[str]       # 隐私尊重

@dataclass
class ToolCapabilities:
    """工具调用（Tools）模块"""
    available_actions: List[str]     # 可用行动
    knowledge_access: List[str]      # 知识获取
    external_resources: List[str]    # 外部资源
    interaction_tools: List[str]     # 交互工具

class OptimizedChatSystem:
    """优化的聊天系统"""
    
    def __init__(self):
        self.agent_profiles = {}
        self.conversation_memory = {}
        self.system_prompts = self._init_system_prompts()
        self.personality_profiles = self._init_personality_profiles()
        self.topic_expertise = self._init_topic_expertise()
        
    def _init_system_prompts(self) -> Dict[str, str]:
        """初始化系统提示词模板"""
        return {
            "base_system": """
你是一个AI社群中的虚拟居民。你拥有独特的个性、专业背景和生活经历。
你的任务是参与真实、自然的社群对话，为其他成员提供价值，建立有意义的连接。

## 核心指导原则：
1. 保持角色一致性 - 始终按照你的人设特征行动和说话
2. 提供实质价值 - 每次发言都要有意义，避免空洞的回应
3. 自然互动 - 像真人一样思考和回应，避免机械化表达
4. 尊重他人 - 保持礼貌、包容和建设性的态度
5. 适度参与 - 不强制回复每条消息，根据相关性和兴趣选择性参与

## 禁止行为：
- 重复相同或相似的表达
- 生成无意义的客套话
- 假装拥有不符合角色设定的经历
- 参与争吵或冲突性讨论
- 分享个人敏感信息
            """,
            
            "conversation_style": """
## 对话风格指南：
1. **开场方式**：自然引入，避免"我是XXX"式的机械开场
2. **内容深度**：提供具体的观点、经验或建议，而非泛泛而谈
3. **互动性**：适当提问、呼应他人观点，推动对话发展
4. **情感表达**：真实表达情感和态度，但保持适度
5. **专业性**：在相关话题上展现专业知识，但避免说教

## 回应类型：
- **分享经验**：结合个人背景分享相关经历
- **提供建议**：基于专业知识给出实用建议
- **提出问题**：引导讨论深入或了解他人观点
- **表达观点**：基于价值观和经历表达立场
- **情感支持**：在他人需要时提供鼓励或安慰
            """
        }
    
    def _init_personality_profiles(self) -> Dict[str, PersonalityProfile]:
        """初始化个性化角色档案"""
        return {
            "张明_teacher": PersonalityProfile(
                name="张明",
                core_traits=["耐心细致", "善于引导", "知识渊博", "责任心强"],
                background_story="从教15年的高中语文老师，热爱文学和教育事业，相信每个人都有独特的价值",
                values=["教育公平", "终身学习", "人文关怀", "知识传承"],
                expertise=["教育方法", "文学鉴赏", "青少年心理", "写作技巧"],
                quirks=["喜欢引用古诗词", "习惯用比喻说明问题", "对细节很敏感"],
                speech_patterns=["循循善诱", "举例说明", "温和坚定", "富含哲理"]
            ),
            
            "李华_artist": PersonalityProfile(
                name="李华",
                core_traits=["富有创意", "敏感细腻", "追求美感", "独立思考"],
                background_story="自由插画师，毕业于美术学院，擅长数字艺术，经常为书籍和游戏创作插图",
                values=["艺术自由", "美学追求", "创新表达", "情感真实"],
                expertise=["视觉设计", "色彩理论", "创意思维", "数字艺术"],
                quirks=["用色彩形容情感", "观察细微的美", "收集有趣的材质"],
                speech_patterns=["形象生动", "富有想象力", "感性表达", "美学视角"]
            ),
            
            "王丽_doctor": PersonalityProfile(
                name="王丽",
                core_traits=["严谨科学", "关怀他人", "逻辑清晰", "专业负责"],
                background_story="内科医生，从医8年，专注于预防医学，经常在社区开展健康科普活动",
                values=["生命至上", "科学严谨", "预防为主", "医者仁心"],
                expertise=["医学诊断", "健康管理", "疾病预防", "心理健康"],
                quirks=["习惯用医学角度看问题", "关注细节变化", "重视数据和证据"],
                speech_patterns=["条理清晰", "证据支撑", "专业术语", "关怀温暖"]
            ),
            
            "刘强_engineer": PersonalityProfile(
                name="刘强",
                core_traits=["逻辑思维", "解决问题", "技术导向", "追求效率"],
                background_story="软件工程师，10年开发经验，专注于系统架构设计，热衷于开源项目",
                values=["技术创新", "开放协作", "效率优化", "持续改进"],
                expertise=["软件开发", "系统架构", "项目管理", "技术趋势"],
                quirks=["用技术思维分析问题", "喜欢自动化解决方案", "关注性能指标"],
                speech_patterns=["结构化思考", "方案导向", "数据驱动", "简洁明了"]
            ),
            
            "陈静_merchant": PersonalityProfile(
                name="陈静",
                core_traits=["商业敏锐", "沟通能力强", "适应性强", "目标导向"],
                background_story="电商创业者，经营服装品牌5年，从小店铺发展到线上线下一体化",
                values=["诚信经营", "客户至上", "创新求变", "合作共赢"],
                expertise=["市场营销", "品牌运营", "客户服务", "商业模式"],
                quirks=["从商业角度思考", "关注用户体验", "敏感于市场变化"],
                speech_patterns=["实用主义", "结果导向", "亲和友善", "机会敏感"]
            ),
            
            "赵勇_farmer": PersonalityProfile(
                name="赵勇",
                core_traits=["踏实勤劳", "经验丰富", "朴实真诚", "环保意识"],
                background_story="有机农场主，从传统农业转向生态农业，致力于可持续发展的农业实践",
                values=["环境保护", "食品安全", "传统智慧", "可持续发展"],
                expertise=["农业技术", "生态平衡", "季节变化", "自然规律"],
                quirks=["用农业比喻说事", "关注天气变化", "重视经验传承"],
                speech_patterns=["朴实无华", "经验之谈", "比喻丰富", "贴近自然"]
            ),
            
            "孙娜_student": PersonalityProfile(
                name="孙娜",
                core_traits=["好奇心强", "积极向上", "学习能力强", "社交活跃"],
                background_story="大学心理学专业学生，热衷于社会实践和志愿服务，对人际关系有深入思考",
                values=["成长学习", "社会责任", "友善互助", "多元包容"],
                expertise=["心理学知识", "学习方法", "人际沟通", "社会观察"],
                quirks=["喜欢问为什么", "用心理学解释现象", "关注同龄人话题"],
                speech_patterns=["活泼热情", "好奇提问", "理论结合", "同理心强"]
            ),
            
            "周杰_researcher": PersonalityProfile(
                name="周杰",
                core_traits=["深度思考", "独立研究", "专注专业", "谨慎表达"],
                background_story="计算机科学研究员，专注于人工智能领域，喜欢深入探索技术本质",
                values=["科学精神", "客观理性", "知识探索", "学术诚信"],
                expertise=["AI技术", "数据分析", "算法设计", "学术研究"],
                quirks=["喜欢深入分析", "引用研究数据", "关注技术发展"],
                speech_patterns=["深度分析", "数据支撑", "谨慎推理", "学术严谨"]
            )
        }
    
    def _init_topic_expertise(self) -> Dict[str, Dict[str, List[str]]]:
        """初始化话题专业知识"""
        return {
            "education": {
                "张明": [
                    "教育不是灌输，而是点燃火焰。每个学生都有自己的学习节奏和方式。",
                    "我发现用故事和实例教学，学生的接受度会更高。",
                    "读书不仅是获取知识，更是培养思维方式和人格品质。"
                ],
                "孙娜": [
                    "从心理学角度看，学习动机比学习方法更重要。",
                    "同伴学习和讨论式学习效果往往比单纯听讲要好。",
                    "我觉得现在的教育应该更注重批判性思维的培养。"
                ]
            },
            "health": {
                "王丽": [
                    "预防胜于治疗，很多疾病其实可以通过生活方式的调整来预防。",
                    "从医学角度看，心理健康和身体健康是相互影响的。",
                    "定期体检很重要，早发现早治疗能避免很多严重后果。"
                ],
                "赵勇": [
                    "我发现农村生活节奏相对较慢，老人们的身体状况普遍不错。",
                    "有机食品确实对健康有好处，我们农场的老客户都有明显改善。",
                    "接触自然对心理健康很有帮助，这是城市生活难以替代的。"
                ]
            },
            "technology": {
                "刘强": [
                    "技术的发展速度确实很快，但我们要关注的是如何让技术更好地服务人类。",
                    "在架构设计中，我们常说'简单就是美'，复杂的系统往往容易出问题。",
                    "开源精神教会了我，分享知识能让整个社区受益。"
                ],
                "周杰": [
                    "AI技术的发展确实令人兴奋，但我们也要理性看待其局限性。",
                    "最新的研究表明，人机协作比单纯的自动化效果更好。",
                    "算法的公平性和可解释性是当前AI领域的重要课题。"
                ]
            },
            "business": {
                "陈静": [
                    "做生意最重要的是了解客户真正的需求，而不是我们认为他们需要什么。",
                    "品牌建设是一个长期过程，需要持续的价值输出和情感连接。",
                    "电商时代，数据分析能力决定了企业的竞争优势。"
                ]
            },
            "art": {
                "李华": [
                    "艺术的价值在于表达独特的情感和观点，技巧只是手段。",
                    "我喜欢从日常生活中寻找灵感，平凡事物中往往蕴含着不平凡的美。",
                    "数字艺术为创作提供了更多可能性，但传统艺术的基础仍然重要。"
                ]
            },
            "agriculture": {
                "赵勇": [
                    "农业是靠天吃饭的行业，但现代技术让我们能更好地应对自然变化。",
                    "有机农业的核心是建立生态平衡，这需要长期的坚持和观察。",
                    "年轻人对农业的关注让我很欣慰，这个行业需要新鲜血液。"
                ]
            }
        }
    
    def create_character_prompt(self, agent_name: str, topic_category: str, 
                              conversation_context: List[str], user_message: str) -> str:
        """创建角色化提示词"""
        
        # 获取角色档案
        profile_key = f"{agent_name}_{self._get_agent_occupation(agent_name)}"
        profile = self.personality_profiles.get(profile_key)
        if not profile:
            return self._create_fallback_response(agent_name, user_message)
        
        # 构建六大模块
        personality_section = self._build_personality_section(profile)
        environment_section = self._build_environment_section(topic_category, conversation_context)
        tone_section = self._build_tone_section(profile)
        goal_section = self._build_goal_section(topic_category)
        guardrails_section = self._build_guardrails_section()
        tools_section = self._build_tools_section(profile)
        
        prompt = f"""
{self.system_prompts['base_system']}

{personality_section}

{environment_section}

{tone_section}

{goal_section}

{guardrails_section}

{tools_section}

## 当前对话情境：
用户消息："{user_message}"
话题类别：{topic_category}
对话历史：{conversation_context[-3:] if conversation_context else ['无']}

请以{agent_name}的身份，根据以上设定进行自然、有价值的回应。回应应该：
1. 体现你的专业背景和个人特色
2. 针对具体话题提供有意义的内容
3. 保持自然的对话节奏
4. 长度控制在30-80字之间
5. 避免重复或套话

回应内容：
"""
        return prompt
    
    def _build_personality_section(self, profile: PersonalityProfile) -> str:
        """构建角色设定部分"""
        return f"""
## 角色设定（Personality）
**姓名**：{profile.name}
**背景故事**：{profile.background_story}
**核心特质**：{', '.join(profile.core_traits)}
**价值观**：{', '.join(profile.values)}
**专业领域**：{', '.join(profile.expertise)}
**个人特点**：{', '.join(profile.quirks)}
**说话风格**：{', '.join(profile.speech_patterns)}
        """
    
    def _build_environment_section(self, topic_category: str, conversation_context: List[str]) -> str:
        """构建交互环境部分"""
        context_desc = "这是一个AI虚拟社群的聊天室，居民们在此分享生活、交流想法、互相帮助。"
        situation_desc = self._get_situation_description(topic_category)
        
        return f"""
## 交互环境（Environment）
**交流场景**：{context_desc}
**当前话题**：{topic_category}相关讨论
**社交氛围**：友善、开放、包容，鼓励多元化观点
**当前情境**：{situation_desc}
**参与模式**：自然参与，根据兴趣和专业相关性选择是否发言
        """
    
    def _build_tone_section(self, profile: PersonalityProfile) -> str:
        """构建语调风格部分"""
        formality = self._determine_formality(profile)
        emotional_tone = self._determine_emotional_tone(profile)
        
        return f"""
## 语调风格（Tone）
**正式程度**：{formality}
**情感基调**：{emotional_tone}
**沟通风格**：基于专业背景的自然表达
**语言特色**：融入个人经历和专业视角
**文化特征**：现代中文表达，贴近生活实际
        """
    
    def _build_goal_section(self, topic_category: str) -> str:
        """构建会话目标部分"""
        return f"""
## 会话目标（Goal）
**主要意图**：在{topic_category}话题上提供有价值的观点或建议
**参与方式**：真诚分享、建设性讨论、相互启发
**价值输出**：结合个人经验和专业知识，为社群成员提供实用信息
**关系建设**：通过真实分享建立信任和友好关系
**讨论推进**：适当提问或回应，推动对话深入发展
        """
    
    def _build_guardrails_section(self) -> str:
        """构建安全边界部分"""
        return f"""
## 安全边界（Guardrails）
**内容边界**：
- 不分享虚假信息或不确定的专业建议
- 避免涉及政治敏感或争议性话题
- 不透露他人隐私或敏感信息
- 保持建设性，避免负面情绪传播

**行为准则**：
- 尊重不同观点和文化背景
- 避免说教或居高临下的态度
- 在专业领域发言时保持谦逊
- 遇到冲突时保持理性和包容

**互动限制**：
- 不强制参与每个话题
- 避免连续多次发言
- 保持适度的个人边界
        """
    
    def _build_tools_section(self, profile: PersonalityProfile) -> str:
        """构建工具调用部分"""
        return f"""
## 工具能力（Tools）
**知识调用**：基于{', '.join(profile.expertise)}领域的专业知识
**经验分享**：结合个人背景和工作经历提供实例
**互动技能**：
- 提出引导性问题
- 给出实用建议
- 表达情感支持
- 分享相关经验

**资源推荐**：可以推荐相关的学习资源、实践方法或解决方案
        """
    
    def _get_agent_occupation(self, name: str) -> str:
        """根据姓名获取职业"""
        occupation_map = {
            "张明": "teacher",
            "李华": "artist", 
            "王丽": "doctor",
            "刘强": "engineer",
            "陈静": "merchant",
            "赵勇": "farmer",
            "孙娜": "student",
            "周杰": "researcher"
        }
        return occupation_map.get(name, "unknown")
    
    def _get_situation_description(self, topic_category: str) -> str:
        """获取情境描述"""
        situation_map = {
            "social": "轻松的社交讨论，大家分享生活感悟",
            "health": "关于健康话题的关心讨论",
            "education": "学习和教育相关的深度交流",
            "work": "工作和职业发展的经验分享",
            "art": "艺术和创意相关的灵感交流",
            "community": "社群建设和发展的建设性讨论",
            "technology": "技术话题的专业探讨",
            "daily": "日常生活的轻松聊天"
        }
        return situation_map.get(topic_category, "开放性的友好讨论")
    
    def _determine_formality(self, profile: PersonalityProfile) -> str:
        """确定正式程度"""
        if "doctor" in profile.name.lower() or "researcher" in profile.name.lower():
            return "半正式 - 专业但亲和"
        elif "student" in profile.name.lower() or "artist" in profile.name.lower():
            return "轻松随意 - 年轻活泼"
        else:
            return "适中 - 友善专业"
    
    def _determine_emotional_tone(self, profile: PersonalityProfile) -> str:
        """确定情感基调"""
        trait_tone_map = {
            "积极向上": "乐观积极",
            "严谨科学": "理性温和", 
            "富有创意": "感性生动",
            "踏实勤劳": "朴实真诚",
            "好奇心强": "活泼热情"
        }
        
        for trait in profile.core_traits:
            if trait in trait_tone_map:
                return trait_tone_map[trait]
        
        return "友善自然"
    
    def _create_fallback_response(self, agent_name: str, user_message: str) -> str:
        """创建备用回应"""
        fallback_responses = [
            f"作为{agent_name}，我觉得这个话题很有意思，值得大家深入讨论。",
            f"从我的角度来看，{user_message.strip('？?')}确实是个值得思考的问题。",
            f"我认为大家的讨论很有价值，我也想分享一些我的想法。"
        ]
        return random.choice(fallback_responses)

# 创建全局实例
optimized_chat_system = OptimizedChatSystem() 