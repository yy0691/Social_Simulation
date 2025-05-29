/**
 * AI社群模拟小游戏 - 类型定义文件
 * 定义整个项目使用的TypeScript接口和类型
 */

// 社群统计数据接口
export interface CommunityStats {
  population: number;
  happiness: number;
  health: number;
  education: number;
  economy: number;
  simulation?: {
    is_running: boolean;
    agent_count: number;
    last_update: string;
    auto_event_interval_hours: number;
    recent_event_count: number;
  };
  last_updated: string;
}

// AI居民信息接口
export interface Agent {
  id: number;
  name: string;
  personality: string;
  role: string;
  mood: number;
  activity_level: number;
  created_at: string;
  last_active: string | null;
}

// 事件记录接口
export interface Event {
  id: number;
  type: string;
  description: string;
  impact: {
    happiness?: number;
    activity?: number;
    resources?: number;
  };
  timestamp: string;
}

// 指令请求接口
export interface CommandRequest {
  command: string;
  description?: string;
}

// 指令响应接口
export interface CommandResponse {
  success: boolean;
  command: string;
  impact_type: string;
  changes: {
    happiness: number;
    activity: number;
  };
  new_stats: {
    happiness: number;
    activity: number;
  };
  message: string;
}

// API响应基础接口
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

// 聊天消息接口
export interface ChatMessage {
  id: number;
  sender: string;
  message: string;
  timestamp: string;
  type: 'user' | 'ai' | 'system';
  isAgent?: boolean;
}

// 应用状态接口
export interface AppState {
  isConnected: boolean;
  isLoading: boolean;
  currentView: 'community' | 'chat' | 'invitation' | 'settings' | 'showcase';
  theme: 'dark' | 'light';
}

// 设置选项接口
export interface Settings {
  theme: 'dark' | 'light';
  autoRefresh: boolean;
  refreshInterval: number;
  soundEnabled: boolean;
  animationsEnabled: boolean;
  compactMode: boolean;
}

// 导航项目接口
export interface NavItem {
  key: string;
  label: string;
  icon: string;
  component: string;
}

// 通知消息接口
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  timestamp: string;
} 