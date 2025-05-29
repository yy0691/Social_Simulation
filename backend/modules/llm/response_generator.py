"""
AI响应生成模块
集成OpenAI API和响应处理逻辑
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from .config import get_llm_config, validate_llm_config, LLMProvider
from .prompts import game_prompts
from .command_parser import command_parser, ParsedCommand

@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str
    response_time: float
    success: bool
    error_message: Optional[str] = None

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 90000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times = []
        self.token_usage = []
    
    def can_make_request(self, estimated_tokens: int = 0) -> Tuple[bool, str]:
        """检查是否可以发起请求"""
        current_time = time.time()
        
        # 清理1分钟前的记录
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if current_time - t < 60]
        
        # 检查请求频率
        if len(self.request_times) >= self.requests_per_minute:
            return False, f"请求频率超限，每分钟最多{self.requests_per_minute}次请求"
        
        # 检查token使用量
        current_token_usage = sum(tokens for _, tokens in self.token_usage)
        if current_token_usage + estimated_tokens > self.tokens_per_minute:
            return False, f"Token使用量超限，每分钟最多{self.tokens_per_minute}个token"
        
        return True, "可以发起请求"
    
    def record_request(self, tokens_used: int = 0):
        """记录请求"""
        current_time = time.time()
        self.request_times.append(current_time)
        if tokens_used > 0:
            self.token_usage.append((current_time, tokens_used))

class ResponseGenerator:
    """AI响应生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = get_llm_config()
        self.client = None
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests_per_minute,
            self.config.rate_limit_tokens_per_minute
        )
        self._init_client()
    
    def _init_client(self):
        """初始化LLM客户端"""
        try:
            if AsyncOpenAI is None:
                self.logger.error("OpenAI库未安装，请运行: pip install openai")
                return
            
            is_valid, message = validate_llm_config()
            if not is_valid:
                self.logger.error(f"LLM配置无效: {message}")
                return
            
            if self.config.provider == LLMProvider.OPENAI:
                client_config = {
                    "api_key": self.config.api_key,
                    "timeout": self.config.timeout,
                    "max_retries": self.config.max_retries
                }
                if self.config.base_url:
                    client_config["base_url"] = self.config.base_url
                
                self.client = AsyncOpenAI(**client_config)
                self.logger.info("OpenAI客户端初始化成功")
            
            elif self.config.provider == LLMProvider.AZURE_OPENAI:
                from openai import AsyncAzureOpenAI
                self.client = AsyncAzureOpenAI(
                    api_key=self.config.api_key,
                    azure_endpoint=self.config.azure_endpoint,
                    api_version=self.config.api_version,
                    timeout=self.config.timeout,
                    max_retries=self.config.max_retries
                )
                self.logger.info("Azure OpenAI客户端初始化成功")
            
        except Exception as e:
            self.logger.error(f"客户端初始化失败: {str(e)}")
            self.client = None
    
    async def generate_response(
        self, 
        prompt_name: str, 
        **kwargs
    ) -> LLMResponse:
        """
        生成AI响应
        
        Args:
            prompt_name: 提示词模板名称
            **kwargs: 提示词参数
            
        Returns:
            LLMResponse: AI响应
        """
        if not self.client:
            return LLMResponse(
                content="",
                usage={},
                model="",
                finish_reason="error",
                response_time=0.0,
                success=False,
                error_message="LLM客户端未初始化"
            )
        
        try:
            # 获取提示词
            system_prompt, user_prompt = game_prompts.get_prompt(prompt_name, **kwargs)
            
            # 检查速率限制
            estimated_tokens = len(system_prompt + user_prompt) // 4  # 粗略估计
            can_request, limit_message = self.rate_limiter.can_make_request(estimated_tokens)
            if not can_request:
                return LLMResponse(
                    content="",
                    usage={},
                    model="",
                    finish_reason="rate_limited",
                    response_time=0.0,
                    success=False,
                    error_message=limit_message
                )
            
            # 准备消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 发起请求
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=0.9 if "conversation" in prompt_name else self.config.temperature,  # 对话回复使用更高的温度
                response_format={"type": "json_object"} if "JSON" in system_prompt else None
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 记录请求
            tokens_used = response.usage.total_tokens if response.usage else 0
            self.rate_limiter.record_request(tokens_used)
            
            # 构造响应
            content = response.choices[0].message.content or ""
            
            return LLMResponse(
                content=content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"生成响应失败: {str(e)}")
            return LLMResponse(
                content="",
                usage={},
                model="",
                finish_reason="error",
                response_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def execute_command(
        self, 
        command_text: str, 
        community_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行玩家指令
        
        Args:
            command_text: 指令文本
            community_stats: 社群状态数据
            
        Returns:
            Dict: 执行结果
        """
        try:
            # 解析指令
            parsed_command = command_parser.parse_command(command_text)
            
            # 验证指令
            is_valid, validation_message = command_parser.validate_command(parsed_command)
            if not is_valid:
                return {
                    "success": False,
                    "message": validation_message,
                    "command_info": {
                        "original_text": command_text,
                        "parsed_type": parsed_command.command_type.value,
                        "confidence": parsed_command.confidence
                    }
                }
            
            # 生成AI响应
            response = await self.generate_response(
                "command_execution",
                command=command_text,
                population=community_stats.get("population", 100),
                happiness=community_stats.get("happiness", 50),
                health=community_stats.get("health", 50),
                education=community_stats.get("education", 50),
                economy=community_stats.get("economy", 50)
            )
            
            if not response.success:
                return {
                    "success": False,
                    "message": f"AI处理失败: {response.error_message}",
                    "command_info": {
                        "original_text": command_text,
                        "parsed_type": parsed_command.command_type.value,
                        "confidence": parsed_command.confidence
                    }
                }
            
            # 解析AI响应
            try:
                ai_result = json.loads(response.content)
            except json.JSONDecodeError:
                # 如果AI没有返回有效JSON，使用解析器的预测结果
                ai_result = {
                    "understanding": f"理解指令：{parsed_command.action} {', '.join(parsed_command.targets)}",
                    "execution_process": f"系统正在执行{parsed_command.command_type.value}类型的指令",
                    "result_description": f"指令执行完成，影响了{len(parsed_command.expected_impact)}个社群指标",
                    "stat_changes": parsed_command.expected_impact,
                    "events_generated": [f"执行了{parsed_command.action}指令"],
                    "success": True,
                    "message": "指令执行成功"
                }
            
            return {
                "success": True,
                "message": ai_result.get("message", "指令执行完成"),
                "understanding": ai_result.get("understanding", ""),
                "execution_process": ai_result.get("execution_process", ""),
                "result_description": ai_result.get("result_description", ""),
                "stat_changes": ai_result.get("stat_changes", {}),
                "events_generated": ai_result.get("events_generated", []),
                "command_info": {
                    "original_text": command_text,
                    "parsed_type": parsed_command.command_type.value,
                    "action": parsed_command.action,
                    "targets": parsed_command.targets,
                    "urgency": parsed_command.urgency,
                    "confidence": parsed_command.confidence
                },
                "ai_response_info": {
                    "model": response.model,
                    "response_time": response.response_time,
                    "tokens_used": response.usage.get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"指令执行失败: {str(e)}")
            return {
                "success": False,
                "message": f"指令执行出错: {str(e)}",
                "command_info": {
                    "original_text": command_text
                }
            }
    
    async def generate_agent_response(
        self,
        agent_info: Dict[str, Any],
        user_message: str,
        community_stats: Dict[str, Any],
        recent_events: List[str]
    ) -> Dict[str, Any]:
        """
        生成AI居民聊天响应
        
        Args:
            agent_info: 居民信息
            user_message: 用户消息
            community_stats: 社群状态
            recent_events: 最近事件
            
        Returns:
            Dict: 响应结果
        """
        try:
            response = await self.generate_response(
                "agent_response",
                agent_name=agent_info.get("name", "居民"),
                personality=agent_info.get("personality", "友好"),
                occupation=agent_info.get("occupation", "居民"),
                age=agent_info.get("age", 30),
                interests=", ".join(agent_info.get("interests", ["生活"])),
                happiness=community_stats.get("happiness", 50),
                health=community_stats.get("health", 50),
                education=community_stats.get("education", 50),
                economy=community_stats.get("economy", 50),
                recent_events="\n".join(recent_events[-3:]),  # 最近3个事件
                user_message=user_message
            )
            
            if not response.success:
                return {
                    "success": False,
                    "message": f"AI响应生成失败: {response.error_message}",
                    "agent_response": "抱歉，我现在无法回复。"
                }
            
            return {
                "success": True,
                "agent_response": response.content,
                "agent_info": agent_info,
                "response_info": {
                    "model": response.model,
                    "response_time": response.response_time,
                    "tokens_used": response.usage.get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"AI居民响应生成失败: {str(e)}")
            return {
                "success": False,
                "message": f"响应生成出错: {str(e)}",
                "agent_response": "抱歉，我现在无法回复。"
            }
    
    async def generate_agent_conversation_response(
        self,
        agent_info: Dict[str, Any],
        original_topic: str,
        conversation_history: List[str],
        current_conversation: List[str],
        agent_own_history: List[str],
        community_stats: Dict[str, Any],
        recent_events: List[str],
        is_first_speaker: bool = False
    ) -> Dict[str, Any]:
        """
        生成基于对话历史的居民回复
        
        Args:
            agent_info: 居民信息
            original_topic: 原始话题
            conversation_history: 聊天室的对话历史
            current_conversation: 当前这轮对话中前面居民的发言
            agent_own_history: 该居民自己的历史发言记录
            community_stats: 社群统计数据
            recent_events: 最近事件
            is_first_speaker: 是否是第一个发言的居民
            
        Returns:
            Dict: 包含居民回复的字典
        """
        try:
            # 如果LLM客户端可用，尝试使用LLM生成回复
            if self.client:
                # 构建对话上下文
                context_parts = []
                
                if conversation_history:
                    context_parts.append("最近的聊天记录：")
                    context_parts.extend(conversation_history[-5:])  # 只取最近5条
                
                if current_conversation and not is_first_speaker:
                    context_parts.append("\n本轮对话中前面居民的发言：")
                    context_parts.extend(current_conversation)
                
                # 添加居民自己的历史发言
                if agent_own_history:
                    context_parts.append("\n我自己之前的发言：")
                    context_parts.extend(agent_own_history[-3:])  # 只取最近3条自己的发言
                
                conversation_context = "\n".join(context_parts) if context_parts else "暂无对话历史"
                
                # 使用专门的对话回复提示词
                response = await self.generate_response(
                    "agent_conversation_response",
                    agent_name=agent_info.get("name", "未知居民"),
                    personality=agent_info.get("personality", "友好"),
                    occupation=agent_info.get("occupation", "居民"),
                    age=agent_info.get("age", 30),
                    interests=", ".join(agent_info.get("interests", ["聊天"])),
                    happiness=community_stats.get("happiness", 50),
                    health=community_stats.get("health", 50),
                    education=community_stats.get("education", 50),
                    economy=community_stats.get("economy", 50),
                    recent_events="\n".join(recent_events) if recent_events else "暂无最近事件",
                    original_topic=original_topic,
                    conversation_context=conversation_context,
                    is_first_speaker=is_first_speaker
                )
                
                if response.success:
                    try:
                        # 尝试解析JSON响应
                        response_data = json.loads(response.content)
                        return {
                            "success": True,
                            "agent_response": response_data.get("agent_response", ""),
                            "response_type": response_data.get("response_type", "normal"),
                            "emotion": response_data.get("emotion", "neutral"),
                            "usage": response.usage
                        }
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，直接使用内容作为回复
                        return {
                            "success": True,
                            "agent_response": response.content.strip(),
                            "response_type": "normal",
                            "emotion": "neutral",
                            "usage": response.usage
                        }
            
            # LLM不可用或调用失败时，使用智能备用回复
            self.logger.warning("LLM不可用，使用智能备用回复机制")
            agent_response = self._generate_intelligent_fallback_response(
                agent_info, original_topic, conversation_history, current_conversation, agent_own_history, is_first_speaker
            )
            
            return {
                "success": True,
                "agent_response": agent_response,
                "response_type": "fallback",
                "emotion": "neutral",
                "usage": {}
            }
                
        except Exception as e:
            self.logger.error(f"生成居民对话回复失败: {str(e)}")
            # 最后的备用回复
            agent_response = self._generate_intelligent_fallback_response(
                agent_info, original_topic, conversation_history, current_conversation, agent_own_history, is_first_speaker
            )
            
            return {
                "success": True,
                "agent_response": agent_response,
                "response_type": "fallback",
                "emotion": "neutral",
                "usage": {}
            }
    
    def _generate_intelligent_fallback_response(
        self, 
        agent_info: Dict[str, Any], 
        original_topic: str, 
        conversation_history: List[str], 
        current_conversation: List[str], 
        agent_own_history: List[str],
        is_first_speaker: bool
    ) -> str:
        """
        生成智能的备用回复，基于对话上下文和居民特征，包括自己的历史发言
        """
        import random
        
        agent_name = agent_info.get("name", "居民")
        personality = agent_info.get("personality", "友好")
        occupation = agent_info.get("occupation", "居民")
        
        # 分析原始话题的关键词
        topic_keywords = self._extract_topic_keywords(original_topic)
        
        # 检查是否有自己的历史发言，避免重复
        has_spoken_before = len(agent_own_history) > 0
        
        if is_first_speaker:
            # 第一个发言的居民，主要回应原始话题
            if has_spoken_before:
                # 如果之前说过话，可以引用或补充
                if "发展" in topic_keywords or "社群" in topic_keywords:
                    responses = [
                        f"我是{agent_name}，之前我也关注过这个话题，现在我想补充一些新的想法...",
                        f"我是{agent_name}，基于我之前的观察，我觉得社群发展确实有了新的变化。",
                        f"大家好！我是{agent_name}，结合我之前的经验，我想分享一些关于社群发展的看法。"
                    ]
                else:
                    responses = [
                        f"我是{agent_name}，这个话题让我想起了之前的一些讨论，我想从新的角度来看。",
                        f"我是{agent_name}，虽然之前我们聊过类似的话题，但今天我有了新的想法。",
                        f"大家好！我是{agent_name}，基于我之前的思考，我想分享一些新的观点。"
                    ]
            else:
                # 第一次发言，按原来的逻辑
                if "发展" in topic_keywords or "社群" in topic_keywords:
                    responses = [
                        f"我是{agent_name}，作为{occupation}，我觉得我们社群的发展还是很不错的！大家都很积极参与各种活动。",
                        f"嗨！我是{agent_name}，从我{personality}的角度来看，社群最近的氛围越来越好了，邻里关系也更和谐。",
                        f"大家好！我是{agent_name}，我觉得我们社群在教育、健康等方面都有不少进步，值得高兴！"
                    ]
                elif "天气" in topic_keywords:
                    responses = [
                        f"我是{agent_name}，确实！今天天气特别好，很适合出门活动呢！",
                        f"是啊！我是{agent_name}，这样的好天气让人心情都变好了，我们可以组织一些户外活动。",
                        f"我是{agent_name}，天气好的时候总是让人精神焕发，社群里的大家也都更有活力了！"
                    ]
                elif "计划" in topic_keywords or "周末" in topic_keywords:
                    responses = [
                        f"我是{agent_name}，周末我打算和邻居们一起做些有意义的事情，比如社区志愿活动。",
                        f"我是{agent_name}，作为{occupation}，我周末想组织一些有益的活动，让大家都能参与进来。",
                        f"我是{agent_name}，周末是放松和交流的好时机，我们可以一起规划一些有趣的事情！"
                    ]
                elif "活动" in topic_keywords:
                    responses = [
                        f"我是{agent_name}，我觉得组织活动是个好主意！可以增进大家的感情，让社群更有凝聚力。",
                        f"我是{agent_name}，作为{occupation}，我很支持组织各种活动，这对社群发展很有帮助。",
                        f"我是{agent_name}，活动能让大家更好地了解彼此，我愿意积极参与和协助组织！"
                    ]
                else:
                    responses = [
                        f"我是{agent_name}，对于这个话题，我觉得很有意思！作为{occupation}，我想分享一下我的看法。",
                        f"大家好！我是{agent_name}，这个话题让我想到了很多，我们可以深入讨论一下。",
                        f"我是{agent_name}，从我{personality}的角度来看，这确实是个值得关注的话题。"
                    ]
        else:
            # 后续发言的居民，需要回应前面的对话
            if current_conversation:
                last_speaker = current_conversation[-1].split(":")[0] if ":" in current_conversation[-1] else "前面的朋友"
                last_content = current_conversation[-1].split(":", 1)[1].strip() if ":" in current_conversation[-1] else ""
                
                # 如果之前说过话，可以引用自己的观点
                if has_spoken_before:
                    responses = [
                        f"我是{agent_name}，{last_speaker}的观点很有意思，结合我之前的想法，我觉得...",
                        f"我是{agent_name}，听了{last_speaker}的分享，让我想起了我之前提到的一些观点，现在我想进一步补充...",
                        f"我是{agent_name}，{last_speaker}说得很好，这和我之前的思考有些相似，我想从另一个角度来看..."
                    ]
                else:
                    # 基于前面的发言内容生成回应
                    if "同意" in last_content or "支持" in last_content:
                        responses = [
                            f"我也同意{last_speaker}的观点！我是{agent_name}，我想补充一点...",
                            f"是的，{last_speaker}说得很对。我是{agent_name}，从{occupation}的角度来看，这确实很重要。",
                            f"我是{agent_name}，{last_speaker}的想法很好，我们可以一起努力实现这些目标。"
                        ]
                    elif "活动" in last_content or "组织" in last_content:
                        responses = [
                            f"我是{agent_name}，听了{last_speaker}的建议，我觉得我们可以从小事做起，逐步扩大活动规模。",
                            f"好主意！我是{agent_name}，作为{occupation}，我可以贡献一些专业知识来支持这些活动。",
                            f"我是{agent_name}，{last_speaker}提到的活动让我很感兴趣，我愿意积极参与！"
                        ]
                    else:
                        responses = [
                            f"我是{agent_name}，听了{last_speaker}的分享，我也想说说我的想法...",
                            f"有趣的观点！我是{agent_name}，我想从另一个角度来看这个问题。",
                            f"我是{agent_name}，{last_speaker}说得很有道理，让我想到了一些相关的经历。"
                        ]
            else:
                responses = [
                    f"我是{agent_name}，虽然我不是第一个发言，但我也想分享一下我的看法。",
                    f"我是{agent_name}，作为{occupation}，我觉得这个话题很值得讨论。",
                    f"大家好！我是{agent_name}，听了前面的讨论，我也有一些想法要分享。"
                ]
        
        return random.choice(responses)
    
    def _extract_topic_keywords(self, topic: str) -> List[str]:
        """从话题中提取关键词"""
        keywords = []
        topic_lower = topic.lower()
        
        keyword_list = [
            "发展", "社群", "天气", "计划", "周末", "活动", "组织", "讨论", 
            "建议", "想法", "问题", "解决", "改善", "提升", "合作", "参与"
        ]
        
        for keyword in keyword_list:
            if keyword in topic_lower:
                keywords.append(keyword)
        
        return keywords
    
    async def analyze_community(
        self,
        community_stats: Dict[str, Any],
        stat_changes: Dict[str, int],
        recent_events: List[str]
    ) -> Dict[str, Any]:
        """
        分析社群状态
        
        Args:
            community_stats: 当前社群状态
            stat_changes: 各项指标变化
            recent_events: 最近事件
            
        Returns:
            Dict: 分析结果
        """
        try:
            response = await self.generate_response(
                "community_analysis",
                population=community_stats.get("population", 100),
                happiness=community_stats.get("happiness", 50),
                health=community_stats.get("health", 50),
                education=community_stats.get("education", 50),
                economy=community_stats.get("economy", 50),
                happiness_change=stat_changes.get("happiness", 0),
                health_change=stat_changes.get("health", 0),
                education_change=stat_changes.get("education", 0),
                economy_change=stat_changes.get("economy", 0),
                recent_events="\n".join(recent_events[-7:])  # 最近7个事件
            )
            
            if not response.success:
                return {
                    "success": False,
                    "message": f"社群分析失败: {response.error_message}"
                }
            
            try:
                analysis_result = json.loads(response.content)
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "response_info": {
                        "model": response.model,
                        "response_time": response.response_time,
                        "tokens_used": response.usage.get("total_tokens", 0)
                    }
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": "AI分析结果格式错误",
                    "raw_response": response.content
                }
                
        except Exception as e:
            self.logger.error(f"社群分析失败: {str(e)}")
            return {
                "success": False,
                "message": f"分析出错: {str(e)}"
            }
    
    def get_client_status(self) -> Dict[str, Any]:
        """获取客户端状态"""
        is_valid, config_message = validate_llm_config()
        
        return {
            "client_initialized": self.client is not None,
            "config_valid": is_valid,
            "config_message": config_message,
            "provider": self.config.provider.value,
            "model": self.config.model,
            "rate_limits": {
                "requests_per_minute": self.config.rate_limit_requests_per_minute,
                "tokens_per_minute": self.config.rate_limit_tokens_per_minute
            }
        }

# 全局响应生成器实例
response_generator = ResponseGenerator() 