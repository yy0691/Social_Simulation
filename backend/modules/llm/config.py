"""
LLM配置模块
包含OpenAI API配置和其他LLM相关设置
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    """LLM提供商枚举"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai" 
    CLAUDE = "claude"
    LOCAL = "local"

@dataclass
class LLMConfig:
    """LLM配置类"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    
    # Azure OpenAI 特定配置
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    api_version: str = "2023-12-01-preview"
    
    # 请求限流配置
    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_minute: int = 90000

class LLMConfigManager:
    """LLM配置管理器"""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> LLMConfig:
        """获取配置，每次都重新加载以确保获取最新环境变量"""
        return self._load_config()
    
    def _load_config(self) -> LLMConfig:
        """从环境变量和配置文件加载配置"""
        
        # 确定提供商
        provider_str = os.getenv("LLM_PROVIDER", "openai").lower()
        provider = LLMProvider.OPENAI
        for p in LLMProvider:
            if p.value == provider_str:
                provider = p
                break
        
        # 获取API密钥，支持多种环境变量名
        api_key = (
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("LLM_API_KEY") or 
            os.getenv("API_KEY")
        )
        
        config = LLMConfig(
            provider=provider,
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            timeout=int(os.getenv("LLM_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
            
            # Azure配置
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
            
            # 限流配置
            rate_limit_requests_per_minute=int(os.getenv("LLM_RATE_LIMIT_RPM", "60")),
            rate_limit_tokens_per_minute=int(os.getenv("LLM_RATE_LIMIT_TPM", "90000"))
        )
        
        return config
    
    def get_client_config(self) -> Dict[str, Any]:
        """获取客户端配置字典"""
        if self.config.provider == LLMProvider.OPENAI:
            config_dict = {
                "api_key": self.config.api_key,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries
            }
            if self.config.base_url:
                config_dict["base_url"] = self.config.base_url
            return config_dict
            
        elif self.config.provider == LLMProvider.AZURE_OPENAI:
            return {
                "api_key": self.config.api_key,
                "azure_endpoint": self.config.azure_endpoint,
                "api_version": self.config.api_version,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries
            }
        
        return {}
    
    def validate_config(self) -> tuple[bool, str]:
        """验证配置是否有效"""
        if not self.config.api_key:
            return False, "缺少API密钥配置"
        
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            if not self.config.azure_endpoint:
                return False, "Azure OpenAI 需要配置 endpoint"
            if not self.config.azure_deployment:
                return False, "Azure OpenAI 需要配置 deployment"
        
        if self.config.max_tokens <= 0:
            return False, "max_tokens 必须大于0"
        
        if not (0 <= self.config.temperature <= 2):
            return False, "temperature 必须在0-2之间"
        
        return True, "配置有效"

# 全局配置实例
llm_config_manager = LLMConfigManager()

def get_llm_config() -> LLMConfig:
    """获取LLM配置"""
    return llm_config_manager.config

def validate_llm_config() -> tuple[bool, str]:
    """验证LLM配置"""
    return llm_config_manager.validate_config() 