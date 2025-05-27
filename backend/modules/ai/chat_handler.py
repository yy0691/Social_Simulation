"""
聊天处理器模块
处理用户消息并生成AI回复
"""

import random
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

class ChatHandler:
    """
    聊天处理器
    负责处理用户消息并生成AI回复
    """
    
    def __init__(self):
        # 预设的AI回复模板
        self.response_templates = [
            "这是一个很有趣的想法！让我想想如何在社群中实现它。",
            "我理解你的意思。这可能会对社群产生积极的影响。",
            "这个建议很不错！我会考虑如何将它融入到社群的发展中。",
            "感谢你的分享！这让我对社群的未来有了新的思考。",
            "你提到的这个点很重要。让我们一起探讨如何改善社群环境。",
            "我同意你的观点。社群的和谐发展需要大家的共同努力。",
            "这是一个值得深入讨论的话题。你还有其他想法吗？",
            "你的建议很有建设性！我会记录下来并在社群中推广。",
            "这个问题确实需要关注。让我们想想解决方案。",
            "非常感谢你的参与！你的意见对社群发展很有价值。"
        ]
        
        # 根据关键词的特定回复
        self.keyword_responses = {
            "聚会": "举办聚会是增进社群成员感情的好方法！我会安排一些有趣的活动。",
            "建设": "基础设施建设对社群发展很重要。我们可以考虑建设一些公共设施。",
            "冲突": "解决冲突需要耐心和智慧。我会帮助调解，促进大家的理解。",
            "幸福": "提升社群幸福感是我们的共同目标。让我们一起努力创造更好的环境。",
            "活跃": "保持社群活跃需要大家的参与。我会组织更多有趣的活动。",
            "问题": "发现问题是解决问题的第一步。让我们一起分析并找到解决方案。",
            "建议": "你的建议很宝贵！我会认真考虑并尝试实施。",
            "帮助": "我很乐意帮助你！请告诉我具体需要什么协助。",
            "改进": "持续改进是社群发展的关键。感谢你的关注和建议。",
            "未来": "对于社群的未来，我充满期待。让我们一起创造美好的明天。"
        }
    
    async def generate_response(self, user_message: str, db: Session) -> str:
        """
        生成AI回复
        
        参数:
        - user_message: 用户消息内容
        - db: 数据库会话
        
        返回:
        - AI回复内容
        """
        try:
            # 检查是否包含特定关键词
            for keyword, response in self.keyword_responses.items():
                if keyword in user_message:
                    return response
            
            # 根据消息长度和内容生成不同类型的回复
            if len(user_message) < 10:
                # 短消息的回复
                short_responses = [
                    "我明白了。",
                    "好的，我会考虑的。",
                    "谢谢你的分享！",
                    "这很有趣。",
                    "我同意你的看法。"
                ]
                return random.choice(short_responses)
            
            elif "?" in user_message or "？" in user_message:
                # 问题类消息的回复
                question_responses = [
                    "这是一个很好的问题。让我想想...",
                    "关于这个问题，我认为需要从多个角度来考虑。",
                    "你提出的问题很有深度，值得我们深入探讨。",
                    "这个问题的答案可能因情况而异，让我们一起分析。",
                    "感谢你的提问！这让我有机会分享我的想法。"
                ]
                return random.choice(question_responses)
            
            else:
                # 默认回复
                return random.choice(self.response_templates)
                
        except Exception as e:
            print(f"生成AI回复时出错: {str(e)}")
            return "抱歉，我现在有点忙，稍后再回复你。"
    
    def get_system_message(self, message_type: str) -> str:
        """
        获取系统消息
        
        参数:
        - message_type: 消息类型
        
        返回:
        - 系统消息内容
        """
        system_messages = {
            "welcome": "欢迎来到AI社群聊天室！我是你的AI助手，随时为你服务。",
            "user_joined": "新用户加入了聊天室，让我们欢迎他们！",
            "user_left": "有用户离开了聊天室，希望他们下次再来。",
            "maintenance": "系统正在进行维护，可能会有短暂的延迟。",
            "update": "聊天系统已更新，现在体验会更好！"
        }
        
        return system_messages.get(message_type, "系统消息")
    
    def analyze_sentiment(self, message: str) -> str:
        """
        简单的情感分析
        
        参数:
        - message: 消息内容
        
        返回:
        - 情感类型: positive/negative/neutral
        """
        positive_words = ["好", "棒", "喜欢", "开心", "高兴", "满意", "赞", "优秀", "完美"]
        negative_words = ["坏", "差", "讨厌", "生气", "愤怒", "不满", "糟糕", "失望", "难过"]
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral" 