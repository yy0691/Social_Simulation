#!/bin/bash

echo "🚀 启动AI社群聊天室服务..."

# 检查后端虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "❌ 后端虚拟环境不存在，请先运行: cd backend && python3 -m venv venv"
    exit 1
fi

# 启动后端服务
echo "📡 启动后端API服务..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端是否启动成功
if curl -s http://127.0.0.1:8000/api/v1/health > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 启动前端服务
echo "🎨 启动前端开发服务器..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "🎉 服务启动完成！"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端API: http://127.0.0.1:8000"
echo "📖 API文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务..."

# 等待中断信号
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ 所有服务已停止"; exit 0' INT

# 保持脚本运行
wait 