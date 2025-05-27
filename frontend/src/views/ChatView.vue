<template>
  <div class="chat-view">
    <!-- 粒子背景 -->
    <ParticleBackground />
    
    <!-- 主要内容区域 -->
    <div class="chat-content">
      <!-- 聊天头部 -->
      <GlassPanel variant="default" class="chat-header">
        <div class="header-content">
          <div class="chat-info">
            <div class="chat-avatar">
              <i class="fas fa-comments"></i>
            </div>
            <div class="chat-details">
              <h2 class="chat-title">AI社群聊天室</h2>
              <p class="chat-subtitle">
                <StatusIndicator
                  :status="connectionStatus"
                  :animated="true"
                >
                  {{ connectionText }}
                </StatusIndicator>
              </p>
            </div>
          </div>
          
          <div class="header-actions">
            <NeonButton
              variant="ghost"
              size="small"
              icon="fas fa-history"
              @click="toggleHistory"
              title="聊天历史"
            />
            <NeonButton
              variant="ghost"
              size="small"
              icon="fas fa-cog"
              @click="toggleSettings"
              title="聊天设置"
            />
          </div>
        </div>
      </GlassPanel>

      <!-- 聊天主体 -->
      <div class="chat-body">
        <!-- 侧边栏 - 聊天历史或设置 -->
        <Transition name="sidebar">
          <div v-if="showSidebar" class="chat-sidebar">
            <GlassPanel variant="transparent" class="sidebar-panel">
              <!-- 历史记录 -->
              <div v-if="sidebarMode === 'history'" class="sidebar-content">
                <div class="sidebar-header">
                  <h3><i class="fas fa-history"></i> 聊天历史</h3>
                  <button @click="closeSidebar" class="close-btn">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div class="history-list">
                  <div
                    v-for="session in chatSessions"
                    :key="session.id"
                    class="history-item"
                    @click="loadChatSession(session.id)"
                  >
                    <div class="history-info">
                      <span class="history-title">{{ session.title }}</span>
                      <span class="history-time">{{ formatTime(session.lastMessage) }}</span>
                    </div>
                    <span class="history-count">{{ session.messageCount }} 条消息</span>
                  </div>
                </div>
              </div>

              <!-- 设置面板 -->
              <div v-else-if="sidebarMode === 'settings'" class="sidebar-content">
                <div class="sidebar-header">
                  <h3><i class="fas fa-cog"></i> 聊天设置</h3>
                  <button @click="closeSidebar" class="close-btn">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div class="settings-list">
                  <div class="setting-item">
                    <label>自动滚动到新消息</label>
                    <input v-model="chatSettings.autoScroll" type="checkbox" />
                  </div>
                  <div class="setting-item">
                    <label>显示发送状态</label>
                    <input v-model="chatSettings.showStatus" type="checkbox" />
                  </div>
                  <div class="setting-item">
                    <label>消息通知</label>
                    <input v-model="chatSettings.notifications" type="checkbox" />
                  </div>
                </div>
              </div>
            </GlassPanel>
          </div>
        </Transition>

        <!-- 消息区域 -->
        <div class="messages-area">
          <GlassPanel variant="default" class="messages-panel">
            <ChatMessageList
              ref="messageListRef"
              :messages="messages"
              :has-more-history="hasMoreHistory"
              :loading-history="loadingHistory"
              :show-typing-indicator="isAITyping"
              :auto-scroll="chatSettings.autoScroll"
              max-height="500px"
              @load-more-history="loadMoreHistory"
              @message-click="onMessageClick"
            />
          </GlassPanel>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <GlassPanel variant="neon" class="input-panel">
          <ChatInput
            :disabled="!isConnected || isAITyping"
            :sending="isSending"
            placeholder="与AI居民对话..."
            :show-char-count="true"
            :show-file-upload="false"
            hint="按 Ctrl+Enter 快速发送消息"
            @send="sendMessage"
            @typing="onUserTyping"
            @stop-typing="onUserStopTyping"
          />
        </GlassPanel>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { 
  ParticleBackground, 
  GlassPanel, 
  NeonButton, 
  StatusIndicator,
  ChatMessageList,
  ChatInput
} from '../components/ui'

// 消息接口
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

// 聊天会话接口
interface ChatSession {
  id: string
  title: string
  lastMessage: Date
  messageCount: number
}

// 响应式数据
const messages = ref<Message[]>([])
const isConnected = ref(true)
const isAITyping = ref(false)
const isSending = ref(false)
const hasMoreHistory = ref(false)
const loadingHistory = ref(false)
const showSidebar = ref(false)
const sidebarMode = ref<'history' | 'settings'>('history')

// 聊天设置
const chatSettings = reactive({
  autoScroll: true,
  showStatus: true,
  notifications: true
})

// 聊天会话历史
const chatSessions = ref<ChatSession[]>([
  {
    id: '1',
    title: '今天的对话',
    lastMessage: new Date(),
    messageCount: 5
  },
  {
    id: '2',
    title: '昨天的讨论',
    lastMessage: new Date(Date.now() - 24 * 60 * 60 * 1000),
    messageCount: 12
  }
])

// 组件引用
const messageListRef = ref()

// 计算属性
const connectionStatus = computed(() => {
  if (!isConnected.value) return 'offline'
  if (isAITyping.value) return 'processing'
  return 'online'
})

const connectionText = computed(() => {
  if (!isConnected.value) return '连接断开'
  if (isAITyping.value) return 'AI正在思考...'
  return '在线'
})

// 方法
const sendMessage = async (content: string) => {
  if (!content.trim() || isSending.value) return

  // 添加用户消息
  const userMessage: Message = {
    id: `user-${Date.now()}`,
    content,
    sender: '用户',
    timestamp: new Date(),
    isUser: true,
    status: 'sent',
    showStatus: chatSettings.showStatus
  }
  
  messages.value.push(userMessage)
  
  // 开始发送状态
  isSending.value = true
  
  try {
    // 模拟AI思考时间
    isAITyping.value = true
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    // 添加AI回复
    const aiMessage: Message = {
      id: `ai-${Date.now()}`,
      content: generateAIResponse(content),
      sender: 'AI助手',
      timestamp: new Date(),
      isAI: true,
      status: 'sent',
      showStatus: chatSettings.showStatus
    }
    
    messages.value.push(aiMessage)
    
  } catch (error) {
    console.error('发送消息失败:', error)
    // 更新用户消息状态为错误
    userMessage.status = 'error'
  } finally {
    isSending.value = false
    isAITyping.value = false
  }
}

const generateAIResponse = (userInput: string): string => {
  const responses = [
    `很有趣的想法！关于"${userInput}"，我觉得这会对社群产生积极的影响。`,
    `我理解你的观点。在AI社群中，${userInput}确实是一个值得深入讨论的话题。`,
    `感谢你的分享！这让我想到了社群中其他居民的想法。`,
    `这是个不错的建议！我会将"${userInput}"记录下来，并与其他AI居民讨论。`,
    `很好的问题！让我们一起探索这个话题在虚拟社群中的可能性。`
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const onUserTyping = () => {
  // 用户开始输入的处理
}

const onUserStopTyping = () => {
  // 用户停止输入的处理
}

const onMessageClick = (message: Message) => {
  console.log('点击消息:', message)
}

const loadMoreHistory = () => {
  loadingHistory.value = true
  // 模拟加载历史消息
  setTimeout(() => {
    const historyMessages: Message[] = [
      {
        id: `history-${Date.now()}`,
        content: '这是一条历史消息',
        sender: 'AI助手',
        timestamp: new Date(Date.now() - 60 * 60 * 1000),
        isAI: true
      }
    ]
    messages.value.unshift(...historyMessages)
    loadingHistory.value = false
  }, 1000)
}

const toggleHistory = () => {
  sidebarMode.value = 'history'
  showSidebar.value = !showSidebar.value
}

const toggleSettings = () => {
  sidebarMode.value = 'settings'
  showSidebar.value = !showSidebar.value
}

const closeSidebar = () => {
  showSidebar.value = false
}

const loadChatSession = (sessionId: string) => {
  console.log('加载聊天会话:', sessionId)
  // 实现会话加载逻辑
  closeSidebar()
}

const formatTime = (date: Date): string => {
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  // 添加一些初始消息
  messages.value = [
    {
      id: 'welcome',
      content: '欢迎来到AI社群聊天室！我是你的AI助手，有什么问题都可以问我。',
      sender: 'AI助手',
      timestamp: new Date(),
      isAI: true
    }
  ]
})
</script>

<style scoped>
.chat-view {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.chat-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  gap: 1rem;
}

/* 聊天头部 */
.chat-header {
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chat-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.chat-details h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.chat-details p {
  margin: 0;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* 聊天主体 */
.chat-body {
  display: flex;
  flex: 1;
  gap: 1rem;
  min-height: 0;
}

.chat-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-panel {
  height: 100%;
}

.sidebar-content {
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--color-text-primary, #1f2937);
}

/* 历史记录 */
.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-item {
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.5rem;
  border: 1px solid transparent;
}

.history-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.history-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.history-title {
  font-weight: 500;
  color: var(--color-text-primary, #1f2937);
}

.history-time {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #6b7280);
}

.history-count {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #6b7280);
}

/* 设置面板 */
.settings-list {
  flex: 1;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item label {
  font-weight: 500;
  color: var(--color-text-primary, #1f2937);
}

.setting-item input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  min-width: 0;
}

.messages-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 输入区域 */
.chat-input-area {
  flex-shrink: 0;
}

.input-panel {
  padding: 1rem;
}

/* 侧边栏动画 */
.sidebar-enter-active,
.sidebar-leave-active {
  transition: all 0.3s ease;
}

.sidebar-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.sidebar-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* 深色主题 */
.dark .sidebar-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.dark .close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-primary, #f9fafb);
}

.dark .setting-item {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-content {
    padding: 0.5rem;
  }
  
  .chat-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: auto;
    z-index: 100;
  }
  
  .header-content {
    padding: 0.75rem;
  }
  
  .chat-avatar {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.2rem;
  }
  
  .chat-details h2 {
    font-size: 1.2rem;
  }
}
</style> 