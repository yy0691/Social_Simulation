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
                temperature=self.config.temperature,
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