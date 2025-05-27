"""
AI社群模拟小游戏 - 后端主入口文件
使用FastAPI框架构建的RESTful API服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
from datetime import datetime

# 导入API路由
from api.v1 import community, commands

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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # 允许前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(community.router, prefix="/api/v1")
app.include_router(commands.router, prefix="/api/v1")

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
        print(f"数据库连接检查失败: {str(e)}")
        db_status = "error"
    
    return {
        "status": "ok",
        "service": "ai-community-game-api",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "llm": "not_configured"       # 稍后实现
        }
    }

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
    # 记录应用启动
    print("🚀 AI社群模拟小游戏API服务启动中...")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    ) 