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
              活跃度: {{ Math.round(activityLevel) }}%
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
  lastUpdated,
  activityLevel
} = communityStore;

const {
  setCurrentView,
  toggleTheme,
  checkConnection,
  removeNotification,
  clearNotifications
} = appStore;

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
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: linear-gradient(135deg, #0a1628 0%, #071015 50%, #000000 100%);
  color: #ffffff;
  overflow-x: hidden;
  font-size: 0.875rem;
  line-height: 1.6;
  
  /* CSS变量定义 */
  --primary-blue: #00d4ff;
  --electric-blue: #0099cc;
  --neon-cyan: #00ffff;
  --deep-blue: #001a2e;
  --dark-navy: #0a1628;
  --midnight: #071015;
  
  /* 渐变色 */
  --gradient-primary: linear-gradient(135deg, #00d4ff 0%, #0099cc 50%, #667eea 100%);
  --gradient-secondary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-dark: linear-gradient(135deg, #0a1628 0%, #071015 50%, #000000 100%);
  
  /* 发光效果 */
  --glow-primary: 0 0 20px rgba(0, 212, 255, 0.5);
  --glow-secondary: 0 0 15px rgba(0, 212, 255, 0.3);
  --glow-hover: 0 0 30px rgba(0, 212, 255, 0.7);
  --glow-intense: 0 0 40px rgba(0, 212, 255, 0.8);
  
  /* 文字颜色 */
  --text-primary: #ffffff;
  --text-secondary: #b3d9ff;
  --text-tertiary: #7aa3d9;
  --text-muted: #4a5568;
  
  /* 背景色 */
  --bg-primary: rgba(10, 22, 40, 0.95);
  --bg-secondary: rgba(7, 16, 21, 0.9);
  --bg-card: rgba(20, 35, 55, 0.8);
  --bg-hover: rgba(0, 212, 255, 0.1);
  
  /* 边框和阴影 */
  --border-primary: 1px solid rgba(0, 212, 255, 0.3);
  --border-secondary: 1px solid rgba(0, 212, 255, 0.2);
  --border-glow: 1px solid rgba(0, 212, 255, 0.6);
  
  /* 间距系统 */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 0.75rem;
  --space-lg: 1rem;
  --space-xl: 1.5rem;
  --space-2xl: 2rem;
  --space-3xl: 3rem;
  
  /* 圆角 */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  
  /* 字体大小 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  
  /* 过渡效果 */
  --transition-fast: 0.15s ease;
  --transition-base: 0.3s ease;
  --transition-slow: 0.5s ease;
  --transition-bounce: 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
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
  background: var(--gradient-dark);
  opacity: 1;
}

.dark .gradient-overlay {
  background: var(--gradient-dark);
  opacity: 1;
}

/* 增强粒子效果 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(2px 2px at 20px 30px, rgba(0, 212, 255, 0.3), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(102, 126, 234, 0.2), transparent),
    radial-gradient(1px 1px at 90px 40px, rgba(0, 255, 255, 0.4), transparent);
  background-repeat: repeat;
  background-size: 100px 100px;
  animation: particles-drift 25s linear infinite;
}

@keyframes particles-drift {
  0% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
  100% { transform: translate(0, 0) rotate(360deg); }
}

/* 优化星星效果 */
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
  width: 3px;
  height: 3px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.9) 0%, rgba(0, 212, 255, 0.1) 70%);
  border-radius: 50%;
  animation: twinkle 4s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(0, 212, 255, 0.8);
}

@keyframes twinkle {
  0%, 100% { 
    opacity: 0.2; 
    transform: scale(0.8);
  }
  50% { 
    opacity: 1; 
    transform: scale(1.2);
  }
}

/* 增强浮动粒子 */
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
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.8) 0%, rgba(0, 212, 255, 0.2) 50%, transparent 100%);
  border-radius: 50%;
  animation: float-up linear infinite;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.6);
}

@keyframes float-up {
  0% {
    transform: translateY(100vh) scale(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
    transform: translateY(90vh) scale(0.5) rotate(36deg);
  }
  50% {
    transform: translateY(50vh) scale(1) rotate(180deg);
  }
  90% {
    opacity: 1;
    transform: translateY(10vh) scale(0.8) rotate(324deg);
  }
  100% {
    transform: translateY(-10vh) scale(0) rotate(360deg);
    opacity: 0;
  }
}

/* 应用容器 */
.app-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  backdrop-filter: blur(20px);
  position: relative;
}

.dark .app-container {
  background: rgba(26, 32, 44, 0.95);
  color: #e2e8f0;
}

/* 增强头部样式 */
.app-header {
  background: var(--bg-secondary);
  backdrop-filter: blur(30px);
  border-bottom: var(--border-primary);
  box-shadow: var(--glow-secondary);
  padding: var(--space-md) var(--space-xl);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all var(--transition-base);
}

.app-header:hover {
  box-shadow: var(--glow-primary);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  gap: var(--space-xl);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2xl);
}

/* 炫酷标题 */
.app-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
  background: var(--gradient-primary);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  text-shadow: var(--glow-secondary);
  letter-spacing: -0.025em;
}

/* 连接状态指示器 */
.connection-status {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-xl);
  font-size: var(--text-sm);
  font-weight: 600;
  border: var(--border-secondary);
  transition: all var(--transition-bounce);
  position: relative;
  overflow: hidden;
}

.connection-status::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent);
  transition: left var(--transition-slow);
}

.connection-status:hover::before {
  left: 100%;
}

.connection-status.connected {
  color: var(--primary-blue);
  border-color: rgba(0, 212, 255, 0.5);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: var(--glow-secondary);
}

.connection-status.connected:hover {
  box-shadow: var(--glow-primary);
  transform: translateY(-2px) scale(1.02);
}

.connection-status.disconnected {
  color: #ff4757;
  border-color: rgba(255, 71, 87, 0.5);
  background: rgba(255, 71, 87, 0.1);
  box-shadow: 0 0 15px rgba(255, 71, 87, 0.3);
}

/* 导航样式系统 */
.header-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  gap: var(--space-2xl);
  max-width: 1200px;
  margin: 0 auto;
}

.nav-main {
  display: flex;
  gap: var(--space-md);
  align-items: center;
}

.nav-actions {
  display: flex;
  gap: var(--space-md);
  align-items: center;
}

/* 炫酷导航按钮 */
.nav-button {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  border: var(--border-secondary);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-bounce);
  font-weight: 600;
  font-size: var(--text-sm);
  white-space: nowrap;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* 发光扫描效果 */
.nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
  transition: left var(--transition-slow);
}

.nav-button:hover::before {
  left: 100%;
}

.nav-button:hover {
  border-color: rgba(0, 212, 255, 0.8);
  box-shadow: var(--glow-hover);
  transform: translateY(-3px) scale(1.05);
  background: rgba(0, 212, 255, 0.15);
  color: var(--text-primary);
}

.nav-button.active {
  background: var(--gradient-primary);
  border-color: var(--primary-blue);
  color: white;
  box-shadow: var(--glow-intense);
  transform: translateY(-2px);
}

.nav-button.active::before {
  display: none;
}

/* 炫酷图标按钮 */
.icon-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  border: var(--border-secondary);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-bounce);
  font-size: var(--text-sm);
  font-weight: 500;
  white-space: nowrap;
  backdrop-filter: blur(10px);
  min-width: 44px;
  min-height: 44px;
  justify-content: center;
}

.icon-button:hover:not(:disabled) {
  border-color: rgba(0, 212, 255, 0.8);
  color: var(--text-primary);
  background: rgba(0, 212, 255, 0.15);
  box-shadow: var(--glow-primary);
  transform: translateY(-2px) scale(1.05);
}

.icon-button:active {
  transform: translateY(0) scale(0.98);
}

.icon-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.button-label {
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.025em;
}

.header-notifications {
  display: flex;
  align-items: center;
}

/* 通知按钮特效 */
.notification-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  padding: 0;
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: linear-gradient(135deg, #ff4757, #ff3742);
  color: white;
  font-size: var(--text-xs);
  padding: 4px 8px;
  border-radius: var(--radius-lg);
  min-width: 20px;
  text-align: center;
  font-weight: 700;
  box-shadow: 0 0 15px rgba(255, 71, 87, 0.6);
  animation: pulse-notification 2s infinite;
}

@keyframes pulse-notification {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 主内容区 */
.app-main {
  flex: 1;
  position: relative;
  padding: var(--space-lg);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 加载和离线状态 */
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
  background: var(--bg-primary);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
}

.loading-spinner,
.offline-content {
  text-align: center;
  padding: var(--space-3xl);
}

.loading-spinner i {
  font-size: 4rem;
  color: var(--primary-blue);
  margin-bottom: var(--space-xl);
  filter: drop-shadow(var(--glow-primary));
}

.offline-content i {
  font-size: 5rem;
  color: #ff4757;
  margin-bottom: var(--space-xl);
  filter: drop-shadow(0 0 20px rgba(255, 71, 87, 0.5));
}

.retry-btn {
  margin-top: var(--space-xl);
  padding: var(--space-lg) var(--space-2xl);
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--transition-bounce);
  font-weight: 600;
  font-size: var(--text-base);
  box-shadow: var(--glow-secondary);
}

.retry-btn:hover:not(:disabled) {
  box-shadow: var(--glow-intense);
  transform: translateY(-3px) scale(1.05);
}

/* 视图容器 */
.view-container {
  width: 100%;
  min-height: calc(100vh - 16rem);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

/* 优化底部状态栏 */
.app-footer {
  background: var(--bg-secondary);
  border-top: var(--border-primary);
  padding: var(--space-md) var(--space-xl);
  backdrop-filter: blur(20px);
  box-shadow: 0 -4px 20px rgba(0, 212, 255, 0.1);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.status-info {
  display: flex;
  gap: var(--space-xl);
  align-items: center;
}

.status-info span {
  padding: var(--space-sm) var(--space-md);
  background: rgba(0, 212, 255, 0.1);
  border: var(--border-secondary);
  border-radius: var(--radius-md);
  font-weight: 500;
}

.app-version span {
  background: var(--gradient-primary);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  letter-spacing: 0.025em;
}

/* 页面切换动画增强 */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.view-fade-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.98);
}

.view-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px) scale(0.98);
}

/* 快捷键提示优化 */
.shortcut-hint {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all var(--transition-bounce);
  box-shadow: var(--glow-secondary);
  transform: scale(0.8);
  font-family: inherit;
}

.nav-button:hover .shortcut-hint {
  opacity: 1;
  transform: scale(1);
}

/* 动画效果增强 */
.spinning {
  animation: spin-enhanced 1s linear infinite;
}

@keyframes spin-enhanced {
  from { 
    transform: rotate(0deg) scale(1); 
  }
  50% { 
    transform: rotate(180deg) scale(1.1); 
  }
  to { 
    transform: rotate(360deg) scale(1); 
  }
}

/* 全局滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

::-webkit-scrollbar-thumb {
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--glow-secondary);
}

::-webkit-scrollbar-thumb:hover {
  box-shadow: var(--glow-primary);
}

/* 选择文本样式 */
::selection {
  background: rgba(0, 212, 255, 0.3);
  color: white;
}

/* 焦点样式 */
*:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3);
}

/* 响应式设计优化 */
@media (max-width: 1200px) {
  .header-nav {
    gap: var(--space-lg);
  }
  
  .nav-button {
    padding: var(--space-sm) var(--space-lg);
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: var(--space-md) var(--space-lg);
  }
  
  .header-content {
    gap: var(--space-md);
  }
  
  .header-nav {
    gap: var(--space-md);
  }
  
  .nav-main {
    gap: var(--space-sm);
  }
  
  .nav-actions {
    gap: var(--space-sm);
  }
  
  .nav-button {
    padding: var(--space-sm) var(--space-md);
    font-size: var(--text-xs);
  }
  
  .nav-button span {
    display: none;
  }
  
  .icon-button {
    padding: var(--space-sm);
    min-width: 40px;
    height: 40px;
  }
  
  .button-label {
    display: none;
  }
  
  .shortcut-hint {
    display: none;
  }
  
  .notifications-panel {
    width: 320px;
    right: var(--space-md);
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: var(--space-sm) var(--space-md);
  }
  
  .nav-button {
    padding: var(--space-sm);
    min-width: 36px;
    height: 36px;
    border-radius: var(--radius-md);
  }
  
  .icon-button {
    padding: var(--space-sm);
    min-width: 36px;
    height: 36px;
  }
  
  .connection-status span {
    display: none;
  }
  
  .connection-status {
    padding: var(--space-sm);
    min-width: 36px;
    height: 36px;
    justify-content: center;
  }
  
  .notification-btn {
    width: 36px;
    height: 36px;
  }
  
  .notifications-panel {
    width: calc(100vw - 2rem);
    right: var(--space-lg);
  }
}

/* 辅助工具类 */
.glow-effect {
  box-shadow: var(--glow-primary);
}

.text-glow {
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: var(--glow-secondary);
  }
  50% {
    box-shadow: var(--glow-intense);
  }
}

/* 通知面板增强 */
.notifications-panel {
  position: absolute;
  top: 100%;
  right: var(--space-xl);
  width: 360px;
  max-height: 480px;
  background: var(--bg-card);
  border: var(--border-glow);
  border-radius: var(--radius-2xl);
  box-shadow: var(--glow-intense);
  z-index: 200;
  overflow: hidden;
  backdrop-filter: blur(30px);
  animation: slideInDown 0.3s ease;
}

@keyframes slideInDown {
  0% {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xl);
  border-bottom: var(--border-secondary);
  background: rgba(0, 212, 255, 0.05);
}

.notifications-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: 700;
}

.clear-btn {
  background: transparent;
  border: var(--border-secondary);
  color: var(--text-secondary);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-bounce);
  font-size: var(--text-sm);
  font-weight: 600;
}

.clear-btn:hover {
  border-color: var(--primary-blue);
  color: var(--text-primary);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: var(--glow-secondary);
}

.notifications-list {
  max-height: 320px;
  overflow-y: auto;
}

/* 通知项目样式 */
.notification-item {
  display: flex;
  gap: var(--space-lg);
  padding: var(--space-lg);
  border-bottom: var(--border-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.notification-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: var(--gradient-primary);
  transform: scaleY(0);
  transition: transform var(--transition-base);
}

.notification-item:hover {
  background: rgba(0, 212, 255, 0.1);
  transform: translateX(8px);
}

.notification-item:hover::before {
  transform: scaleY(1);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item.success i {
  color: #2ecc71;
}

.notification-item.error i {
  color: #ff4757;
}

.notification-item.warning i {
  color: #ffa726;
}

.notification-item.info i {
  color: var(--primary-blue);
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 var(--space-sm) 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

.notification-content p {
  margin: 0 0 var(--space-sm) 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.notification-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: 500;
}
</style> 