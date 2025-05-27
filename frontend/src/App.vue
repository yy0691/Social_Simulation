<template>
  <div id="app" :class="{ 'dark': isDarkMode, 'light': !isDarkMode }">
    <!-- 背景效果 -->
    <div class="app-background">
      <div class="gradient-overlay"></div>
      <div class="particles" v-if="settings.animationsEnabled"></div>
    </div>

    <!-- 主容器 -->
    <div class="app-container">
      <!-- 头部导航 -->
      <header class="app-header">
        <div class="header-content">
          <!-- Logo和标题 -->
          <div class="header-left">
            <h1 class="app-title">
              <i class="fas fa-robot"></i>
              AI社群模拟小游戏
            </h1>
            <div class="connection-status" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
              <i :class="isConnected ? 'fas fa-wifi' : 'fas fa-wifi-slash'"></i>
              <span>{{ isConnected ? '已连接' : '未连接' }}</span>
            </div>
          </div>

          <!-- 导航按钮 -->
          <nav class="header-nav">
            <button
              v-for="item in navItems"
              :key="item.key"
              @click="setCurrentView(item.key as any)"
              :class="['nav-button', { 'active': currentView === item.key }]"
            >
              <i :class="item.icon"></i>
              <span>{{ item.label }}</span>
            </button>
          </nav>

          <!-- 头部右侧操作 -->
          <div class="header-right">
            <!-- 通知按钮 -->
            <button class="icon-button" @click="showNotifications = !showNotifications" v-if="unreadNotifications > 0">
              <i class="fas fa-bell"></i>
              <span class="notification-badge">{{ unreadNotifications }}</span>
            </button>

            <!-- 主题切换 -->
            <button class="icon-button" @click="toggleTheme">
              <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'"></i>
            </button>

            <!-- 刷新按钮 -->
            <button class="icon-button" @click="refreshData" :disabled="isLoading">
              <i :class="['fas fa-sync-alt', { 'spinning': isLoading }]"></i>
            </button>
          </div>
        </div>
      </header>

      <!-- 通知面板 -->
      <div v-if="showNotifications && notifications.length > 0" class="notifications-panel">
        <div class="notifications-header">
          <h3>通知消息</h3>
          <button @click="clearNotifications" class="clear-btn">清空</button>
        </div>
        <div class="notifications-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            :class="['notification-item', notification.type]"
            @click="removeNotification(notification.id)"
          >
            <i :class="getNotificationIcon(notification.type)"></i>
            <div class="notification-content">
              <h4>{{ notification.title }}</h4>
              <p>{{ notification.message }}</p>
              <span class="notification-time">{{ formatTime(notification.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <main class="app-main">
        <!-- 加载状态 -->
        <div v-if="isLoading && !isConnected" class="loading-overlay">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>连接中...</p>
          </div>
        </div>

        <!-- 离线状态 -->
        <div v-else-if="!isConnected" class="offline-overlay">
          <div class="offline-content">
            <i class="fas fa-exclamation-triangle"></i>
            <h2>无法连接到服务器</h2>
            <p>请检查网络连接或服务器状态</p>
            <button @click="checkConnection" class="retry-btn" :disabled="connectionChecking">
              <i class="fas fa-redo-alt"></i>
              重试连接
            </button>
          </div>
        </div>

        <!-- 主要视图 -->
        <div v-else class="view-container">
          <!-- 社群中心视图 -->
          <CommunityView v-if="currentView === 'community'" />
          
          <!-- 聊天室视图 -->
          <ChatView v-else-if="currentView === 'chat'" />
          
          <!-- 设置视图 -->
          <SettingsView v-else-if="currentView === 'settings'" />
        </div>
      </main>

      <!-- 底部状态栏 -->
      <footer class="app-footer">
        <div class="footer-content">
          <div class="status-info">
            <span>最后更新: {{ lastUpdated ? formatTime(lastUpdated.toISOString()) : '未知' }}</span>
            <span v-if="communityStats">
              人口: {{ communityStats.population }} | 
              幸福度: {{ Math.round(communityStats.happiness) }}% | 
              活跃度: {{ Math.round(communityStats.activity) }}%
            </span>
          </div>
          <div class="app-version">
            <span>AI社群模拟小游戏 v1.0.0</span>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAppStore } from './stores/app';
import { useCommunityStore } from './stores/community';
import CommunityView from './views/CommunityView.vue';
import ChatView from './views/ChatView.vue';
import SettingsView from './views/SettingsView.vue';

// 状态管理
const appStore = useAppStore();
const communityStore = useCommunityStore();

// 响应式数据
const showNotifications = ref(false);
const refreshInterval = ref<number | null>(null);

// 计算属性
const {
  isConnected,
  isLoading,
  currentView,
  isDarkMode,
  notifications,
  unreadNotifications,
  connectionChecking,
  settings,
  navItems
} = appStore;

const {
  stats: communityStats,
  lastUpdated
} = communityStore;

// 方法
const {
  setCurrentView,
  toggleTheme,
  checkConnection,
  removeNotification,
  clearNotifications
} = appStore;

const { refreshAll } = communityStore;

// 刷新数据
const refreshData = async () => {
  await communityStore.refreshAll();
};

// 格式化时间
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// 获取通知图标
const getNotificationIcon = (type: string) => {
  const icons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  };
  return icons[type as keyof typeof icons] || icons.info;
};

// 设置自动刷新
const setupAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }

  if (settings.autoRefresh && isConnected.value) {
    refreshInterval.value = setInterval(() => {
      if (isConnected.value) {
        refreshData();
      }
    }, settings.refreshInterval);
  }
};

// 组件挂载
onMounted(async () => {
  // 初始化应用
  await appStore.initApp();
  
  // 如果连接成功，获取初始数据
  if (isConnected.value) {
    await refreshData();
    setupAutoRefresh();
  }

  // 监听设置变化
  appStore.$subscribe(() => {
    setupAutoRefresh();
  });

  // 点击外部关闭通知面板
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    if (!target.closest('.notifications-panel') && !target.closest('.icon-button')) {
      showNotifications.value = false;
    }
  });
});

// 组件卸载
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }
});
</script>

<style scoped>
/* 主应用样式 */
#app {
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  transition: all 0.3s ease;
}

/* 背景效果 */
.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.1;
}

.dark .gradient-overlay {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  opacity: 0.8;
}

.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="20" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="60" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  animation: particles-move 20s linear infinite;
}

@keyframes particles-move {
  0% { transform: translateY(0); }
  100% { transform: translateY(-100vh); }
}

/* 应用容器 */
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.dark .app-container {
  background: rgba(26, 32, 44, 0.95);
  color: #e2e8f0;
}

/* 头部样式 */
.app-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.dark .app-header {
  background: rgba(45, 55, 72, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  border: 1px solid;
}

.connection-status.connected {
  color: #10b981;
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.connection-status.disconnected {
  color: #ef4444;
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* 导航样式 */
.header-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.75rem;
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-button:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.nav-button.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 头部右侧 */
.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-button {
  position: relative;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-button:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notification-badge {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  background: #ef4444;
  color: white;
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.75rem;
  min-width: 1.25rem;
  text-align: center;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 通知面板 */
.notifications-panel {
  position: absolute;
  top: 100%;
  right: 2rem;
  width: 24rem;
  max-height: 20rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 200;
  overflow: hidden;
}

.dark .notifications-panel {
  background: #2d3748;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark .notifications-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.notifications-list {
  max-height: 16rem;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: background 0.2s ease;
}

.notification-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.dark .notification-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.notification-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.notification-content p {
  margin: 0 0 0.25rem 0;
  font-size: 0.8rem;
  opacity: 0.8;
}

.notification-time {
  font-size: 0.75rem;
  opacity: 0.6;
}

/* 主内容区 */
.app-main {
  flex: 1;
  position: relative;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.loading-overlay,
.offline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.dark .loading-overlay,
.dark .offline-overlay {
  background: rgba(26, 32, 44, 0.9);
}

.loading-spinner,
.offline-content {
  text-align: center;
}

.loading-spinner i {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.offline-content i {
  font-size: 4rem;
  color: #ef4444;
  margin-bottom: 1rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover:not(:disabled) {
  background: #5a67d8;
}

/* 视图容器 */
.view-container {
  width: 100%;
  min-height: calc(100vh - 12rem);
}

/* 底部状态栏 */
.app-footer {
  background: rgba(248, 250, 252, 0.9);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
}

.dark .app-footer {
  background: rgba(45, 55, 72, 0.9);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  font-size: 0.875rem;
}

.status-info span {
  margin-right: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-main {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .notifications-panel {
    width: calc(100vw - 2rem);
    right: 1rem;
  }
}
</style> 