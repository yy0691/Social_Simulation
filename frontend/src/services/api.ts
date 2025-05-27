/**
 * AI社群模拟小游戏 - API服务层
 * 封装所有与后端API的交互逻辑
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { 
  CommunityStats, 
  Agent, 
  Event, 
  CommandRequest, 
  CommandResponse,
  ApiResponse,
  ChatMessage
} from '../types';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// 创建axios实例
class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log(`🚀 API请求: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ API请求错误:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API响应: ${response.config.url} - ${response.status}`);
        return response;
      },
      (error) => {
        console.error('❌ API响应错误:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // 通用GET请求
  private async get<T>(url: string): Promise<T> {
    const response = await this.client.get<T>(url);
    return response.data;
  }

  // 通用POST请求
  private async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  // 健康检查
  async healthCheck(): Promise<any> {
    return this.get('/api/v1/health');
  }

  // 获取问候信息
  async getGreeting(): Promise<any> {
    return this.get('/api/v1/greeting');
  }

  // 获取社群状态
  async getCommunityStatus(): Promise<CommunityStats> {
    return this.get('/api/v1/community/status');
  }

  // 获取AI居民列表
  async getAgents(): Promise<{ agents: Agent[]; total_count: number }> {
    return this.get('/api/v1/community/agents');
  }

  // 获取事件历史
  async getEvents(limit: number = 10, offset: number = 0): Promise<{ 
    events: Event[]; 
    limit: number; 
    offset: number; 
  }> {
    return this.get(`/api/v1/community/events?limit=${limit}&offset=${offset}`);
  }

  // 获取统计汇总
  async getStatsSummary(): Promise<{
    community_stats: CommunityStats;
    totals: {
      agents: number;
      events: number;
    };
    last_updated: string;
  }> {
    return this.get('/api/v1/community/stats/summary');
  }

  // 执行玩家指令
  async executeCommand(request: CommandRequest): Promise<CommandResponse> {
    return this.post('/api/v1/commands/execute', request);
  }

  // 获取指令历史
  async getCommandHistory(limit: number = 10): Promise<{
    commands: Array<{
      id: number;
      command: string;
      type: string;
      impact: any;
      timestamp: string;
    }>;
  }> {
    return this.get(`/api/v1/commands/history?limit=${limit}`);
  }

  // 测试连接
  async testConnection(): Promise<boolean> {
    try {
      await this.get('/');
      return true;
    } catch (error) {
      console.error('连接测试失败:', error);
      return false;
    }
  }

  // 获取API文档
  getDocsUrl(): string {
    return `${API_BASE_URL}/docs`;
  }

  // 获取ReDoc文档
  getRedocUrl(): string {
    return `${API_BASE_URL}/redoc`;
  }
}

// 创建并导出API服务实例
export const api = new ApiService();
export default api; 