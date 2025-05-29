"""
AI模块 - AI相关功能
包含LLM集成、聊天处理等功能
"""

from .enhanced_local_chat import enhanced_local_chat
from .realistic_chat_system import realistic_chat_system
from .chat_handler import ChatHandler
from .optimized_chat_system import optimized_chat_system
from .smart_chat_handler import smart_chat_handler

# 创建实例
chat_handler = ChatHandler()

__all__ = [
    'enhanced_local_chat',
    'realistic_chat_system', 
    'chat_handler',
    'optimized_chat_system',
    'smart_chat_handler'
] 