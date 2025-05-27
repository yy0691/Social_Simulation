<template>
  <div 
    :class="[
      'toggle-switch',
      {
        'toggle-checked': modelValue,
        'toggle-disabled': disabled
      }
    ]"
    @click="handleToggle"
  >
    <!-- 开关轨道 -->
    <div class="toggle-track">
      <!-- 开关按钮 -->
      <div class="toggle-thumb">
        <div class="thumb-glow"></div>
      </div>
      
      <!-- 轨道发光效果 -->
      <div class="track-glow"></div>
    </div>
    
    <!-- 状态指示器 -->
    <div class="toggle-icons">
      <i class="toggle-icon-off fas fa-times"></i>
      <i class="toggle-icon-on fas fa-check"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  disabled?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  size: 'medium'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'change': [value: boolean]
}>()

const handleToggle = () => {
  if (props.disabled) return
  
  const newValue = !props.modelValue
  emit('update:modelValue', newValue)
  emit('change', newValue)
}
</script>

<style scoped>
.toggle-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-switch.toggle-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-track {
  position: relative;
  width: 3.5rem;
  height: 1.75rem;
  background: rgba(55, 65, 81, 0.8);
  border-radius: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.toggle-checked .toggle-track {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 1.25rem;
  height: 1.25rem;
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.2),
    0 1px 2px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-checked .toggle-thumb {
  transform: translateX(1.75rem);
  background: linear-gradient(135deg, #ffffff, #f0f9ff);
  box-shadow: 
    0 2px 8px rgba(0, 212, 255, 0.3),
    0 1px 3px rgba(0, 0, 0, 0.1);
}

.thumb-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: radial-gradient(circle, transparent 60%, rgba(0, 212, 255, 0.3) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.toggle-checked .thumb-glow {
  opacity: 1;
  animation: thumb-pulse 2s ease-in-out infinite;
}

.track-glow {
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: inherit;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.4),
    rgba(0, 153, 204, 0.4)
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.toggle-checked .track-glow {
  opacity: 1;
}

.toggle-icons {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.5rem;
  pointer-events: none;
}

.toggle-icon-off,
.toggle-icon-on {
  font-size: 0.7rem;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.6);
}

.toggle-icon-off {
  opacity: 1;
  transform: scale(1);
}

.toggle-icon-on {
  opacity: 0;
  transform: scale(0.8);
}

.toggle-checked .toggle-icon-off {
  opacity: 0;
  transform: scale(0.8);
}

.toggle-checked .toggle-icon-on {
  opacity: 1;
  transform: scale(1);
  color: rgba(255, 255, 255, 0.9);
}

/* 尺寸变体 */
.toggle-switch.small .toggle-track {
  width: 2.5rem;
  height: 1.25rem;
}

.toggle-switch.small .toggle-thumb {
  width: 0.875rem;
  height: 0.875rem;
}

.toggle-switch.small.toggle-checked .toggle-thumb {
  transform: translateX(1.25rem);
}

.toggle-switch.large .toggle-track {
  width: 4.5rem;
  height: 2.25rem;
}

.toggle-switch.large .toggle-thumb {
  width: 1.75rem;
  height: 1.75rem;
}

.toggle-switch.large.toggle-checked .toggle-thumb {
  transform: translateX(2.25rem);
}

/* 悬停效果 */
.toggle-switch:hover:not(.toggle-disabled) .toggle-track {
  transform: scale(1.05);
}

.toggle-switch:hover:not(.toggle-disabled) .toggle-thumb {
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.3),
    0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-switch:hover:not(.toggle-disabled).toggle-checked .toggle-thumb {
  box-shadow: 
    0 4px 12px rgba(0, 212, 255, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 动画 */
@keyframes thumb-pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

/* 深色主题适配 */
.dark .toggle-track {
  background: rgba(17, 24, 39, 0.9);
  border-color: rgba(255, 255, 255, 0.05);
}

.dark .toggle-thumb {
  background: linear-gradient(135deg, #f9fafb, #e5e7eb);
}

.dark .toggle-checked .toggle-thumb {
  background: linear-gradient(135deg, #ffffff, #f0f9ff);
}
</style> 