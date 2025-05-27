<template>
  <nav class="game-navigation">
    <div class="nav-container">
      <!-- 导航标签 -->
      <div class="nav-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="[
            'nav-tab',
            { 
              'active': activeTab === tab.key,
              'disabled': tab.disabled
            }
          ]"
          @click="handleTabClick(tab)"
          :disabled="tab.disabled"
        >
          <div class="tab-content">
            <i :class="tab.icon" class="tab-icon"></i>
            <span class="tab-text">{{ tab.label }}</span>
            
            <!-- 通知徽章 -->
            <div
              v-if="tab.badge && tab.badge > 0"
              class="notification-badge"
            >
              {{ tab.badge > 99 ? '99+' : tab.badge }}
            </div>
          </div>
          
          <!-- 激活指示器 -->
          <div class="tab-indicator"></div>
          
          <!-- 悬停效果 -->
          <div class="tab-glow"></div>
        </button>
      </div>
      
      <!-- 右侧状态区域 -->
      <div class="nav-status">
        <!-- 在线状态指示器 -->
        <div
          :class="[
            'online-indicator',
            connectionStatus
          ]"
        >
          <i :class="statusIcon"></i>
          <span>{{ statusText }}</span>
        </div>
        
        <!-- 额外的操作按钮 -->
        <div v-if="showActions" class="nav-actions">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
    
    <!-- 导航背景光效 -->
    <div class="nav-background-glow"></div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export interface NavigationTab {
  key: string;
  label: string;
  icon: string;
  badge?: number;
  disabled?: boolean;
}

interface Props {
  tabs: NavigationTab[];
  activeTab: string;
  connectionStatus?: 'online' | 'offline' | 'connecting';
  showActions?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  connectionStatus: 'online',
  showActions: false
});

const emit = defineEmits<{
  'tab-change': [tabKey: string];
  'tab-click': [tab: NavigationTab];
}>();

const statusConfig = {
  online: {
    icon: 'fas fa-circle',
    text: '在线',
    class: 'online'
  },
  offline: {
    icon: 'fas fa-circle',
    text: '离线',
    class: 'offline'
  },
  connecting: {
    icon: 'fas fa-spinner fa-spin',
    text: '连接中',
    class: 'connecting'
  }
};

const statusIcon = computed(() => {
  return statusConfig[props.connectionStatus].icon;
});

const statusText = computed(() => {
  return statusConfig[props.connectionStatus].text;
});

const handleTabClick = (tab: NavigationTab) => {
  if (tab.disabled) return;
  
  emit('tab-click', tab);
  emit('tab-change', tab.key);
};
</script>

<style scoped>
.game-navigation {
  position: relative;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
}

.nav-tabs {
  display: flex;
  gap: 4px;
}

.nav-tab {
  position: relative;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
  overflow: hidden;
  outline: none;
  min-width: 120px;
}

.tab-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  position: relative;
  z-index: 2;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: color 0.3s ease;
}

.tab-icon {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.tab-text {
  font-size: 14px;
  white-space: nowrap;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #ff0066, #ff3399);
  color: white;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 0, 102, 0.4);
  animation: badge-pulse 2s ease-in-out infinite;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #00d4ff, #0099cc);
  border-radius: 1px;
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.tab-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.1),
    rgba(0, 153, 204, 0.1)
  );
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* 导航标签状态 */
.nav-tab:hover .tab-content {
  color: rgba(255, 255, 255, 0.9);
}

.nav-tab:hover .tab-icon {
  transform: scale(1.1);
}

.nav-tab:hover .tab-glow {
  opacity: 1;
}

.nav-tab:hover .tab-indicator {
  width: 80%;
}

.nav-tab.active .tab-content {
  color: #ffffff;
}

.nav-tab.active .tab-icon {
  transform: scale(1.1);
  color: #00d4ff;
}

.nav-tab.active .tab-indicator {
  width: 100%;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.nav-tab.active .tab-glow {
  opacity: 1;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.2),
    rgba(0, 153, 204, 0.2)
  );
}

.nav-tab.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-tab.disabled:hover .tab-glow {
  opacity: 0;
}

/* 右侧状态区域 */
.nav-status {
  display: flex;
  align-items: center;
  gap: 16px;
}

.online-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.online-indicator.online {
  color: #00d4ff;
  border-color: rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.1);
}

.online-indicator.online i {
  animation: online-pulse 2s ease-in-out infinite;
}

.online-indicator.offline {
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
  background: rgba(231, 76, 60, 0.1);
}

.online-indicator.connecting {
  color: #f39c12;
  border-color: rgba(243, 156, 18, 0.3);
  background: rgba(243, 156, 18, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 背景光效 */
.nav-background-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 212, 255, 0.05) 50%,
    transparent 100%
  );
  opacity: 0;
  animation: nav-glow 4s ease-in-out infinite;
}

/* 动画 */
@keyframes badge-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes online-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes nav-glow {
  0%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
    height: 56px;
  }
  
  .nav-tab {
    min-width: 100px;
  }
  
  .tab-content {
    padding: 10px 16px;
    gap: 6px;
  }
  
  .tab-text {
    font-size: 13px;
  }
  
  .tab-icon {
    font-size: 14px;
  }
  
  .online-indicator {
    font-size: 11px;
    padding: 4px 8px;
  }
}

@media (max-width: 640px) {
  .tab-text {
    display: none;
  }
  
  .nav-tab {
    min-width: 48px;
  }
  
  .tab-content {
    padding: 10px 12px;
  }
  
  .nav-status span {
    display: none;
  }
}

/* 深色主题适配 */
.dark .game-navigation {
  background: rgba(0, 0, 0, 0.5);
  border-bottom-color: rgba(255, 255, 255, 0.05);
}

.dark .nav-tab.active .tab-glow {
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.25),
    rgba(0, 153, 204, 0.25)
  );
}

.dark .online-indicator {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.05);
}
</style> 