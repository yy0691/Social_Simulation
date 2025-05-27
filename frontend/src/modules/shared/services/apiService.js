import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    console.log('发送API请求:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求配置错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应成功:', response.status, response.config.url)
    return response.data
  },
  (error) => {
    console.error('API响应错误:', error.response?.status, error.message)
    
    // 统一错误处理
    if (error.response) {
      switch (error.response.status) {
        case 400:
          console.error('请求参数错误')
          break
        case 401:
          console.error('未授权访问')
          break
        case 403:
          console.error('禁止访问')
          break
        case 404:
          console.error('接口不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error('未知错误')
      }
    } else if (error.request) {
      console.error('网络连接错误')
    }
    
    return Promise.reject(error)
  }
)

// API服务类
class ApiService {
  // 基础API调用
  async get(url, params = {}) {
    return await api.get(url, { params })
  }
  
  async post(url, data = {}) {
    return await api.post(url, data)
  }
  
  async put(url, data = {}) {
    return await api.put(url, data)
  }
  
  async delete(url) {
    return await api.delete(url)
  }
  
  // 业务API方法
  
  // 获取问候信息
  async getGreeting() {
    return await this.get('/greeting')
  }
  
  // 获取社群状态
  async getCommunityStats() {
    return await this.get('/community/stats')
  }
  
  // 执行玩家指令
  async executeCommand(command) {
    return await this.post('/command', { command })
  }
  
  // 获取事件历史
  async getEvents(limit = 10) {
    return await this.get('/events', { limit })
  }
  
  // 获取聊天记录
  async getChatMessages(limit = 20) {
    return await this.get('/chat/messages', { limit })
  }
  
  // 发送聊天消息
  async sendChatMessage(message) {
    return await this.post('/chat/send', { message })
  }
  
  // 获取AI居民信息
  async getAgents() {
    return await this.get('/agents')
  }
  
  // 健康检查
  async healthCheck() {
    return await this.get('/health')
  }
}

// 创建实例并导出
const apiService = new ApiService()

export default apiService

// 也可以单独导出API方法
export const {
  getGreeting,
  getCommunityStats,
  executeCommand,
  getEvents,
  getChatMessages,
  sendChatMessage,
  getAgents,
  healthCheck
} = apiService 