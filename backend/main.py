"""
AI社群模拟小游戏 - 后端主入口文件
使用FastAPI框架构建的RESTful API服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

# 创建FastAPI应用实例
app = FastAPI(
    title="AI社群模拟小游戏API",
    description="基于LLM的社群模拟游戏后端API服务",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# 配置CORS跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 允许前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "version": "1.0.0"
    }

# API版本前缀路由
@app.get("/api/v1/health")
async def health_check():
    """
    详细健康检查接口
    """
    return {
        "status": "ok",
        "service": "ai-community-game-api",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "not_connected",  # 稍后实现
            "llm": "not_configured"       # 稍后实现
        }
    }

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
        "tips": [
            "输入指令来影响AI社群的行为",
            "观察社群统计数据的变化",
            "与AI居民聊天互动"
        ]
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
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
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    ) 