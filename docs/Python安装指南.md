# Python安装和依赖配置指南

## 📋 当前状态
✅ **Python 3.13 已安装并配置完成**
✅ **虚拟环境已创建并激活**
✅ **所有项目依赖已安装**
✅ **FastAPI服务器正常运行**
✅ **API端点测试通过**

---

## 🐍 第一步：安装Python

### Windows系统安装方法

#### 方法1：官网下载（推荐）
1. **访问Python官网**: https://www.python.org/downloads/
2. **下载最新版本**: 建议下载Python 3.11或3.12版本
3. **运行安装程序**:
   - ✅ **重要**：勾选"Add Python to PATH"
   - ✅ 勾选"Install for all users"（可选）
   - 点击"Install Now"

#### 方法2：Microsoft Store
1. 打开Microsoft Store
2. 搜索"Python 3.11"
3. 点击"获取"并安装

#### 方法3：Chocolatey（高级用户）
```powershell
# 先安装Chocolatey (如果没有)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装Python
choco install python
```

---

## 🔍 第二步：验证安装

安装完成后，**重新打开PowerShell**并运行：

```powershell
# 检查Python版本
python --version
# 或
python3 --version
# 或
py --version

# 检查pip版本
pip --version
```

**期望输出**：
```
Python 3.11.x (或更高版本)
pip 23.x.x (或更高版本)
```

---

## 🚀 第三步：安装项目依赖

验证Python安装成功后，在backend目录运行以下命令：

### 1. 创建虚拟环境（推荐）
```powershell
# 进入backend目录
cd E:\blog\SimGame\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 你会看到命令提示符前面有 (venv) 标识
```

### 2. 升级pip（可选但推荐）
```powershell
python -m pip install --upgrade pip
```

### 3. 安装项目依赖
```powershell
pip install -r requirements.txt
```

### 4. 验证安装
```powershell
# 检查已安装的包
pip list

# 应该看到以下包：
# fastapi==0.104.1
# uvicorn==0.24.0
# sqlalchemy==2.0.23
# python-multipart==0.0.6
# python-dotenv==1.0.0
# openai==1.3.6
# pydantic==2.5.0
# httpx==0.25.2
```

---

## 🧪 第四步：测试安装

### 1. 初始化数据库
```powershell
python -m modules.shared.init_data
```

### 2. 启动FastAPI服务器
```powershell
python main.py
```

**期望输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using StatReload
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. 访问API文档
在浏览器中打开：
- http://127.0.0.1:8000/docs (Swagger UI)
- http://127.0.0.1:8000/redoc (ReDoc)

---

## 🐛 常见问题排查

### 问题1：Python命令不被识别
**症状**：`'python' 不是内部或外部命令`

**解决方法**：
1. 确认Python已安装
2. 重新安装Python，确保勾选"Add Python to PATH"
3. 手动添加Python到PATH：
   ```
   控制面板 → 系统 → 高级系统设置 → 环境变量
   在"系统变量"中找到"Path"
   添加Python安装路径（通常是 C:\Python311\ 或 C:\Users\用户名\AppData\Local\Programs\Python\Python311\）
   ```

### 问题2：pip安装失败
**症状**：`ERROR: Could not install packages`

**解决方法**：
```powershell
# 升级pip
python -m pip install --upgrade pip

# 使用清华源加速下载
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：虚拟环境无法激活
**症状**：`无法加载文件 venv\Scripts\Activate.ps1`

**解决方法**：
```powershell
# 修改PowerShell执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后重新激活
venv\Scripts\activate
```

### 问题4：端口被占用
**症状**：`ERROR: [Errno 10048] Only one usage of each socket address`

**解决方法**：
```powershell
# 查看端口占用
netstat -ano | findstr :8000

# 结束占用进程
taskkill /PID <进程ID> /F

# 或者修改端口
uvicorn main:app --reload --port 8001
```

---

## 📝 下一步操作

Python依赖安装完成后，您可以：

1. ✅ 初始化数据库
2. ✅ 启动后端API服务器
3. ✅ 开始前端开发
4. ✅ 测试前后端连接

---

## 🎯 项目进度更新

✅ **已完成的后端配置**：
- ✅ Python 3.13 环境配置
- ✅ 虚拟环境创建和激活
- ✅ FastAPI 项目搭建
- ✅ 项目依赖安装 (FastAPI, SQLAlchemy, OpenAI等)
- ✅ API 基础结构搭建
- ✅ CORS 跨域配置
- ✅ 健康检查端点测试通过
- ✅ 问候接口测试通过

## ✅ API测试结果

**根路径 (/)**: 
- 状态码: 200 ✅
- 响应: AI社群模拟小游戏API服务运行中

**健康检查 (/api/v1/health)**:
- 状态码: 200 ✅
- 响应: 服务状态正常

**问候接口 (/api/v1/greeting)**:
- 状态码: 200 ✅
- 响应: 欢迎消息和使用提示

---

**创建时间**: 2024年
**最后更新**: 当前时间
**版本**: v1.0 