<template>
  <div class="streaming-message" :class="{ 'message-complete': isComplete }">
    <!-- 头像和名称 -->
    <div class="message-header">
      <div class="agent-avatar">
        <i class="fas fa-user-friends"></i>
        <div v-if="isTyping" class="typing-pulse"></div>
      </div>
      <div class="agent-info">
        <span class="agent-name">{{ agentName }}</span>
        <span class="typing-status" v-if="isTyping">正在输入中...</span>
        <span class="typing-status" v-else-if="isStreaming">{{ streamProgress }}%</span>
      </div>
    </div>

    <!-- 消息内容 -->
    <div class="message-content">
      <div v-if="!hasStarted" class="waiting-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      
      <div v-else class="streaming-text">
        <span 
          v-for="(char, index) in displayedChars" 
          :key="index"
          class="char"
          :class="{ 'char-new': index === displayedChars.length - 1 }"
        >
          {{ char }}
        </span>
        <span v-if="isStreaming && !isComplete" class="cursor">|</span>
      </div>
    </div>

    <!-- 进度条 -->
    <div v-if="isStreaming" class="progress-bar">
      <div class="progress-fill" :style="{ width: `${streamProgress}%` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  agentName: string
  isVisible: boolean
}

const props = defineProps<Props>()

// 响应式数据
const hasStarted = ref(false)
const isTyping = ref(true)
const isStreaming = ref(false)
const isComplete = ref(false)
const displayedChars = ref<string[]>([])
const streamProgress = ref(0)
const eventSource = ref<EventSource | null>(null)

// 计算属性
const displayedText = computed(() => displayedChars.value.join(''))

// 监听组件显示状态
watch(() => props.isVisible, (visible) => {
  if (visible) {
    startStreaming()
  } else {
    stopStreaming()
  }
})

// 开始流式传输
const startStreaming = async () => {
  try {
    console.log(`🎭 开始监听 ${props.agentName} 的实时流式回复`)
    
    // 极短的等待时间
    setTimeout(() => {
      hasStarted.value = true
      isTyping.value = false
      isStreaming.value = true
    }, 100)  // 从500ms减少到100ms，几乎立即开始

    // 立即创建EventSource连接
    const streamUrl = `http://localhost:8000/api/v1/chat/stream/${encodeURIComponent(props.agentName)}`
    console.log(`🔗 连接流式API: ${streamUrl}`)
    
    eventSource.value = new EventSource(streamUrl)
    
    eventSource.value.onopen = () => {
      console.log(`✅ ${props.agentName} 流式连接已建立`)
    }
    
    eventSource.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log(`📨 ${props.agentName} 收到数据:`, data)
        
        switch (data.type) {
          case 'content':
            // 添加新字符
            displayedChars.value.push(data.char)
            streamProgress.value = Math.round((data.progress || 0) * 100)
            console.log(`📝 ${props.agentName} 新字符: "${data.char}", 进度: ${streamProgress.value}%`)
            break
            
          case 'complete':
            // 流式传输完成
            isStreaming.value = false
            isComplete.value = true
            streamProgress.value = 100
            console.log(`✅ ${props.agentName} 实时流式传输完成`)
            setTimeout(() => {
              stopStreaming()
            }, 2000) // 2秒后关闭连接
            break
            
          case 'waiting':
            // 等待开始生成
            console.log(`⏳ ${props.agentName} 等待开始生成...`)
            break
            
          case 'timeout':
            // 超时
            console.log(`⏰ ${props.agentName} 流式传输超时`)
            stopStreaming()
            break
            
          case 'error':
            // 错误
            console.log(`❌ ${props.agentName} 流式传输出错`)
            stopStreaming()
            break
        }
      } catch (error) {
        console.error(`❌ ${props.agentName} 解析实时流式数据失败:`, error, '原始数据:', event.data)
      }
    }

    eventSource.value.onerror = (error) => {
      console.error(`❌ ${props.agentName} 实时流式连接错误:`, error)
      console.log(`🔍 ${props.agentName} 连接状态:`, eventSource.value?.readyState)
      
      // 不立即停止，尝试重连
      setTimeout(() => {
        if (eventSource.value && eventSource.value.readyState === EventSource.CLOSED) {
          console.log(`🔄 ${props.agentName} 尝试重连...`)
          stopStreaming()
          setTimeout(startStreaming, 1000) // 1秒后重试
        }
      }, 500)
    }

  } catch (error) {
    console.error(`❌ 启动 ${props.agentName} 实时流式传输失败:`, error)
  }
}

// 停止流式传输
const stopStreaming = () => {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
}

// 生命周期
onMounted(() => {
  if (props.isVisible) {
    startStreaming()
  }
})

onUnmounted(() => {
  stopStreaming()
})

// 导出方法
defineExpose({
  startStreaming,
  stopStreaming,
  reset: () => {
    hasStarted.value = false
    isTyping.value = true
    isStreaming.value = false
    isComplete.value = false
    displayedChars.value = []
    streamProgress.value = 0
  }
})
</script>

<style scoped>
.streaming-message {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(240, 147, 251, 0.1);
  border: 1px solid rgba(240, 147, 251, 0.2);
  border-radius: 0.75rem;
  border-bottom-left-radius: 0.25rem;
  backdrop-filter: blur(10px);
  margin: 0.5rem 0;
  max-height: 150px;
  overflow-y: auto;
  animation: slideInUp 0.3s ease-out;
}

.message-complete {
  background: rgba(79, 172, 254, 0.1);
  border-color: rgba(79, 172, 254, 0.2);
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.agent-avatar {
  position: relative;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  flex-shrink: 0;
}

.typing-pulse {
  position: absolute;
  top: -1px;
  right: -1px;
  width: 8px;
  height: 8px;
  background: #f093fb;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.agent-name {
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  font-size: 0.9rem;
}

.typing-status {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  font-style: italic;
}

.message-content {
  min-height: 1.5rem;
  display: flex;
  align-items: flex-start;
  flex: 1;
  overflow-y: auto;
}

.waiting-dots {
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem 0;
}

.waiting-dots span {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
  background: #f093fb;
  animation: typingDots 1.4s ease-in-out infinite;
}

.waiting-dots span:nth-child(1) { animation-delay: 0s; }
.waiting-dots span:nth-child(2) { animation-delay: 0.2s; }
.waiting-dots span:nth-child(3) { animation-delay: 0.4s; }

.streaming-text {
  line-height: 1.5;
  font-size: 0.9rem;
  color: var(--color-text-primary, #1f2937);
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.char {
  transition: all 0.1s ease;
}

.char-new {
  animation: charAppear 0.2s ease-out;
}

.cursor {
  animation: blink 1s infinite;
  color: #f093fb;
  font-weight: bold;
}

.progress-bar {
  height: 0.2rem;
  background: rgba(240, 147, 251, 0.2);
  border-radius: 0.1rem;
  overflow: hidden;
  flex-shrink: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
  border-radius: 0.1rem;
  transition: width 0.2s ease;
}

/* 动画 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

@keyframes typingDots {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-0.5rem);
    opacity: 1;
  }
}

@keyframes charAppear {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 深色主题 */
.dark .agent-name {
  color: var(--color-text-primary, #f9fafb);
}

.dark .streaming-text {
  color: var(--color-text-primary, #f9fafb);
}

.dark .typing-status {
  color: var(--color-text-secondary, #9ca3af);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .streaming-message {
    padding: 0.75rem;
    margin: 0.75rem 0;
  }
  
  .agent-avatar {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
  }
  
  .streaming-text {
    font-size: 0.9rem;
  }
}
</style> 