<template>
  <button
    :class="[
      'neon-button',
      variant,
      size,
      {
        'loading': loading,
        'disabled': disabled,
        'glowing': glowing
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- 按钮内容 -->
    <span class="button-content">
      <i v-if="icon && !loading" :class="icon" class="button-icon"></i>
      <i v-if="loading" class="fas fa-spinner fa-spin button-icon"></i>
      <span v-if="$slots.default" class="button-text">
        <slot />
      </span>
    </span>
    
    <!-- 发光效果 -->
    <div class="btn-glow"></div>
    
    <!-- 点击波纹效果 -->
    <div class="ripple-effect"></div>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  icon?: string;
  loading?: boolean;
  disabled?: boolean;
  glowing?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  loading: false,
  disabled: false,
  glowing: false
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const isAnimating = ref(false);

const handleClick = (event: MouseEvent) => {
  if (props.disabled || props.loading) return;
  
  // 创建波纹效果
  createRipple(event);
  
  emit('click', event);
};

const createRipple = (event: MouseEvent) => {
  const button = event.currentTarget as HTMLElement;
  const ripple = button.querySelector('.ripple-effect') as HTMLElement;
  
  if (!ripple) return;
  
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;
  
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';
  
  ripple.classList.add('ripple-active');
  
  setTimeout(() => {
    ripple.classList.remove('ripple-active');
  }, 600);
};
</script>

<style scoped>
.neon-button {
  position: relative;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  outline: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* 按钮尺寸 */
.neon-button.small {
  padding: 8px 16px;
  font-size: 12px;
  min-height: 32px;
}

.neon-button.medium {
  padding: 12px 24px;
  font-size: 14px;
  min-height: 40px;
}

.neon-button.large {
  padding: 16px 32px;
  font-size: 16px;
  min-height: 48px;
}

/* 按钮变体 */
.neon-button.primary {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.neon-button.primary:hover {
  background: linear-gradient(135deg, #00e6ff, #00b3e6);
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.4),
    0 6px 20px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.neon-button.secondary {
  background: linear-gradient(135deg, #6c5ce7, #a29bfe);
  color: white;
  border: 1px solid rgba(108, 92, 231, 0.3);
}

.neon-button.secondary:hover {
  background: linear-gradient(135deg, #7d70e8, #b3aaff);
  box-shadow: 
    0 0 20px rgba(108, 92, 231, 0.4),
    0 6px 20px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.neon-button.success {
  background: linear-gradient(135deg, #00b894, #00cec9);
  color: white;
  border: 1px solid rgba(0, 184, 148, 0.3);
}

.neon-button.warning {
  background: linear-gradient(135deg, #fdcb6e, #f39c12);
  color: white;
  border: 1px solid rgba(253, 203, 110, 0.3);
}

.neon-button.danger {
  background: linear-gradient(135deg, #e17055, #d63031);
  color: white;
  border: 1px solid rgba(225, 112, 85, 0.3);
}

.neon-button.ghost {
  background: transparent;
  color: #00d4ff;
  border: 2px solid #00d4ff;
}

.neon-button.ghost:hover {
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.2),
    0 4px 15px rgba(0, 0, 0, 0.2);
}

/* 按钮内容 */
.button-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-icon {
  font-size: 1em;
}

.button-text {
  white-space: nowrap;
}

/* 发光效果 */
.btn-glow {
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

.neon-button.glowing .btn-glow {
  opacity: 1;
  animation: glow-pulse 2s ease-in-out infinite;
}

.neon-button.primary .btn-glow {
  background: linear-gradient(135deg, 
    rgba(0, 212, 255, 0.3), 
    rgba(0, 153, 204, 0.3)
  );
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
}

/* 波纹效果 */
.ripple-effect {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: scale(0);
  pointer-events: none;
}

.ripple-effect.ripple-active {
  animation: ripple 0.6s ease-out;
}

/* 禁用状态 */
.neon-button.disabled,
.neon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.neon-button.disabled:hover,
.neon-button:disabled:hover {
  transform: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* 加载状态 */
.neon-button.loading {
  cursor: default;
}

.neon-button.loading .button-icon {
  animation: spin 1s linear infinite;
}

/* 动画 */
@keyframes glow-pulse {
  0%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .neon-button.large {
    padding: 14px 28px;
    font-size: 15px;
  }
  
  .neon-button.medium {
    padding: 10px 20px;
    font-size: 13px;
  }
}

/* 深色主题适配 */
.dark .neon-button.ghost {
  border-color: #00d4ff;
  color: #00d4ff;
}

.dark .neon-button.ghost:hover {
  background: rgba(0, 212, 255, 0.15);
}
</style> 