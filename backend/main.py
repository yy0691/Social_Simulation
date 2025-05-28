"""
AI社群模拟小游戏 - 后端主入口文件
使用FastAPI框架构建的RESTful API服务
"""

# 加载环境变量文件
import os
from pathlib import Path

# 加载.env文件
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
                os.environ[key] = value
                print(f"  {key}={value}")
        
        print(f"✅ 已加载环境变量文件: {env_path}")
    else:
        print(f"⚠️ 环境变量文件不存在: {env_path}")

# 在导入其他模块之前加载环境变量
load_env()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import asyncio
import logging
from datetime import datetime

# 导入API路由
from api.v1 import community, commands, chat, system

# 导入模拟和LLM模块
from modules.simulation import community_simulation
from modules.llm import validate_llm_config, response_generator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="AI社群模拟小游戏API",
    description="基于LLM的社群模拟游戏后端API服务",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url=None  # 禁用默认ReDoc，使用自定义
)

# 暂时注释掉中间件
# app.add_middleware(ErrorHandlingMiddleware)
# app.add_middleware(RequestLoggingMiddleware)
# app.add_middleware(PerformanceMiddleware, slow_request_threshold=2.0)

# 配置CORS跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],  # 允许前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(community.router, prefix="/api/v1")
app.include_router(commands.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")

# 启动事件处理
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的初始化任务"""
    logger.info("🚀 AI社群模拟小游戏API服务启动中...")
    
    try:
        # 验证LLM配置
        is_valid, config_message = validate_llm_config()
        if is_valid:
            logger.info("✅ LLM配置验证成功")
        else:
            logger.warning(f"⚠️ LLM配置问题: {config_message}")
        
        # 启动社群模拟
        await community_simulation.start_simulation()
        logger.info("✅ AI社群模拟引擎已启动")
        
        # 检查数据库连接
        from modules.shared.database import SessionLocal, CommunityStats
        try:
            db = SessionLocal()
            db.query(CommunityStats).first()
            db.close()
            logger.info("✅ 数据库连接正常")
        except Exception as db_error:
            logger.error(f"❌ 数据库连接失败: {str(db_error)}")
        
        logger.info("🎉 所有服务初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 启动过程中发生错误: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的清理任务"""
    logger.info("🛑 AI社群模拟小游戏API服务关闭中...")
    
    try:
        # 停止社群模拟
        await community_simulation.stop_simulation()
        logger.info("✅ AI社群模拟引擎已停止")
        
    except Exception as e:
        logger.error(f"❌ 关闭过程中发生错误: {str(e)}")

# 根路径 - 健康检查接口
@app.get("/")
async def read_root():
    """
    健康检查接口
    返回API状态和基本信息
    """
    return {
        "message": "AI社群模拟小游戏API服务运行中",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "simulation_running": community_simulation.simulation_running
    }

# API版本前缀路由
@app.get("/api/v1/health")
async def health_check():
    """
    详细健康检查接口
    """
    from modules.shared.database import SessionLocal, CommunityStats
    
    # 检查数据库连接
    db_status = "disconnected"
    try:
        db = SessionLocal()
        # 尝试查询以测试连接
        db.query(CommunityStats).first()
        db_status = "connected"
        db.close()
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        db_status = "error"
    
    # 检查LLM配置
    is_llm_valid, llm_message = validate_llm_config()
    llm_status = "configured" if is_llm_valid else "not_configured"
    
    # 获取LLM客户端状态
    llm_client_status = response_generator.get_client_status()
    
    # 获取模拟状态
    simulation_status = community_simulation.get_simulation_status()
    
    return {
        "status": "ok",
        "service": "ai-community-game-api",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "llm": llm_status,
            "llm_client": llm_client_status,
            "simulation": simulation_status
        },
        "messages": {
            "llm_config": llm_message
        }
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    """获取系统全面状态信息"""
    try:
        # 获取社群统计
        community_stats = await community_simulation.get_community_stats()
        
        # 获取模拟状态
        simulation_status = community_simulation.get_simulation_status()
        
        # 获取LLM状态
        llm_client_status = response_generator.get_client_status()
        
        # 获取最近事件
        recent_events = await community_simulation.get_recent_events(5)
        
        # 获取居民数量
        agents = community_simulation.get_all_agents()
        active_agents = [agent for agent in agents if agent.is_active]
        
        return {
            "success": True,
            "data": {
                "community_stats": community_stats,
                "simulation_status": simulation_status,
                "llm_client_status": llm_client_status,
                "recent_events": recent_events,
                "agents_info": {
                    "total_agents": len(agents),
                    "active_agents": len(active_agents),
                    "agent_names": [agent.name for agent in active_agents]
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"获取系统状态失败: {str(e)}"
            }
        )

# 自定义ReDoc路由 - 使用本地CDN
@app.get("/redoc", response_class=HTMLResponse)
async def redoc_html():
    """
    自定义ReDoc页面，使用多个CDN备用源
    解决CDN访问问题
    """
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI社群模拟小游戏API - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body { margin: 0; padding: 0; }
                redoc { display: block; }
            </style>
        </head>
        <body>
            <div id="redoc-container"></div>
            <script>
                // 多个CDN备用源
                const cdnSources = [
                    'https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js',
                    'https://unpkg.com/redoc/bundles/redoc.standalone.js',
                    'https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js'
                ];
                
                function loadReDoc(srcIndex = 0) {
                    if (srcIndex >= cdnSources.length) {
                        document.getElementById('redoc-container').innerHTML = 
                            '<div style="padding: 40px; text-align: center; font-family: sans-serif;">' +
                            '<h2>ReDoc 加载失败</h2>' +
                            '<p>无法从CDN加载ReDoc资源，请检查网络连接。</p>' +
                            '<p>您可以访问 <a href="/docs">Swagger UI</a> 查看API文档。</p>' +
                            '</div>';
                        return;
                    }
                    
                    const script = document.createElement('script');
                    script.src = cdnSources[srcIndex];
                    script.onload = function() {
                        Redoc.init('/openapi.json', {
                            scrollYOffset: 50,
                            theme: {
                                colors: {
                                    primary: {
                                        main: '#1976d2'
                                    }
                                }
                            }
                        }, document.getElementById('redoc-container'));
                    };
                    script.onerror = function() {
                        console.log('CDN源 ' + (srcIndex + 1) + ' 失败，尝试下一个...');
                        loadReDoc(srcIndex + 1);
                    };
                    document.head.appendChild(script);
                }
                
                loadReDoc();
            </script>
        </body>
    </html>
    """

# 问候接口 - 获取欢迎信息
@app.get("/api/v1/greeting")
async def get_greeting():
    """
    获取问候信息
    返回游戏欢迎消息
    """
    return {
        "message": "欢迎来到AI社群模拟小游戏！",
        "description": "在这里你可以与AI居民互动，观察社群的发展和演化。",
        "features": [
            "📝 输入指令来影响AI社群的行为",
            "📊 观察社群统计数据的变化", 
            "💬 与AI居民聊天互动",
            "🎭 体验AI居民的个性化反应",
            "🎲 观察随机事件对社群的影响"
        ],
        "simulation_running": community_simulation.simulation_running,
        "agent_count": len(community_simulation.get_all_agents())
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "服务器内部错误，请稍后重试",
            "timestamp": datetime.now().isoformat()
        }
    )

# 启动配置
if __name__ == "__main__":
    # 记录应用启动
    print("🚀 AI社群模拟小游戏API服务启动中...")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    ) 