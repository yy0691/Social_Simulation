<template>
  <div id="app" :class="{ 'dark': isDarkMode, 'light': !isDarkMode }">
    <!-- 背景效果 -->
    <div class="app-background">
      <div class="gradient-overlay"></div>
      <div class="particles" v-if="settings.animationsEnabled"></div>
      <div class="stars" v-if="settings.animationsEnabled">
        <div class="star" v-for="n in 50" :key="n" 
             :style="{ 
               left: Math.random() * 100 + '%', 
               top: Math.random() * 100 + '%',
               animationDelay: Math.random() * 3 + 's'
             }"></div>
      </div>
      <div class="floating-particles" v-if="settings.animationsEnabled">
        <div class="particle" v-for="n in 20" :key="n"
             :style="{
               left: Math.random() * 100 + '%',
               animationDelay: Math.random() * 20 + 's',
               animationDuration: (15 + Math.random() * 10) + 's'
             }"></div>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="app-container">
      <!-- 头部导航 -->
      <header class="app-header">
        <div class="header-content">
          <!-- 导航按钮组 -->
          <nav class="header-nav">
            <!-- 主要导航按钮 -->
            <div class="nav-main">
              <button
                v-for="(item, index) in navItems"
                :key="item.key"
                @click="setCurrentView(item.key as any)"
                :class="['nav-button', { 'active': currentView === item.key }]"
                :title="`${item.label} (Ctrl+${index + 1})`"
              >
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
                <kbd class="shortcut-hint">{{ index + 1 }}</kbd>
              </button>
            </div>

            <!-- 功能按钮组 -->
            <div class="nav-actions">
              <!-- LLM状态指示器 -->
              <SimpleLLMStatus />

              <!-- 主题切换 -->
              <button class="icon-button" @click="toggleTheme" title="切换主题">
                <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'"></i>
                <span class="button-label">{{ isDarkMode ? '浅色' : '深色' }}</span>
              </button>

              <!-- 刷新按钮 -->
              <button class="icon-button" @click="refreshData" :disabled="isLoading" title="刷新数据">
                <i :class="['fas fa-sync-alt', { 'spinning': isLoading }]"></i>
                <span class="button-label">刷新</span>
              </button>

              <!-- 连接状态 -->
              <div class="connection-status" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
                <i :class="isConnected ? 'fas fa-wifi' : 'fas fa-wifi-slash'"></i>
                <span>{{ isConnected ? '已连接' : '未连接' }}</span>
              </div>
            </div>
          </nav>

          <!-- 通知按钮（如果有未读通知） -->
          <div class="header-notifications" v-if="unreadNotifications > 0">
            <button class="icon-button notification-btn" @click="showNotifications = !showNotifications">
              <i class="fas fa-bell"></i>
              <span class="notification-badge">{{ unreadNotifications }}</span>
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
          <Transition name="view-fade" mode="out-in">
            <!-- 社群中心视图 -->
            <CommunityView v-if="currentView === 'community'" key="community" />
            
            <!-- 聊天室视图 -->
            <ChatView v-else-if="currentView === 'chat'" key="chat" />
            
            <!-- 邀请视图 -->
            <InvitationView v-else-if="currentView === 'invitation'" key="invitation" />
            
            <!-- 设置视图 -->
            <SettingsView v-else-if="currentView === 'settings'" key="settings" />
            
            <!-- 样式展示视图 -->
            <StyleShowcase v-else-if="currentView === 'showcase'" key="showcase" />
          </Transition>
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
import InvitationView from './views/InvitationView.vue';
import StyleShowcase from './views/StyleShowcase.vue';

// 创建一个简单的LLM状态指示器组件
const SimpleLLMStatus = {
  template: `<div style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px;"><div style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></div><span style="font-size: 14px;">LLM</span></div>`
};

// 状态管理
const appStore = useAppStore();
const communityStore = useCommunityStore();

// 响应式数据
const showNotifications = ref(false);
const refreshInterval = ref<number | null>(null);

// 计算属性
const isConnected = computed(() => appStore.isConnected);
const isLoading = computed(() => appStore.isLoading);
const currentView = computed(() => appStore.currentView);
const isDarkMode = computed(() => appStore.isDarkMode);
const notifications = computed(() => appStore.notifications);
const unreadNotifications = computed(() => appStore.unreadNotifications);
const connectionChecking = computed(() => appStore.connectionChecking);
const settings = computed(() => appStore.settings);
const navItems = appStore.navItems;

const {
  stats: communityStats,
  lastUpdated
} = communityStore;

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

  if (settings.value.autoRefresh && isConnected.value) {
    refreshInterval.value = setInterval(() => {
      if (isConnected.value) {
        refreshData();
      }
    }, settings.value.refreshInterval);
  }
};

// 键盘快捷键处理
const handleKeydown = (e: KeyboardEvent) => {
  // 检查是否在输入框中
  const target = e.target as HTMLElement;
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
    return;
  }

  // 处理快捷键
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case '1':
        e.preventDefault();
        setCurrentView('community');
        break;
      case '2':
        e.preventDefault();
        setCurrentView('chat');
        break;
      case '3':
        e.preventDefault();
        setCurrentView('settings');
        break;
      case 'r':
        e.preventDefault();
        refreshData();
        break;
      case 'd':
        e.preventDefault();
        toggleTheme();
        break;
    }
  }
  
  // ESC键关闭通知面板
  if (e.key === 'Escape') {
    showNotifications.value = false;
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

  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeydown);

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
  
  // 移除事件监听器
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
/* 主应用样式 */
#app {
  min-height: 100vh;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  transition: all 0.3s ease;
  overflow-x: hidden;
}

/* 背景效果 */
.app-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
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

/* 星星效果 */
.stars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: twinkle 3s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* 浮动粒子效果 */
.floating-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.8) 0%, transparent 70%);
  border-radius: 50%;
  animation: float-up linear infinite;
}

@keyframes float-up {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) scale(1);
    opacity: 0;
  }
}

/* 应用容器 */
.app-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: relative;
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
  padding: 0.5rem 1rem;
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
  gap: 1rem;
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
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;
  transition: all 0.3s ease;
}

.connection-status.connected {
  color: var(--neon-green);
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.1);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}

.connection-status.disconnected {
  color: var(--neon-pink);
  border-color: rgba(236, 72, 153, 0.3);
  background: rgba(236, 72, 153, 0.1);
  box-shadow: 0 0 10px rgba(236, 72, 153, 0.2);
}

/* 导航样式 */
.header-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  gap: var(--spacing-lg);
  max-width: 1000px;
  margin: 0 auto;
}

.nav-main {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.nav-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  font-size: 0.875rem;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.nav-button:hover::before {
  left: 100%;
}

.nav-button:hover {
  border-color: var(--neon-blue);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
  background: rgba(0, 212, 255, 0.05);
}

.nav-button.active {
  background: linear-gradient(135deg, var(--neon-blue), var(--electric-blue));
  border-color: var(--neon-blue);
  color: white;
  box-shadow: 0 0 25px rgba(0, 212, 255, 0.4);
  transform: translateY(-2px);
}

.nav-button.active::before {
  display: none;
}

.icon-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  white-space: nowrap;
}

.icon-button:hover:not(:disabled) {
  border-color: var(--neon-blue);
  color: var(--text-primary);
  background: rgba(0, 212, 255, 0.05);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
  transform: translateY(-1px);
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.button-label {
  font-size: 0.75rem;
  font-weight: 500;
}

.header-notifications {
  display: flex;
  align-items: center;
}

.notification-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  padding: 0;
  justify-content: center;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--neon-pink);
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  font-weight: 600;
  box-shadow: 0 0 10px rgba(236, 72, 153, 0.4);
}

/* 主内容区 */
.app-main {
  flex: 1;
  position: relative;
  padding: 0.25rem;
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
  padding: 0.5rem 1rem;
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

/* 页面切换动画 */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.view-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 导航按钮样式优化 */
.nav-button {
  position: relative;
  overflow: hidden;
}

.shortcut-hint {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(102, 126, 234, 0.8);
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-family: inherit;
}

.nav-button:hover .shortcut-hint {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-nav {
    max-width: 800px;
    gap: var(--spacing-md);
  }
  
  .nav-button {
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: 0.8rem;
  }
  
  .icon-button {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.8rem;
  }
  
  .button-label {
    font-size: 0.7rem;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: var(--spacing-sm) var(--spacing-lg);
  }
  
  .header-content {
    gap: var(--spacing-sm);
  }
  
  .header-nav {
    gap: var(--spacing-sm);
    max-width: none;
  }
  
  .nav-main {
    gap: var(--spacing-xs);
  }
  
  .nav-actions {
    gap: var(--spacing-xs);
  }
  
  .nav-button {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
  }
  
  .nav-button span {
    display: none; /* 隐藏按钮文字，只显示图标 */
  }
  
  .icon-button {
    padding: var(--spacing-xs);
    min-width: 32px;
    height: 32px;
  }
  
  .button-label {
    display: none; /* 隐藏功能按钮文字 */
  }
  
  .connection-status {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
  }
  
  .shortcut-hint {
    display: none; /* 隐藏快捷键提示 */
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: var(--spacing-xs) var(--spacing-md);
  }
  
  .header-content {
    gap: var(--spacing-xs);
  }
  
  .header-nav {
    gap: var(--spacing-xs);
  }
  
  .nav-main {
    gap: 2px;
  }
  
  .nav-actions {
    gap: 2px;
  }
  
  .nav-button {
    padding: var(--spacing-xs);
    min-width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
  }
  
  .icon-button {
    padding: 4px;
    min-width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
  }
  
  .connection-status span {
    display: none; /* 小屏幕隐藏连接状态文字 */
  }
  
  .connection-status {
    padding: var(--spacing-xs);
    min-width: 28px;
    height: 28px;
    justify-content: center;
  }
  
  .header-notifications {
    margin-left: var(--spacing-xs);
  }
  
  .notification-btn {
    width: 28px;
    height: 28px;
  }
}

/* 动画效果 */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 通知面板样式 */
.notifications-panel {
  position: absolute;
  top: 100%;
  right: var(--spacing-lg);
  width: 320px;
  max-height: 400px;
  background: var(--bg-card);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-heavy);
  z-index: 200;
  overflow: hidden;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.notifications-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
}

.clear-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.75rem;
}

.clear-btn:hover {
  border-color: var(--neon-blue);
  color: var(--text-primary);
  background: rgba(0, 212, 255, 0.05);
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.3s ease;
}

.notification-item:hover {
  background: rgba(0, 212, 255, 0.05);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item.success i {
  color: var(--neon-green);
}

.notification-item.error i {
  color: var(--neon-pink);
}

.notification-item.warning i {
  color: var(--neon-orange);
}

.notification-item.info i {
  color: var(--neon-blue);
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.notification-content p {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.notification-time {
  font-size: 0.7rem;
  color: var(--text-tertiary);
}
</style> 