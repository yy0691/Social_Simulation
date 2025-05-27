<template>
  <div class="chat-message-list">
    <!-- 加载更多历史消息 -->
    <div v-if="hasMoreHistory" class="load-more-container">
      <NeonButton
        variant="ghost"
        size="small"
        icon="fas fa-arrow-up"
        :loading="loadingHistory"
        @click="loadMoreHistory"
      >
        加载更多历史消息
      </NeonButton>
    </div>

    <!-- 消息列表容器 -->
    <div
      ref="messagesContainer"
      class="messages-container"
      @scroll="onScroll"
    >
      <!-- 日期分隔符 -->
      <template v-for="(group, date) in groupedMessages" :key="date">
        <div class="date-separator">
          <div class="date-line"></div>
          <span class="date-text">{{ formatDate(date) }}</span>
          <div class="date-line"></div>
        </div>

        <!-- 该日期的消息 -->
        <ChatMessage
          v-for="message in group"
          :key="message.id"
          :content="message.content"
          :sender="message.sender"
          :timestamp="message.timestamp"
          :is-user="message.isUser"
          :is-a-i="message.isAI"
          :status="message.status"
          :show-status="message.showStatus"
          @message-click="onMessageClick(message)"
        />
      </template>

      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-comments"></i>
        </div>
        <h3>还没有消息</h3>
        <p>开始与AI居民对话吧！</p>
      </div>

      <!-- 正在输入指示器 -->
      <div v-if="showTypingIndicator" class="typing-indicator">
        <div class="typing-avatar">
          <i class="fas fa-robot"></i>
        </div>
        <div class="typing-content">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span class="typing-text">AI正在输入...</span>
        </div>
      </div>

      <!-- 滚动到底部按钮 -->
      <Transition name="scroll-to-bottom">
        <NeonButton
          v-if="showScrollToBottom"
          variant="primary"
          size="small"
          icon="fas fa-arrow-down"
          class="scroll-to-bottom-btn"
                     @click="() => scrollToBottom()"
          title="滚动到底部"
        >
          {{ unreadCount > 0 ? `${unreadCount} 条新消息` : '滚动到底部' }}
        </NeonButton>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import ChatMessage from './ChatMessage.vue'
import NeonButton from './NeonButton.vue'

interface Message {
  id: string
  content: string
  sender: string
  timestamp: string | Date
  isUser?: boolean
  isAI?: boolean
  status?: 'sending' | 'sent' | 'error'
  showStatus?: boolean
}

interface Props {
  messages: Message[]
  hasMoreHistory?: boolean
  loadingHistory?: boolean
  showTypingIndicator?: boolean
  autoScroll?: boolean
  maxHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  hasMoreHistory: false,
  loadingHistory: false,
  showTypingIndicator: false,
  autoScroll: true,
  maxHeight: '400px'
})

const emit = defineEmits<{
  loadMoreHistory: []
  messageClick: [message: Message]
  scroll: [{ scrollTop: number; scrollHeight: number; clientHeight: number }]
}>()

// 响应式数据
const messagesContainer = ref<HTMLElement>()
const showScrollToBottom = ref(false)
const unreadCount = ref(0)
const lastScrollTop = ref(0)
const autoScrollEnabled = ref(true)

// 计算属性
const groupedMessages = computed(() => {
  const groups: Record<string, Message[]> = {}
  
  props.messages.forEach(message => {
    const date = new Date(message.timestamp)
    const dateKey = date.toDateString()
    
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(message)
  })
  
  return groups
})

// 监听消息变化，自动滚动到底部
watch(
  () => props.messages,
  async (newMessages, oldMessages) => {
    if (newMessages.length > (oldMessages?.length || 0)) {
      const container = messagesContainer.value
      if (container && autoScrollEnabled.value && props.autoScroll) {
        await nextTick()
        scrollToBottom(false)
      } else {
        // 如果没有自动滚动，增加未读计数
        unreadCount.value++
      }
    }
  },
  { deep: true }
)

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }
}

// 滚动事件处理
const onScroll = (event: Event) => {
  const container = event.target as HTMLElement
  const { scrollTop, scrollHeight, clientHeight } = container
  
  // 发出滚动事件
  emit('scroll', { scrollTop, scrollHeight, clientHeight })
  
  // 判断是否显示滚动到底部按钮
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
  showScrollToBottom.value = !isNearBottom
  
  // 如果滚动到底部，清除未读计数
  if (isNearBottom) {
    unreadCount.value = 0
    autoScrollEnabled.value = true
  } else if (scrollTop < lastScrollTop.value) {
    // 向上滚动时禁用自动滚动
    autoScrollEnabled.value = false
  }
  
  lastScrollTop.value = scrollTop
}

// 滚动到底部
const scrollToBottom = (smooth = true) => {
  const container = messagesContainer.value
  if (container) {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    })
    unreadCount.value = 0
    autoScrollEnabled.value = true
    showScrollToBottom.value = false
  }
}

// 加载更多历史消息
const loadMoreHistory = () => {
  emit('loadMoreHistory')
}

// 消息点击事件
const onMessageClick = (message: Message) => {
  emit('messageClick', message)
}

// 生命周期
onMounted(() => {
  // 初始滚动到底部
  nextTick(() => {
    scrollToBottom(false)
  })
})

// 导出方法供父组件调用
defineExpose({
  scrollToBottom,
  scrollToTop: () => {
    const container = messagesContainer.value
    if (container) {
      container.scrollTo({ top: 0, behavior: 'smooth' })
    }
  },
  scrollToMessage: (messageId: string) => {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
})
</script>

<style scoped>
.chat-message-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.load-more-container {
  padding: 1rem;
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  max-height: v-bind(maxHeight);
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.3) transparent;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 日期分隔符 */
.date-separator {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  gap: 1rem;
}

.date-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(102, 126, 234, 0.3), transparent);
}

.date-text {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  padding: 0.25rem 0.75rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 1rem;
  white-space: nowrap;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  height: 100%;
  min-height: 200px;
}

.empty-icon {
  font-size: 3rem;
  color: var(--color-text-secondary, #9ca3af);
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 1rem 0;
  animation: fadeInUp 0.3s ease-out;
}

.typing-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
  flex-shrink: 0;
}

.typing-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: rgba(240, 147, 251, 0.1);
  border: 1px solid rgba(240, 147, 251, 0.2);
  border-radius: 1rem;
  border-bottom-left-radius: 0.25rem;
  backdrop-filter: blur(10px);
}

.typing-dots span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #f093fb;
  animation: typingDots 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(1) {
  animation-delay: 0s;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.typing-text {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #6b7280);
  margin-left: 0.5rem;
}

/* 滚动到底部按钮 */
.scroll-to-bottom-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  z-index: 10;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* 深色主题 */
.dark .load-more-container {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.dark .date-line {
  background: linear-gradient(to right, transparent, rgba(102, 126, 234, 0.4), transparent);
}

.dark .date-text {
  color: var(--color-text-secondary, #9ca3af);
  background: rgba(102, 126, 234, 0.2);
}

.dark .empty-state h3 {
  color: var(--color-text-primary, #f9fafb);
}

.dark .empty-state p {
  color: var(--color-text-secondary, #9ca3af);
}

.dark .typing-dots {
  background: rgba(240, 147, 251, 0.15);
  border-color: rgba(240, 147, 251, 0.3);
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

/* 滚动到底部按钮动画 */
.scroll-to-bottom-enter-active,
.scroll-to-bottom-leave-active {
  transition: all 0.3s ease;
}

.scroll-to-bottom-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.scroll-to-bottom-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .messages-container {
    padding: 0.5rem;
  }
  
  .typing-avatar {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
  }
  
  .scroll-to-bottom-btn {
    bottom: 0.5rem;
    right: 0.5rem;
  }
  
  .date-separator {
    margin: 1rem 0;
  }
}
</style> 