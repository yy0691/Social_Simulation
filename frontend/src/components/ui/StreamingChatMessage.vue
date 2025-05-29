<template>
  <div class="streaming-message-container">
    <!-- AI居民头像 -->
    <div class="avatar-container">
      <div class="avatar avatar-agent">
        <i class="fas fa-user-friends"></i>
      </div>
      <div v-if="!isComplete" class="streaming-pulse"></div>
    </div>

    <!-- 消息内容 -->
    <div class="message-content">
      <!-- 发送者信息 -->
      <div class="message-header">
        <span class="sender-name">{{ sender }}</span>
        <span class="streaming-status">
          <i v-if="!isComplete" class="fas fa-circle streaming-dot"></i>
          <span v-if="!isComplete">正在输入...</span>
          <span v-else>已完成</span>
        </span>
      </div>

      <!-- 流式消息气泡 -->
      <div class="message-bubble bubble-streaming">
        <div v-if="!hasStarted" class="waiting-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        
        <div v-else class="streaming-content">
          <span 
            v-for="(char, index) in displayedChars" 
            :key="index"
            class="char"
            :class="{ 'char-new': index === displayedChars.length - 1 }"
          >
            {{ char }}
          </span>
          <span v-if="!isComplete" class="cursor">|</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  agentName: string
  sender: string
  isComplete: boolean
}

const props = defineProps<Props>()

// 响应式数据
const hasStarted = ref(false)
const displayedChars = ref<string[]>([])
const eventSource = ref<EventSource | null>(null)

// 启动流式传输
const startStreaming = async () => {
  try {
    console.log(`🎬 开始监听 ${props.agentName} 的流式回复`)
    
    // 短暂延迟后开始显示
    setTimeout(() => {
      hasStarted.value = true
    }, 300)

    // 创建EventSource连接
    const streamUrl = `http://localhost:8000/api/v1/chat/stream/${encodeURIComponent(props.agentName)}`
    eventSource.value = new EventSource(streamUrl)
    
    eventSource.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'content':
            // 添加新字符
            displayedChars.value.push(data.char)
            break
            
          case 'complete':
            // 流式传输完成
            console.log(`✅ ${props.agentName} 流式传输完成`)
            stopStreaming()
            break
            
          case 'waiting':
            // 等待生成
            hasStarted.value = false
            break
            
          case 'timeout':
          case 'error':
            console.log(`❌ ${props.agentName} 流式传输${data.type}`)
            stopStreaming()
            break
        }
      } catch (error) {
        console.error(`❌ ${props.agentName} 解析流式数据失败:`, error)
      }
    }

    eventSource.value.onerror = (error) => {
      console.error(`❌ ${props.agentName} 流式连接错误:`, error)
      setTimeout(stopStreaming, 1000)
    }

  } catch (error) {
    console.error(`❌ 启动 ${props.agentName} 流式传输失败:`, error)
  }
}

// 停止流式传输
const stopStreaming = () => {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = null
  }
}

// 监听完成状态
watch(() => props.isComplete, (isComplete) => {
  if (isComplete) {
    stopStreaming()
  }
})

// 生命周期
onMounted(() => {
  startStreaming()
})

onUnmounted(() => {
  stopStreaming()
})
</script>

<style scoped>
.streaming-message-container {
  display: flex;
  margin-bottom: 1rem;
  gap: 0.75rem;
  animation: streamingSlideIn 0.3s ease-out;
}

/* 头像样式 */
.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: white;
}

.avatar-agent {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

.streaming-pulse {
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border-radius: 50%;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  animation: streamingPulse 2s ease-in-out infinite;
  z-index: -1;
}

/* 消息内容 */
.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
  gap: 0.5rem;
}

.sender-name {
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  font-size: 0.9rem;
}

.streaming-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

.streaming-dot {
  color: #4facfe;
  animation: streamingBlink 1s infinite;
}

/* 消息气泡 */
.bubble-streaming {
  background: rgba(79, 172, 254, 0.1);
  border: 1px solid rgba(79, 172, 254, 0.2);
  border-radius: 1rem;
  border-bottom-left-radius: 0.25rem;
  padding: 0.75rem 1rem;
  position: relative;
  backdrop-filter: blur(10px);
  min-height: 2.5rem;
  display: flex;
  align-items: center;
}

/* 等待动画 */
.waiting-dots {
  display: flex;
  gap: 0.25rem;
}

.waiting-dots span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #4facfe;
  animation: waitingDots 1.4s ease-in-out infinite;
}

.waiting-dots span:nth-child(1) { animation-delay: 0s; }
.waiting-dots span:nth-child(2) { animation-delay: 0.2s; }
.waiting-dots span:nth-child(3) { animation-delay: 0.4s; }

/* 流式内容 */
.streaming-content {
  line-height: 1.5;
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
  animation: cursorBlink 1s infinite;
  color: #4facfe;
  font-weight: bold;
}

/* 动画定义 */
@keyframes streamingSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes streamingPulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
}

@keyframes streamingBlink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.3;
  }
}

@keyframes waitingDots {
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

@keyframes cursorBlink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 深色主题 */
.dark .sender-name {
  color: var(--color-text-primary, #f9fafb);
}

.dark .streaming-content {
  color: var(--color-text-primary, #f9fafb);
}

.dark .streaming-status {
  color: var(--color-text-secondary, #9ca3af);
}
</style> 