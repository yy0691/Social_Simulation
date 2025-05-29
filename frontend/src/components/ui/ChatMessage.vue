<template>
  <div :class="['message-container', messageClass]">
    <!-- 用户头像 -->
    <div class="avatar-container">
      <div :class="['avatar', avatarClass]">
        <i :class="avatarIcon"></i>
      </div>
      <div v-if="isAI" class="ai-glow"></div>
    </div>

    <!-- 消息内容 -->
    <div class="message-content">
      <!-- 发送者信息 -->
      <div class="message-header">
        <span class="sender-name">{{ senderName }}</span>
        <span class="message-time">
          <i class="fas fa-clock"></i>
          {{ formattedTime }}
        </span>
      </div>

      <!-- 消息气泡 -->
      <div :class="['message-bubble', bubbleClass]" @click="onMessageClick">
        <div class="message-text">{{ content }}</div>
        <div v-if="isAI" class="ai-indicator">
          <div class="ai-pulse"></div>
          <span>AI</span>
        </div>
        <div v-if="!isUser" class="bubble-glow"></div>
      </div>

      <!-- 消息状态 -->
      <div v-if="showStatus" class="message-status">
        <i v-if="status === 'sending'" class="fas fa-circle-notch fa-spin status-icon"></i>
        <i v-else-if="status === 'sent'" class="fas fa-check status-icon"></i>
        <i v-else-if="status === 'error'" class="fas fa-exclamation-triangle status-icon error"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  content: string
  sender: string
  timestamp: string | Date
  isUser?: boolean
  isAI?: boolean
  isAgent?: boolean
  status?: 'sending' | 'sent' | 'error'
  showStatus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isUser: false,
  isAI: false,
  isAgent: false,
  status: 'sent',
  showStatus: false
})

const emit = defineEmits<{
  messageClick: []
}>()

// 计算属性
const messageClass = computed(() => ({
  'message-user': props.isUser,
  'message-ai': props.isAI,
  'message-agent': props.isAgent,
  'message-other': !props.isUser && !props.isAI && !props.isAgent
}))

const avatarClass = computed(() => ({
  'avatar-user': props.isUser,
  'avatar-ai': props.isAI,
  'avatar-agent': props.isAgent,
  'avatar-other': !props.isUser && !props.isAI && !props.isAgent
}))

const bubbleClass = computed(() => ({
  'bubble-user': props.isUser,
  'bubble-ai': props.isAI,
  'bubble-agent': props.isAgent,
  'bubble-other': !props.isUser && !props.isAI && !props.isAgent,
  'bubble-sending': props.status === 'sending',
  'bubble-error': props.status === 'error'
}))

const avatarIcon = computed(() => {
  if (props.isUser) return 'fas fa-user'
  if (props.isAI) return 'fas fa-robot'
  if (props.isAgent) return 'fas fa-user-friends'
  return 'fas fa-user-circle'
})

const senderName = computed(() => {
  if (props.isUser) return '你'
  if (props.isAI) return 'AI助手'
  return props.sender
})

const formattedTime = computed(() => {
  const date = typeof props.timestamp === 'string' ? new Date(props.timestamp) : props.timestamp
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

// 事件处理
const onMessageClick = () => {
  emit('messageClick')
}
</script>

<style scoped>
.message-container {
  display: flex;
  margin-bottom: 1.5rem;
  animation: messageSlideIn 0.3s ease-out;
  gap: 0.75rem;
}

.message-user {
  flex-direction: row-reverse;
}

.message-ai .message-content,
.message-other .message-content {
  align-items: flex-start;
}

.message-user .message-content {
  align-items: flex-end;
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
  position: relative;
  overflow: hidden;
}

.avatar-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.avatar-ai {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
}

.avatar-agent {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

.avatar-other {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
}

.ai-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent, #f093fb, transparent, #f5576c, transparent);
  animation: aiGlowRotate 3s linear infinite;
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
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
}

.message-user .message-header {
  justify-content: flex-end;
}

.sender-name {
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
}

.message-time {
  color: var(--color-text-secondary, #6b7280);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 消息气泡 */
.message-bubble {
  position: relative;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  max-width: 100%;
  word-wrap: break-word;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bubble-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 0.25rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.bubble-ai {
  background: rgba(240, 147, 251, 0.1);
  border: 1px solid rgba(240, 147, 251, 0.2);
  color: var(--color-text-primary, #1f2937);
  border-bottom-left-radius: 0.25rem;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.bubble-agent {
  background: rgba(79, 172, 254, 0.1);
  border: 1px solid rgba(79, 172, 254, 0.2);
  color: var(--color-text-primary, #1f2937);
  border-bottom-left-radius: 0.25rem;
  backdrop-filter: blur(10px);
}

.bubble-other {
  background: rgba(79, 172, 254, 0.1);
  border: 1px solid rgba(79, 172, 254, 0.2);
  color: var(--color-text-primary, #1f2937);
  border-bottom-left-radius: 0.25rem;
  backdrop-filter: blur(10px);
}

.bubble-sending {
  opacity: 0.7;
  animation: bubblePulse 1.5s ease-in-out infinite;
}

.bubble-error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.message-bubble:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.bubble-user:hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.message-text {
  line-height: 1.5;
  position: relative;
  z-index: 1;
}

/* AI指示器 */
.ai-indicator {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #f093fb;
  opacity: 0.8;
}

.ai-pulse {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
  background: #f093fb;
  animation: aiPulse 2s ease-in-out infinite;
}

/* 气泡发光效果 */
.bubble-glow {
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: inherit;
  background: linear-gradient(45deg, transparent, rgba(240, 147, 251, 0.3), transparent);
  animation: bubbleGlow 3s ease-in-out infinite;
  z-index: -1;
}

/* 消息状态 */
.message-status {
  margin-top: 0.25rem;
  text-align: right;
}

.message-ai .message-status,
.message-other .message-status {
  text-align: left;
}

.status-icon {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #6b7280);
}

.status-icon.error {
  color: #ef4444;
}

/* 深色主题 */
.dark .sender-name {
  color: var(--color-text-primary, #f9fafb);
}

.dark .message-time {
  color: var(--color-text-secondary, #9ca3af);
}

.dark .bubble-ai {
  background: rgba(240, 147, 251, 0.15);
  color: var(--color-text-primary, #f9fafb);
}

.dark .bubble-agent {
  background: rgba(79, 172, 254, 0.15);
  color: var(--color-text-primary, #f9fafb);
}

.dark .bubble-other {
  background: rgba(79, 172, 254, 0.15);
  color: var(--color-text-primary, #f9fafb);
}

.dark .bubble-error {
  background: rgba(239, 68, 68, 0.15);
}

/* 动画 */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes aiGlowRotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes aiPulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes bubbleGlow {
  0%, 100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

@keyframes bubblePulse {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 0.9;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .avatar {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
  }
  
  .message-bubble {
    padding: 0.6rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style> 