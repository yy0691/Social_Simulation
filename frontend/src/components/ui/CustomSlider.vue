<template>
  <div 
    :class="[
      'custom-slider',
      {
        'slider-disabled': disabled,
        'slider-vertical': vertical
      }
    ]"
  >
    <!-- 滑块轨道 -->
    <div 
      ref="trackRef"
      class="slider-track"
      @mousedown="startDrag"
      @touchstart="startDrag"
    >
      <!-- 已填充部分 -->
      <div 
        class="slider-fill"
        :style="fillStyle"
      >
        <div class="fill-glow"></div>
      </div>
      
      <!-- 滑块手柄 -->
      <div 
        class="slider-thumb"
        :style="thumbStyle"
        @mousedown.stop="startDrag"
        @touchstart.stop="startDrag"
      >
        <div class="thumb-inner">
          <div class="thumb-glow"></div>
        </div>
        
        <!-- 数值显示 -->
        <div v-if="showValue" class="value-display">
          {{ displayValue }}
        </div>
      </div>
      
      <!-- 刻度标记 -->
      <div v-if="showTicks" class="slider-ticks">
        <div
          v-for="tick in ticks"
          :key="tick.value"
          class="tick-mark"
          :style="getTickStyle(tick.value)"
        >
          <span v-if="tick.label" class="tick-label">{{ tick.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  modelValue: number
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  vertical?: boolean
  showValue?: boolean
  showTicks?: boolean
  tickLabels?: Record<number, string>
  formatValue?: (value: number) => string
}

const props = withDefaults(defineProps<Props>(), {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
  vertical: false,
  showValue: false,
  showTicks: false,
  tickLabels: () => ({})
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'change': [value: number]
  'input': [value: number]
}>()

// 响应式数据
const trackRef = ref<HTMLElement>()
const isDragging = ref(false)

// 计算属性
const normalizedValue = computed(() => {
  return Math.max(props.min, Math.min(props.max, props.modelValue))
})

const percentage = computed(() => {
  const range = props.max - props.min
  const value = normalizedValue.value - props.min
  return (value / range) * 100
})

const fillStyle = computed(() => {
  if (props.vertical) {
    return {
      height: `${percentage.value}%`
    }
  } else {
    return {
      width: `${percentage.value}%`
    }
  }
})

const thumbStyle = computed(() => {
  if (props.vertical) {
    return {
      bottom: `${percentage.value}%`
    }
  } else {
    return {
      left: `${percentage.value}%`
    }
  }
})

const displayValue = computed(() => {
  if (props.formatValue) {
    return props.formatValue(normalizedValue.value)
  }
  return normalizedValue.value.toString()
})

const ticks = computed(() => {
  if (!props.showTicks) return []
  
  const range = props.max - props.min
  const stepCount = Math.floor(range / props.step)
  const tickStep = Math.max(1, Math.floor(stepCount / 10)) * props.step
  
  const tickArray = []
  for (let i = props.min; i <= props.max; i += tickStep) {
    tickArray.push({
      value: i,
      label: props.tickLabels[i] || ''
    })
  }
  
  return tickArray
})

// 方法
const getTickStyle = (value: number) => {
  const range = props.max - props.min
  const position = ((value - props.min) / range) * 100
  
  if (props.vertical) {
    return { bottom: `${position}%` }
  } else {
    return { left: `${position}%` }
  }
}

const updateValue = (clientX: number, clientY: number) => {
  if (!trackRef.value || props.disabled) return
  
  const rect = trackRef.value.getBoundingClientRect()
  let percentage: number
  
  if (props.vertical) {
    percentage = 1 - (clientY - rect.top) / rect.height
  } else {
    percentage = (clientX - rect.left) / rect.width
  }
  
  percentage = Math.max(0, Math.min(1, percentage))
  
  const range = props.max - props.min
  let newValue = props.min + (percentage * range)
  
  // 对齐到步长
  newValue = Math.round(newValue / props.step) * props.step
  newValue = Math.max(props.min, Math.min(props.max, newValue))
  
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
    emit('input', newValue)
    emit('change', newValue)
  }
}

const startDrag = (event: MouseEvent | TouchEvent) => {
  if (props.disabled) return
  
  event.preventDefault()
  isDragging.value = true
  
  const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
  const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY
  
  updateValue(clientX, clientY)
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('touchmove', onTouchMove)
  document.addEventListener('touchend', onTouchEnd)
}

const onMouseMove = (event: MouseEvent) => {
  if (!isDragging.value) return
  updateValue(event.clientX, event.clientY)
}

const onTouchMove = (event: TouchEvent) => {
  if (!isDragging.value) return
  event.preventDefault()
  updateValue(event.touches[0].clientX, event.touches[0].clientY)
}

const onMouseUp = () => {
  endDrag()
}

const onTouchEnd = () => {
  endDrag()
}

const endDrag = () => {
  isDragging.value = false
  
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('touchmove', onTouchMove)
  document.removeEventListener('touchend', onTouchEnd)
}

// 键盘事件
const handleKeyDown = (event: KeyboardEvent) => {
  if (props.disabled) return
  
  let delta = 0
  
  switch (event.key) {
    case 'ArrowLeft':
    case 'ArrowDown':
      delta = -props.step
      break
    case 'ArrowRight':
    case 'ArrowUp':
      delta = props.step
      break
    case 'PageDown':
      delta = -(props.max - props.min) / 10
      break
    case 'PageUp':
      delta = (props.max - props.min) / 10
      break
    case 'Home':
      emit('update:modelValue', props.min)
      return
    case 'End':
      emit('update:modelValue', props.max)
      return
    default:
      return
  }
  
  event.preventDefault()
  const newValue = Math.max(props.min, Math.min(props.max, props.modelValue + delta))
  emit('update:modelValue', newValue)
}

// 生命周期
onMounted(() => {
  if (trackRef.value) {
    trackRef.value.addEventListener('keydown', handleKeyDown)
  }
})

onUnmounted(() => {
  endDrag()
})
</script>

<style scoped>
.custom-slider {
  position: relative;
  user-select: none;
  touch-action: none;
}

.slider-track {
  position: relative;
  width: 100%;
  height: 0.5rem;
  background: rgba(55, 65, 81, 0.6);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.slider-vertical .slider-track {
  width: 0.5rem;
  height: 100px;
  min-height: 100px;
}

.slider-track:hover {
  background: rgba(55, 65, 81, 0.8);
  transform: scaleY(1.2);
}

.slider-vertical .slider-track:hover {
  transform: scaleX(1.2);
}

.slider-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0099cc);
  border-radius: inherit;
  transition: all 0.3s ease;
  overflow: hidden;
}

.slider-vertical .slider-fill {
  bottom: 0;
  top: auto;
  width: 100%;
  background: linear-gradient(0deg, #00d4ff, #0099cc);
}

.fill-glow {
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.4), rgba(0, 153, 204, 0.4));
  border-radius: inherit;
  animation: fill-pulse 2s ease-in-out infinite;
}

.slider-vertical .fill-glow {
  background: linear-gradient(0deg, rgba(0, 212, 255, 0.4), rgba(0, 153, 204, 0.4));
}

.slider-thumb {
  position: absolute;
  top: 50%;
  width: 1.25rem;
  height: 1.25rem;
  transform: translate(-50%, -50%);
  cursor: grab;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.slider-vertical .slider-thumb {
  left: 50%;
  top: auto;
  transform: translate(-50%, 50%);
}

.slider-thumb:active {
  cursor: grabbing;
}

.thumb-inner {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #ffffff, #f8fafc);
  border-radius: 50%;
  border: 2px solid rgba(0, 212, 255, 0.3);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.15),
    0 0 0 4px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.slider-thumb:hover .thumb-inner {
  transform: scale(1.2);
  border-color: rgba(0, 212, 255, 0.6);
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.2),
    0 0 0 6px rgba(0, 212, 255, 0.2);
}

.thumb-glow {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.4) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.slider-thumb:hover .thumb-glow {
  opacity: 1;
  animation: thumb-glow-pulse 1.5s ease-in-out infinite;
}

.value-display {
  position: absolute;
  top: -2.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: #ffffff;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.slider-vertical .value-display {
  top: 50%;
  left: -3rem;
  transform: translateY(-50%);
}

.slider-thumb:hover .value-display {
  opacity: 1;
}

.slider-ticks {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  height: 1rem;
}

.slider-vertical .slider-ticks {
  top: 0;
  left: 100%;
  right: auto;
  bottom: 0;
  width: 2rem;
  height: auto;
}

.tick-mark {
  position: absolute;
  top: 0.25rem;
  width: 1px;
  height: 0.5rem;
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-50%);
}

.slider-vertical .tick-mark {
  top: auto;
  left: 0.25rem;
  width: 0.5rem;
  height: 1px;
  transform: translateY(50%);
}

.tick-label {
  position: absolute;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
}

.slider-vertical .tick-label {
  top: 50%;
  left: 1rem;
  transform: translateY(-50%);
}

/* 禁用状态 */
.slider-disabled {
  opacity: 0.5;
  pointer-events: none;
}

.slider-disabled .slider-track {
  cursor: not-allowed;
}

/* 动画 */
@keyframes fill-pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

@keyframes thumb-glow-pulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

/* 深色主题适配 */
.dark .slider-track {
  background: rgba(17, 24, 39, 0.8);
  border-color: rgba(255, 255, 255, 0.05);
}

.dark .slider-track:hover {
  background: rgba(17, 24, 39, 0.9);
}

.dark .value-display {
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark .tick-mark {
  background: rgba(255, 255, 255, 0.2);
}

.dark .tick-label {
  color: rgba(255, 255, 255, 0.6);
}
</style> 