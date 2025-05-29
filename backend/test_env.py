#!/usr/bin/env python3
"""
测试环境变量加载
"""

import os
from pathlib import Path

def load_env():
    """加载.env文件中的环境变量"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            # 尝试UTF-8编码
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                # 如果UTF-8失败，尝试GBK编码
                with open(env_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果还是失败，尝试latin-1编码
                with open(env_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        
        # 解析环境变量
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")  # 去除引号
                print(f"  设置环境变量: {key}={value}")
                os.environ[key] = value
                # 立即验证是否设置成功
                actual_value = os.getenv(key)
                print(f"  验证结果: {key}={actual_value}")
                if actual_value != value:
                    print(f"  ⚠️ 警告: 设置失败！期望={value}, 实际={actual_value}")
        
        print(f"✅ 已加载环境变量文件: {env_path}")
    else:
        print(f"⚠️ 环境变量文件不存在: {env_path}")

if __name__ == "__main__":
    print("🔍 测试环境变量加载...")
    print("加载前:")
    print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL')}")
    
    load_env()
    
    print("\n立即检查:")
    print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    
    print("\n加载后:")
    print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL')}")
    print(f"  LLM_MAX_TOKENS: {os.getenv('LLM_MAX_TOKENS')}")
    print(f"  LLM_TEMPERATURE: {os.getenv('LLM_TEMPERATURE')}")
    
    # 测试LLM配置
    print("\n🧪 测试LLM配置读取...")
    from modules.llm.config import get_llm_config, validate_llm_config
    
    config = get_llm_config()
    is_valid, message = validate_llm_config()
    
    print(f"配置有效: {is_valid}")
    print(f"配置消息: {message}")
    print(f"API密钥: {config.api_key}")
    print(f"模型: {config.model}")
    print(f"最大Token: {config.max_tokens}")
    print(f"温度: {config.temperature}") 