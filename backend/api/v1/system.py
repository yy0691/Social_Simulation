"""
系统状态API - 提供LLM连接状态和系统诊断功能
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import asyncio
import logging

from modules.llm import get_llm_config, validate_llm_config, response_generator, command_parser
from modules.simulation import community_simulation

router = APIRouter(prefix="/system", tags=["system"])

# 配置日志
logger = logging.getLogger(__name__)

@router.get("/llm/status")
async def get_llm_status():
    """获取LLM连接状态"""
    try:
        # 基础配置检查
        config = get_llm_config()
        is_valid, message = validate_llm_config()
        client_status = response_generator.get_client_status()
        
        return {
            "success": True,
            "data": {
                "config_valid": is_valid,
                "config_message": message,
                "client_initialized": client_status["client_initialized"],
                "provider": client_status["provider"],
                "model": client_status["model"],
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "timeout": config.timeout,
                "rate_limits": {
                    "requests_per_minute": config.rate_limit_requests_per_minute,
                    "tokens_per_minute": config.rate_limit_tokens_per_minute
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取LLM状态失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.post("/llm/test")
async def test_llm_connection():
    """测试LLM连接和功能"""
    test_results = {
        "config_check": False,
        "client_init": False,
        "api_call": False,
        "command_parse": False,
        "agent_response": False,
        "overall_success": False,
        "logs": [],
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 1. 配置检查
        test_results["logs"].append("开始配置检查...")
        is_valid, message = validate_llm_config()
        if is_valid:
            test_results["config_check"] = True
            test_results["logs"].append(f"✅ 配置验证通过: {message}")
        else:
            test_results["errors"].append(f"❌ 配置验证失败: {message}")
            
        # 2. 客户端初始化检查
        test_results["logs"].append("检查客户端初始化...")
        client_status = response_generator.get_client_status()
        if client_status["client_initialized"]:
            test_results["client_init"] = True
            test_results["logs"].append("✅ 客户端初始化成功")
        else:
            test_results["errors"].append("❌ 客户端初始化失败")
        
        # 3. API调用测试
        if test_results["config_check"] and test_results["client_init"]:
            test_results["logs"].append("测试API调用...")
            try:
                config = get_llm_config()
                test_messages = [
                    {"role": "system", "content": "你是一个测试助手，请简洁回复。"},
                    {"role": "user", "content": "请回复'连接测试成功'"}
                ]
                
                response = await response_generator.client.chat.completions.create(
                    model=config.model,
                    messages=test_messages,
                    max_tokens=50,
                    temperature=0.1
                )
                
                reply = response.choices[0].message.content.strip()
                test_results["api_call"] = True
                test_results["logs"].append(f"✅ API调用成功，回复: {reply}")
                
                # 记录token使用
                if hasattr(response, 'usage') and response.usage:
                    test_results["logs"].append(f"📊 Token使用: {response.usage.total_tokens}")
                
            except Exception as api_error:
                test_results["errors"].append(f"❌ API调用失败: {str(api_error)}")
        
        # 4. 指令解析测试
        test_results["logs"].append("测试指令解析功能...")
        try:
            test_command = "组织一次社区聚会活动"
            parsed = command_parser.parse_command(test_command)
            test_results["command_parse"] = True
            test_results["logs"].append(f"✅ 指令解析成功: {parsed.command_type.value}")
        except Exception as parse_error:
            test_results["errors"].append(f"❌ 指令解析失败: {str(parse_error)}")
        
        # 5. 居民对话测试
        if test_results["api_call"]:
            test_results["logs"].append("测试居民对话生成...")
            try:
                test_agent_info = {
                    "name": "测试居民",
                    "personality": "友善",
                    "occupation": "教师",
                    "age": 30
                }
                
                agent_response = await response_generator.generate_agent_response(
                    agent_info=test_agent_info,
                    user_message="你好，今天过得怎么样？",
                    community_stats={"happiness": 70, "health": 80, "education": 75, "economy": 65},
                    recent_events=["社区举办了读书活动"]
                )
                
                if agent_response["success"]:
                    test_results["agent_response"] = True
                    response_preview = agent_response["agent_response"][:50] + "..."
                    test_results["logs"].append(f"✅ 居民对话生成成功: {response_preview}")
                else:
                    test_results["errors"].append(f"❌ 居民对话生成失败: {agent_response['message']}")
                    
            except Exception as agent_error:
                test_results["errors"].append(f"❌ 居民对话测试失败: {str(agent_error)}")
        
        # 计算总体成功状态
        test_results["overall_success"] = (
            test_results["config_check"] and 
            test_results["client_init"] and 
            test_results["api_call"]
        )
        
        if test_results["overall_success"]:
            test_results["logs"].append("🎉 所有核心功能测试通过！")
        else:
            test_results["logs"].append("⚠️ 部分功能测试失败，请检查配置")
        
        return {
            "success": True,
            "data": test_results
        }
        
    except Exception as e:
        test_results["errors"].append(f"测试过程异常: {str(e)}")
        return {
            "success": False,
            "data": test_results,
            "error": str(e)
        }

@router.get("/status/full")
async def get_full_system_status():
    """获取完整系统状态"""
    try:
        # LLM状态
        llm_status_response = await get_llm_status()
        llm_status = llm_status_response["data"] if llm_status_response["success"] else None
        
        # 模拟系统状态
        simulation_status = community_simulation.get_simulation_status()
        
        # 社群统计
        try:
            community_stats = await community_simulation.get_community_stats()
        except:
            community_stats = None
        
        # 数据库状态
        from modules.shared.database import SessionLocal, CommunityStats
        db_status = "disconnected"
        try:
            db = SessionLocal()
            db.query(CommunityStats).first()
            db_status = "connected"
            db.close()
        except:
            db_status = "error"
        
        return {
            "success": True,
            "data": {
                "timestamp": datetime.now().isoformat(),
                "llm": llm_status,
                "simulation": simulation_status,
                "community": community_stats,
                "database": {
                    "status": db_status
                },
                "system": {
                    "uptime": "运行中",
                    "version": "1.0.0"
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取系统状态失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/logs/recent")
async def get_recent_logs(lines: int = 50):
    """获取最近的系统日志"""
    try:
        # 这里可以读取日志文件或内存中的日志
        # 暂时返回模拟数据
        logs = [
            f"{datetime.now().isoformat()} - INFO - 系统运行正常",
            f"{datetime.now().isoformat()} - INFO - LLM配置已加载",
            f"{datetime.now().isoformat()} - INFO - 模拟引擎运行中"
        ]
        
        return {
            "success": True,
            "data": {
                "logs": logs[-lines:],
                "total_lines": len(logs),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取日志失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        } 