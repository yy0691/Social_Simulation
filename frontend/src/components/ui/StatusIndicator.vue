<template>
  <div
    :class="[
      'status-indicator',
      status,
      size,
      {
        'animated': animated,
        'pulsing': pulsing
      }
    ]"
  >
    <!-- 状态图标 -->
    <div class="status-icon">
      <i :class="statusIcon" v-if="!loading"></i>
      <div v-if="loading || status === 'processing'" class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
    </div>
    
    <!-- 状态文本 -->
    <div v-if="showText || $slots.default" class="status-text">
      <slot>{{ statusText }}</slot>
    </div>
    
    <!-- 处理点动画 -->
    <div v-if="status === 'processing'" class="processing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
    
    <!-- 状态光晕 -->
    <div class="status-glow"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  status?: 'online' | 'offline' | 'processing' | 'success' | 'warning' | 'error' | 'idle';
  size?: 'small' | 'medium' | 'large';
  showText?: boolean;
  animated?: boolean;
  pulsing?: boolean;
  loading?: boolean;
  customIcon?: string;
  customText?: string;
}

const props = withDefaults(defineProps<Props>(), {
  status: 'idle',
  size: 'medium',
  showText: true,
  animated: true,
  pulsing: false,
  loading: false
});

const statusConfig = {
  online: {
    icon: 'fas fa-circle',
    text: '在线',
    color: '#00d4ff'
  },
  offline: {
    icon: 'fas fa-circle',
    text: '离线',
    color: '#e74c3c'
  },
  processing: {
    icon: 'fas fa-brain',
    text: 'AI正在思考中',
    color: '#f39c12'
  },
  success: {
    icon: 'fas fa-check-circle',
    text: '成功',
    color: '#00b894'
  },
  warning: {
    icon: 'fas fa-exclamation-triangle',
    text: '警告',
    color: '#fdcb6e'
  },
  error: {
    icon: 'fas fa-times-circle',
    text: '错误',
    color: '#e74c3c'
  },
  idle: {
    icon: 'fas fa-circle',
    text: '空闲',
    color: '#636e72'
  }
};

const statusIcon = computed(() => {
  return props.customIcon || statusConfig[props.status].icon;
});

const statusText = computed(() => {
  return props.customText || statusConfig[props.status].text;
});

const statusColor = computed(() => {
  return statusConfig[props.status].color;
});
</script>

<style scoped>
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  padding: 8px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

/* 尺寸变体 */
.status-indicator.small {
  padding: 4px 8px;
  gap: 4px;
  font-size: 12px;
}

.status-indicator.small .status-icon {
  width: 16px;
  height: 16px;
  font-size: 10px;
}

.status-indicator.medium {
  padding: 8px 12px;
  gap: 8px;
  font-size: 14px;
}

.status-indicator.medium .status-icon {
  width: 20px;
  height: 20px;
  font-size: 12px;
}

.status-indicator.large {
  padding: 12px 16px;
  gap: 10px;
  font-size: 16px;
}

.status-indicator.large .status-icon {
  width: 24px;
  height: 24px;
  font-size: 14px;
}

/* 状态图标 */
.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  position: relative;
  min-width: 20px;
  min-height: 20px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: spin 1s linear infinite;
}

/* 状态文本 */
.status-text {
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* 处理点动画 */
.processing-dots {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.processing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #f39c12;
  animation: dot-bounce 1.4s ease-in-out infinite both;
}

.processing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.processing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

/* 状态光晕 */
.status-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

/* 状态变体样式 */
.status-indicator.online {
  border-color: rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.1);
}

.status-indicator.online .status-icon {
  color: #00d4ff;
}

.status-indicator.online.animated .status-icon {
  animation: online-pulse 2s ease-in-out infinite;
}

.status-indicator.offline {
  border-color: rgba(231, 76, 60, 0.3);
  background: rgba(231, 76, 60, 0.1);
}

.status-indicator.offline .status-icon {
  color: #e74c3c;
}

.status-indicator.processing {
  border-color: rgba(243, 156, 18, 0.3);
  background: rgba(243, 156, 18, 0.1);
}

.status-indicator.processing .status-icon {
  color: #f39c12;
}

.status-indicator.processing.animated {
  animation: processing-glow 2s ease-in-out infinite;
}

.status-indicator.success {
  border-color: rgba(0, 184, 148, 0.3);
  background: rgba(0, 184, 148, 0.1);
}

.status-indicator.success .status-icon {
  color: #00b894;
}

.status-indicator.warning {
  border-color: rgba(253, 203, 110, 0.3);
  background: rgba(253, 203, 110, 0.1);
}

.status-indicator.warning .status-icon {
  color: #fdcb6e;
}

.status-indicator.error {
  border-color: rgba(231, 76, 60, 0.3);
  background: rgba(231, 76, 60, 0.1);
}

.status-indicator.error .status-icon {
  color: #e74c3c;
}

.status-indicator.idle {
  border-color: rgba(99, 110, 114, 0.3);
  background: rgba(99, 110, 114, 0.1);
}

.status-indicator.idle .status-icon {
  color: #636e72;
}

/* 脉冲效果 */
.status-indicator.pulsing .status-glow {
  opacity: 1;
  animation: status-pulse 2s ease-in-out infinite;
}

.status-indicator.online .status-glow {
  background: radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%);
}

.status-indicator.processing .status-glow {
  background: radial-gradient(circle, rgba(243, 156, 18, 0.3) 0%, transparent 70%);
}

.status-indicator.success .status-glow {
  background: radial-gradient(circle, rgba(0, 184, 148, 0.3) 0%, transparent 70%);
}

.status-indicator.warning .status-glow {
  background: radial-gradient(circle, rgba(253, 203, 110, 0.3) 0%, transparent 70%);
}

.status-indicator.error .status-glow {
  background: radial-gradient(circle, rgba(231, 76, 60, 0.3) 0%, transparent 70%);
}

/* 动画定义 */
@keyframes online-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

@keyframes processing-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(243, 156, 18, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(243, 156, 18, 0.6);
  }
}

@keyframes status-pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

@keyframes dot-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .status-indicator.large {
    padding: 10px 14px;
    font-size: 15px;
  }
  
  .status-indicator.medium {
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .status-indicator.small {
    padding: 4px 6px;
    font-size: 11px;
  }
}

/* 深色主题适配 */
.dark .status-indicator {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .status-text {
  color: #ffffff;
}
</style> 