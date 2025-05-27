/**
 * AI社群模拟小游戏 - 社群状态管理
 * 使用Pinia管理社群相关的状态和数据
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import type { CommunityStats, Agent, Event, CommandRequest, CommandResponse } from '../types';

export const useCommunityStore = defineStore('community', () => {
  // 状态变量
  const stats = ref<CommunityStats | null>(null);
  const agents = ref<Agent[]>([]);
  const events = ref<Event[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const lastUpdated = ref<Date | null>(null);

  // 计算属性
  const isHealthy = computed(() => {
    if (!stats.value) return false;
    return stats.value.happiness > 50 && stats.value.activity > 30;
  });

  const totalAgents = computed(() => agents.value.length);

  const averageMood = computed(() => {
    if (agents.value.length === 0) return 0;
    const sum = agents.value.reduce((acc, agent) => acc + agent.mood, 0);
    return Math.round(sum / agents.value.length);
  });

  const recentEvents = computed(() => {
    return events.value.slice(0, 5);
  });

  // 获取社群状态
  const fetchCommunityStatus = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      
      stats.value = await api.getCommunityStatus();
      lastUpdated.value = new Date();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取社群状态失败';
      console.error('获取社群状态失败:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // 获取AI居民列表
  const fetchAgents = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.getAgents();
      agents.value = response.agents;
      lastUpdated.value = new Date();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取居民列表失败';
      console.error('获取居民列表失败:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // 获取事件历史
  const fetchEvents = async (limit: number = 10) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.getEvents(limit);
      events.value = response.events;
      lastUpdated.value = new Date();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取事件历史失败';
      console.error('获取事件历史失败:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // 执行玩家指令
  const executeCommand = async (request: CommandRequest): Promise<CommandResponse | null> => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.executeCommand(request);
      
      // 更新本地状态
      if (stats.value && response.success) {
        stats.value.happiness = response.new_stats.happiness;
        stats.value.activity = response.new_stats.activity;
      }
      
      // 刷新事件列表
      await fetchEvents();
      
      lastUpdated.value = new Date();
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '执行指令失败';
      console.error('执行指令失败:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // 获取完整统计汇总
  const fetchStatsSummary = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.getStatsSummary();
      stats.value = response.community_stats;
      lastUpdated.value = new Date();
      
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取统计汇总失败';
      console.error('获取统计汇总失败:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // 刷新所有数据
  const refreshAll = async () => {
    await Promise.all([
      fetchCommunityStatus(),
      fetchAgents(),
      fetchEvents()
    ]);
  };

  // 清除错误状态
  const clearError = () => {
    error.value = null;
  };

  // 重置状态
  const reset = () => {
    stats.value = null;
    agents.value = [];
    events.value = [];
    error.value = null;
    lastUpdated.value = null;
    isLoading.value = false;
  };

  return {
    // 状态
    stats,
    agents,
    events,
    isLoading,
    error,
    lastUpdated,
    
    // 计算属性
    isHealthy,
    totalAgents,
    averageMood,
    recentEvents,
    
    // 方法
    fetchCommunityStatus,
    fetchAgents,
    fetchEvents,
    executeCommand,
    fetchStatsSummary,
    refreshAll,
    clearError,
    reset
  };
}); 