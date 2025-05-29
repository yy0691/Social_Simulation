/**
 * AI社群模拟小游戏 - 应用状态管理
 * 管理应用级别的状态，如连接状态、主题、设置等
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import type { AppState, Settings, Notification, NavItem } from '../types';

export const useAppStore = defineStore('app', () => {
  // 状态变量
  const isConnected = ref(false);
  const isLoading = ref(false);
  const currentView = ref<'community' | 'chat' | 'invitation' | 'settings' | 'showcase'>('community');
  const theme = ref<'dark' | 'light'>('dark');
  const notifications = ref<Notification[]>([]);
  const connectionChecking = ref(false);

  // 设置状态
  const settings = ref<Settings>({
    theme: 'dark',
    autoRefresh: true,
    refreshInterval: 30000, // 30秒
    soundEnabled: true,
    animationsEnabled: true,
    compactMode: false
  });

  // 导航项目配置 - 按照人类使用逻辑排序
  const navItems: NavItem[] = [
    {
      key: 'community',
      label: '社群中心',
      icon: 'fas fa-users',
      component: 'CommunityView'
    },
    {
      key: 'chat',
      label: '聊天室',
      icon: 'fas fa-comments',
      component: 'ChatView'
    },
    {
      key: 'invitation',
      label: '邀请管理',
      icon: 'fas fa-user-plus',
      component: 'InvitationView'
    },
    {
      key: 'settings',
      label: '设置',
      icon: 'fas fa-cog',
      component: 'SettingsView'
    },
    {
      key: 'showcase',
      label: '样式展示',
      icon: 'fas fa-palette',
      component: 'StyleShowcase'
    }
  ];

  // 计算属性
  const currentNavItem = computed(() => {
    return navItems.find(item => item.key === currentView.value);
  });

  const unreadNotifications = computed(() => {
    return notifications.value.length;
  });

  const isDarkMode = computed(() => theme.value === 'dark');

  // 检查API连接状态
  const checkConnection = async () => {
    if (connectionChecking.value) return;
    
    try {
      connectionChecking.value = true;
      const connected = await api.testConnection();
      isConnected.value = connected;
      
      if (connected) {
        addNotification({
          type: 'success',
          title: '连接成功',
          message: 'API服务器连接正常',
          duration: 3000
        });
      } else {
        addNotification({
          type: 'error',
          title: '连接失败',
          message: '无法连接到API服务器',
          duration: 5000
        });
      }
    } catch (error) {
      isConnected.value = false;
      console.error('连接检查失败:', error);
      addNotification({
        type: 'error',
        title: '连接错误',
        message: '网络连接出现问题',
        duration: 5000
      });
    } finally {
      connectionChecking.value = false;
    }
  };

  // 切换视图
  const setCurrentView = (view: 'community' | 'chat' | 'invitation' | 'settings' | 'showcase') => {
    currentView.value = view;
  };

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
    settings.value.theme = theme.value;
    saveSettings();
    applyTheme();
  };

  // 应用主题
  const applyTheme = () => {
    const html = document.documentElement;
    if (theme.value === 'dark') {
      html.classList.add('dark');
      html.classList.remove('light');
    } else {
      html.classList.add('light');
      html.classList.remove('dark');
    }
  };

  // 添加通知
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString()
    };

    notifications.value.unshift(newNotification);

    // 自动删除通知
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, notification.duration);
    }
  };

  // 删除通知
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) {
      notifications.value.splice(index, 1);
    }
  };

  // 清空所有通知
  const clearNotifications = () => {
    notifications.value = [];
  };

  // 更新设置
  const updateSettings = (newSettings: Partial<Settings>) => {
    settings.value = { ...settings.value, ...newSettings };
    
    // 同步主题
    if (newSettings.theme && newSettings.theme !== theme.value) {
      theme.value = newSettings.theme;
      applyTheme();
    }
    
    saveSettings();
  };

  // 保存设置到本地存储
  const saveSettings = () => {
    try {
      localStorage.setItem('ai-community-settings', JSON.stringify(settings.value));
    } catch (error) {
      console.error('保存设置失败:', error);
    }
  };

  // 从本地存储加载设置
  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('ai-community-settings');
      if (saved) {
        const loadedSettings = JSON.parse(saved);
        settings.value = { ...settings.value, ...loadedSettings };
        theme.value = settings.value.theme;
        applyTheme();
      }
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  };

  // 重置设置
  const resetSettings = () => {
    settings.value = {
      theme: 'dark',
      autoRefresh: true,
      refreshInterval: 30000,
      soundEnabled: true,
      animationsEnabled: true,
      compactMode: false
    };
    theme.value = 'dark';
    applyTheme();
    saveSettings();
  };

  // 获取应用状态
  const getAppState = (): AppState => {
    return {
      isConnected: isConnected.value,
      isLoading: isLoading.value,
      currentView: currentView.value,
      theme: theme.value
    };
  };

  // 初始化应用
  const initApp = async () => {
    loadSettings();
    await checkConnection();
  };

  return {
    // 状态
    isConnected,
    isLoading,
    currentView,
    theme,
    notifications,
    connectionChecking,
    settings,
    navItems,
    
    // 计算属性
    currentNavItem,
    unreadNotifications,
    isDarkMode,
    
    // 方法
    checkConnection,
    setCurrentView,
    toggleTheme,
    applyTheme,
    addNotification,
    removeNotification,
    clearNotifications,
    updateSettings,
    saveSettings,
    loadSettings,
    resetSettings,
    getAppState,
    initApp
  };
}); 