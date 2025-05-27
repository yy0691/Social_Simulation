<template>
  <div 
    :class="[
      'glass-panel',
      variant,
      { 'glowing': glowing, 'elevated': elevated }
    ]"
    :style="customStyle"
  >
    <div class="glass-content">
      <slot />
    </div>
    <div v-if="glowing" class="panel-glow"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'default' | 'neon' | 'transparent';
  glowing?: boolean;
  elevated?: boolean;
  customClass?: string;
  width?: string;
  height?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  glowing: false,
  elevated: false,
  customClass: '',
  width: 'auto',
  height: 'auto'
});

const customStyle = computed(() => ({
  width: props.width,
  height: props.height
}));
</script>

<style scoped>
.glass-panel {
  position: relative;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.glass-panel.default {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.glass-panel.neon {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.1),
    0 8px 32px rgba(0, 0, 0, 0.1);
}

.glass-panel.transparent {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-panel.elevated {
  transform: translateY(-2px);
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

.glass-panel.glowing::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    45deg,
    rgba(0, 212, 255, 0.1),
    rgba(255, 0, 150, 0.1),
    rgba(255, 204, 0, 0.1)
  );
  border-radius: inherit;
  opacity: 0;
  animation: glow-pulse 3s ease-in-out infinite;
  pointer-events: none;
}

.glass-content {
  position: relative;
  z-index: 1;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(0, 212, 255, 0.1) 0%,
    transparent 70%
  );
  opacity: 0;
  animation: glow-pulse 2s ease-in-out infinite;
  pointer-events: none;
}

/* 动画效果 */
@keyframes glow-pulse {
  0%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .glass-content {
    padding: 16px;
  }
  
  .glass-panel {
    border-radius: 12px;
  }
}

/* 深色主题适配 */
.dark .glass-panel.default {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .glass-panel.transparent {
  background: rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.05);
}
</style> 