<template>
  <div class="chat-view">

    <!-- 聊天消息区域 -->
    <div class="chat-messages-container">
      <div class="messages-list" ref="messagesContainer">
        <!-- 消息列表 -->
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message-item', {
            'message-user': message.isUser,
            'message-ai': message.isAI,
            'message-agent': message.isAgent,
            'message-streaming': message.status === 'sending'
          }]"
        >
          <!-- 用户头像 -->
          <div class="message-avatar">
            <div :class="['avatar', getAvatarClass(message)]">
              <i :class="getAvatarIcon(message)"></i>
            </div>
          </div>

          <!-- 消息内容 -->
          <div class="message-content">
            <!-- 用户名和时间 -->
            <div class="message-header">
              <span class="message-sender">{{ message.sender }}</span>
              <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
            </div>
            
            <!-- 消息文本 -->
            <div class="message-text">
              {{ message.content }}
              <div v-if="message.status === 'sending'" class="streaming-indicator">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
        <div v-if="agentTypingStatus.isTyping" class="typing-indicator">
          <div class="typing-content">
            <div class="typing-avatar">
              <i class="fas fa-robot"></i>
            </div>
            <div class="typing-text">
              <span>{{ agentTypingStatus.agents.join('、') }} 正在输入...</span>
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <ChatInput
        :disabled="!isConnected || isAITyping"
        :sending="isSending"
        placeholder="输入消息..."
        :show-char-count="false"
        :show-file-upload="false"
        @send="sendMessage"
        @typing="onUserTyping"
        @stop-typing="onUserStopTyping"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ChatInput } from '../components/ui'

// 消息接口
interface Message {
  id: string
  content: string
  sender: string
  timestamp: string | Date
  isUser?: boolean
  isAI?: boolean
  isAgent?: boolean
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
const loadingHistory = ref(false)
const showSidebar = ref(false)
const sidebarMode = ref<'history' | 'settings'>('history')

// 新增：AI居民回复状态
const agentTypingStatus = ref<{
  isTyping: boolean
  agents: string[]
  expectedReplies: number
  receivedReplies: number
}>({
  isTyping: false,
  agents: [],
  expectedReplies: 0,
  receivedReplies: 0
})

// 新增：正在生成回复的居民状态
const activeAgentGenerations = ref<Set<string>>(new Set())

// 聊天设置
const chatSettings = reactive({
  autoScroll: true,
  showStatus: true,
  notifications: true
})

// 新增：消息容器引用
const messagesContainer = ref()

// 新增方法：获取头像类名
const getAvatarClass = (message: Message): string => {
  if (message.isUser) return 'avatar-user'
  if (message.isAI) return 'avatar-ai'
  if (message.isAgent) return 'avatar-agent'
  return 'avatar-default'
}

// 新增方法：获取头像图标
const getAvatarIcon = (message: Message): string => {
  if (message.isUser) return 'fas fa-user'
  if (message.isAI) return 'fas fa-robot'
  if (message.isAgent) return 'fas fa-user-friends'
  return 'fas fa-user'
}

// 新增方法：格式化消息时间
const formatMessageTime = (timestamp: string | Date): string => {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 小于1分钟显示"刚刚"
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于1小时显示分钟
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }
  
  // 同一天显示时间
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
  
  // 不同天显示日期和时间
  return date.toLocaleString('zh-CN', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 方法
const sendMessage = async (content: string) => {
  if (!content.trim() || isSending.value) return

  isSending.value = true
  
  try {
    console.log('📤 发送消息:', content)
    
    // 发送消息到后端API
    const response = await fetch('http://127.0.0.1:8000/api/v1/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: content })
    })
    
    const data = await response.json()
    
    if (data.success) {
      console.log('✅ 消息发送成功')
      
      // 立即刷新消息列表以显示新消息
      await loadChatMessages()
      
      // 启动AI居民状态监控（更频繁）
      startAgentStatusMonitoring()
      
      // 启动密集刷新策略，确保及时获取居民回复
      startIntensiveRefresh()
      
    } else {
      console.error('❌ 发送消息失败:', data.error)
      alert('发送消息失败: ' + (data.error || '未知错误'))
    }
    
  } catch (error) {
    console.error('❌ 发送消息失败:', error)
    alert('发送消息失败: ' + (error as Error).message)
  } finally {
    isSending.value = false
  }
}

const onUserTyping = () => {
  // 用户开始输入的处理
}

const onUserStopTyping = () => {
  // 用户停止输入的处理
}

const closeSidebar = () => {
  showSidebar.value = false
}

// 生命周期
onMounted(async () => {
  // 加载真实的聊天消息
  await loadChatMessages()
  
  // 启动正常刷新策略
  startNormalRefresh()
  
  console.log('💬 聊天室已加载，开始监听新消息')
})

onUnmounted(() => {
  // 清理定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (intensiveRefreshTimeout) {
    clearTimeout(intensiveRefreshTimeout)
  }
  if (agentMonitoringTimeout) {
    clearTimeout(agentMonitoringTimeout)
  }
  if (statusMonitoringInterval) {
    clearInterval(statusMonitoringInterval)
  }
  
  // 清理所有EventSource连接
  for (const [agentName, eventSource] of activeEventSources.entries()) {
    console.log(`🧹 清理 ${agentName} 的EventSource连接`)
    eventSource.close()
  }
  activeEventSources.clear()
  streamingAgents.clear()
})

// 新增方法：加载聊天消息
const loadChatMessages = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/chat/messages?limit=50')
    const data = await response.json()
    
    if (data.success) {
      // 处理API响应数据格式
      const apiMessages = data.data.messages || data.data || []
      
      // 转换为前端消息格式
      const newMessages = apiMessages.map((msg: any) => ({
        id: msg.id.toString(),
        content: msg.content,
        sender: msg.sender_name || msg.sender || '未知',
        timestamp: new Date(msg.timestamp),
        isUser: msg.sender_type === 'user',
        isAI: msg.sender_type === 'ai',
        isAgent: msg.sender_type === 'agent',
        status: 'sent',
        showStatus: chatSettings.showStatus
      }))
      
      // 保护正在流式传输的消息
      const streamingMessages = messages.value.filter(msg => 
        msg.status === 'sending' && msg.id.startsWith('streaming-')
      )
      
      // 清理已完成的流式消息（避免重复）
      const activeStreamingMessages = streamingMessages.filter(msg => {
        const agentName = msg.sender
        return streamingAgents.has(agentName)
      })
      
      if (activeStreamingMessages.length > 0) {
        console.log(`🛡️ 保护 ${activeStreamingMessages.length} 条流式消息:`, 
          activeStreamingMessages.map(m => ({ id: m.id, sender: m.sender, content: m.content.substring(0, 20) + '...' })))
      }
      
      // 检查是否有新消息（比较最新消息的ID）
      const oldLatestId = messages.value.length > 0 ? 
        messages.value.filter(msg => !msg.id.startsWith('streaming-'))[messages.value.filter(msg => !msg.id.startsWith('streaming-')).length - 1]?.id : null
      const newLatestId = newMessages.length > 0 ? newMessages[newMessages.length - 1].id : null
      
      // 如果有新消息或者消息数量变化，则更新
      if (newLatestId !== oldLatestId || newMessages.length !== messages.value.filter(msg => !msg.id.startsWith('streaming-')).length) {
        const oldCount = messages.value.filter(msg => !msg.id.startsWith('streaming-')).length
        const oldAgentCount = messages.value.filter(msg => msg.isAgent && !msg.id.startsWith('streaming-')).length
        
        // 合并数据库消息和流式消息
        const combinedMessages = [...newMessages, ...activeStreamingMessages].sort((a, b) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        )
        
        messages.value = combinedMessages
        
        // 如果消息数量增加，说明有新消息
        if (newMessages.length > oldCount) {
          const newCount = newMessages.length - oldCount
          console.log(`📬 收到 ${newCount} 条新消息`)
          
          // 检查是否有新的居民消息，并更新状态
          const newAgentCount = newMessages.filter((msg: Message) => msg.isAgent).length
          const newAgentMessages = newAgentCount - oldAgentCount
          
          if (newAgentMessages > 0 && agentTypingStatus.value.isTyping) {
            // 更新收到的回复数
            agentTypingStatus.value.receivedReplies += newAgentMessages
            
            // 获取新回复的居民名字
            const recentAgentMessages = newMessages
              .filter((msg: Message) => msg.isAgent)
              .slice(-newAgentMessages)
              .map((msg: Message) => msg.sender)
            
            console.log(`🎭 收到 ${newAgentMessages} 条居民回复:`, recentAgentMessages.join(', '))
            
            // 如果收到足够的回复，可以提前结束监控
            if (agentTypingStatus.value.receivedReplies >= agentTypingStatus.value.expectedReplies) {
              agentTypingStatus.value.isTyping = false
              if (agentMonitoringTimeout) {
                clearTimeout(agentMonitoringTimeout)
                agentMonitoringTimeout = null
              }
              console.log('✅ 已收到预期的AI居民回复，结束监控')
            }
            
            // 播放通知音效（如果启用）
            if (chatSettings.notifications) {
              playNotificationSound()
            }
          }
        }
      }
    } else {
      console.error('获取消息失败:', data.error || '未知错误')
    }
  } catch (error) {
    console.error('加载聊天消息失败:', error)
  }
}

// 新增：播放通知音效
const playNotificationSound = () => {
  try {
    // 创建一个简单的提示音
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
    
    gainNode.gain.setValueAtTime(0, audioContext.currentTime)
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.05)
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.2)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.2)
  } catch (error) {
    console.log('无法播放通知音效:', error)
  }
}

// 智能刷新策略
let refreshInterval: number | null = null
let intensiveRefreshTimeout: number | null = null
let agentMonitoringTimeout: number | null = null

const startIntensiveRefresh = () => {
  // 清除之前的定时器
  if (intensiveRefreshTimeout) {
    clearTimeout(intensiveRefreshTimeout)
  }
  
  console.log('🚀 启动超密集刷新模式 (每0.2秒刷新)')
  
  // 发送消息后的15秒内，每0.2秒刷新一次
  const intensiveRefresh = setInterval(async () => {
    await loadChatMessages()
  }, 200) // 从500ms改为200ms，极速刷新
  
  intensiveRefreshTimeout = setTimeout(() => {
    clearInterval(intensiveRefresh)
    intensiveRefreshTimeout = null
    console.log('🔄 切换到正常刷新频率')
  }, 15000) // 从20秒缩短到15秒
}

const startNormalRefresh = () => {
  // 清除之前的定时器
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  
  console.log('⏰ 启动正常刷新模式 (每1秒刷新)')
  
  // 正常情况下每1秒刷新一次（从3秒改为1秒）
  refreshInterval = setInterval(async () => {
    await loadChatMessages()
  }, 1000)
}

// 新增：监控AI居民回复状态
const monitorAgentStatus = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/chat/agent-status')
    const data = await response.json()
    
    if (data.success) {
      const generations = data.data.active_generations || {}
      
      // 更新正在生成的居民列表
      const currentGenerating = new Set<string>()
      
      for (const [agentName, genInfo] of Object.entries(generations)) {
        const info = genInfo as any
        
        switch (info.status) {
          case 'generating':
            currentGenerating.add(agentName)
            console.log(`🎭 ${agentName} 正在生成回复...`)
            // generating状态时只记录，不启动流式传输
            break
            
          case 'streaming':
            currentGenerating.add(agentName)
            console.log(`📡 ${agentName} 流式传输中，进度: ${info.progress || 0}`)
            // 只在streaming状态时启动流式传输
            if (!streamingAgents.has(agentName)) {
              startStreamingForAgent(agentName)
              streamingAgents.add(agentName)
            }
            break
            
          case 'completed':
            console.log(`✅ ${agentName} 回复完成`)
            streamingAgents.delete(agentName)
            break
            
          case 'error':
            console.log(`❌ ${agentName} 生成出错`)
            streamingAgents.delete(agentName)
            break
        }
      }
      
      activeAgentGenerations.value = currentGenerating
      
      // 更新UI状态
      if (currentGenerating.size > 0) {
        agentTypingStatus.value = {
          isTyping: true,
          agents: Array.from(currentGenerating),
          expectedReplies: currentGenerating.size,
          receivedReplies: 0
        }
      } else if (agentTypingStatus.value.isTyping && streamingAgents.size === 0) {
        agentTypingStatus.value.isTyping = false
      }
    }
  } catch (error) {
    console.error('监控AI居民状态失败:', error)
  }
}

// 跟踪已启动流式传输的居民
const streamingAgents = new Set<string>()
// 跟踪活跃的EventSource连接
const activeEventSources = new Map<string, EventSource>()

// 为特定居民启动流式传输
const startStreamingForAgent = (agentName: string) => {
  console.log(`🚀 为 ${agentName} 启动流式消息显示`)
  
  // 如果已经有活跃的EventSource连接，直接返回
  if (activeEventSources.has(agentName)) {
    console.log(`ℹ️ ${agentName} 已有活跃的EventSource连接，跳过`)
    return
  }
  
  // 检查是否已经有对应的流式消息
  const existingStreamingMessage = messages.value.find(
    msg => msg.sender === agentName && msg.status === 'sending' && msg.id.startsWith('streaming-')
  )
  
  if (existingStreamingMessage) {
    console.log(`ℹ️ ${agentName} 已有流式消息，直接使用:`, existingStreamingMessage.id)
    startStreamingContent(agentName, existingStreamingMessage.id)
    return
  }
  
  // 直接在消息列表中添加一个临时的流式消息
  const streamingMessage: Message = {
    id: `streaming-${agentName}-${Date.now()}`,
    content: '',  // 内容将通过流式API逐步更新
    sender: agentName,
    timestamp: new Date(),
    isAgent: true,
    status: 'sending',
    showStatus: true
  }
  
  console.log(`🆕 为 ${agentName} 创建新的流式消息:`, streamingMessage.id)
  
  // 添加到消息列表
  messages.value.push(streamingMessage)
  
  // 确保DOM更新后再启动流式内容获取
  setTimeout(() => {
    startStreamingContent(agentName, streamingMessage.id)
  }, 50)
}

// 获取流式内容并实时更新消息
const startStreamingContent = async (agentName: string, messageId: string) => {
  try {
    // 如果已经有连接，先关闭
    if (activeEventSources.has(agentName)) {
      const oldEventSource = activeEventSources.get(agentName)
      oldEventSource?.close()
      activeEventSources.delete(agentName)
      console.log(`🔄 关闭 ${agentName} 的旧EventSource连接`)
    }
    
    const streamUrl = `http://localhost:8000/api/v1/chat/stream/${encodeURIComponent(agentName)}`
    console.log(`🎬 启动 ${agentName} 的流式连接:`, streamUrl, `消息ID: ${messageId}`)
    
    const eventSource = new EventSource(streamUrl)
    let hasConnected = false
    
    // 记录活跃连接
    activeEventSources.set(agentName, eventSource)
    
    eventSource.onopen = () => {
      hasConnected = true
      console.log(`✅ ${agentName} 流式连接已建立`)
    }
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // 找到对应的消息并更新内容
        const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
        if (messageIndex === -1) {
          console.warn(`⚠️ 找不到消息ID: ${messageId}，当前消息列表:`, messages.value.map(m => ({ id: m.id, sender: m.sender, status: m.status })))
          return
        }
        
        switch (data.type) {
          case 'content':
            // 逐字符添加内容
            messages.value[messageIndex].content += data.char
            break
            
          case 'complete':
            // 完成流式传输
            messages.value[messageIndex].status = 'sent'
            console.log(`✅ ${agentName} 流式传输完成`)
            eventSource.close()
            activeEventSources.delete(agentName)
            streamingAgents.delete(agentName)
            
            // 标记该消息为完成状态，等待下次刷新时被数据库消息替换
            messages.value[messageIndex].id = `completed-${agentName}-${Date.now()}`
            
            // 立即刷新一次，获取数据库中的最终消息
            setTimeout(() => {
              loadChatMessages()
            }, 1000)
            break
            
          case 'waiting':
            console.log(`⏳ ${agentName} 等待开始生成...`)
            break
            
          case 'timeout':
            console.log(`⏰ ${agentName} 流式传输超时`)
            messages.value[messageIndex].status = 'error'
            messages.value[messageIndex].content = '回复超时，请重试'
            eventSource.close()
            activeEventSources.delete(agentName)
            streamingAgents.delete(agentName)
            break
            
          case 'error':
            console.log(`❌ ${agentName} 流式传输出错`)
            messages.value[messageIndex].status = 'error'
            messages.value[messageIndex].content = '回复出错，请重试'
            eventSource.close()
            activeEventSources.delete(agentName)
            streamingAgents.delete(agentName)
            break
        }
      } catch (error) {
        console.error(`❌ ${agentName} 解析流式数据失败:`, error)
      }
    }

    eventSource.onerror = (error) => {
      console.error(`❌ ${agentName} 流式连接错误:`, error)
      
      if (!hasConnected) {
        // 如果从未连接成功，可能是URL或服务器问题
        console.error(`❌ ${agentName} 从未连接成功，可能是服务器问题`)
        const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
        if (messageIndex !== -1) {
          messages.value[messageIndex].status = 'error'
          messages.value[messageIndex].content = '连接失败，将通过轮询获取回复'
        }
      }
      
      activeEventSources.delete(agentName)
      streamingAgents.delete(agentName)
      setTimeout(() => eventSource.close(), 1000)
    }

  } catch (error) {
    console.error(`❌ 启动 ${agentName} 流式传输失败:`, error)
    activeEventSources.delete(agentName)
    streamingAgents.delete(agentName)
  }
}

// 启动AI居民状态监控
let statusMonitoringInterval: number | null = null

const startAgentStatusMonitoring = () => {
  // 清除之前的监控
  if (statusMonitoringInterval) {
    clearInterval(statusMonitoringInterval)
  }
  
  console.log('🎬 启动AI居民超频监控')
  
  // 立即执行一次
  monitorAgentStatus()
  
  // 每0.3秒监控一次状态（稍微放慢一点，减少服务器压力）
  statusMonitoringInterval = setInterval(async () => {
    await monitorAgentStatus()
  }, 300)
  
  // 60秒后停止密集监控（给足够时间让AI生成完成）
  setTimeout(() => {
    if (statusMonitoringInterval) {
      clearInterval(statusMonitoringInterval)
      statusMonitoringInterval = null
      console.log('⏰ AI居民状态监控结束')
    }
  }, 60000)  // 从15秒延长到60秒
}
</script>

<style scoped>
.chat-view {
  background: linear-gradient(135deg, #1a1c2e 0%, #2d3748 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: #e2e8f0;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* 顶部导航栏 */
.top-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-buttons {
  display: flex;
  gap: 0.5rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 2rem;
  color: #cbd5e0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.nav-btn.active {
  background: linear-gradient(135deg, #3182ce 0%, #63b3ed 100%);
  color: white;
  border-color: #3182ce;
  box-shadow: 0 4px 15px rgba(49, 130, 206, 0.3);
}

.online-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #68d391;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #68d391;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 聊天头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f7fafc;
}

.chat-title i {
  color: #63b3ed;
}

.online-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #a0aec0;
}

/* 消息区域 */
.chat-messages-container {
  flex: 1;
  overflow: hidden;
  padding: 1rem 2rem;
}

.messages-list {
  height: 100%;
  overflow-y: auto;
  scroll-behavior: smooth;
  padding-right: 0.5rem;
}

.messages-list::-webkit-scrollbar {
  width: 6px;
}

.messages-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.messages-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.messages-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  animation: messageSlideIn 0.3s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.avatar-user {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
}

.avatar-ai {
  background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
}

.avatar-agent {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.avatar-default {
  background: linear-gradient(135deg, #718096 0%, #4a5568 100%);
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
}

.message-user .message-content {
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.15) 0%, rgba(49, 130, 206, 0.1) 100%);
  border-color: rgba(66, 153, 225, 0.3);
}

.message-ai .message-content {
  background: linear-gradient(135deg, rgba(159, 122, 234, 0.15) 0%, rgba(128, 90, 213, 0.1) 100%);
  border-color: rgba(159, 122, 234, 0.3);
}

.message-agent .message-content {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.15) 0%, rgba(56, 161, 105, 0.1) 100%);
  border-color: rgba(72, 187, 120, 0.3);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-sender {
  font-weight: 600;
  font-size: 0.9rem;
  color: #f7fafc;
}

.message-time {
  font-size: 0.8rem;
  color: #a0aec0;
}

.message-text {
  color: #e2e8f0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.message-streaming .message-content {
  border-color: rgba(99, 179, 237, 0.5);
  animation: streamingPulse 1.5s ease-in-out infinite;
}

@keyframes streamingPulse {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(99, 179, 237, 0.4);
  }
  50% { 
    box-shadow: 0 0 0 8px rgba(99, 179, 237, 0);
  }
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  opacity: 0.8;
}

.typing-content {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.typing-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
}

.typing-text {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e0;
  font-size: 0.9rem;
}

.typing-dots {
  display: inline-flex;
  gap: 0.25rem;
  margin-left: 0.5rem;
}

.typing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #a0aec0;
  animation: typingDot 1.4s infinite;
}

.typing-dots span:nth-child(1) { animation-delay: 0ms; }
.typing-dots span:nth-child(2) { animation-delay: 200ms; }
.typing-dots span:nth-child(3) { animation-delay: 400ms; }

@keyframes typingDot {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.streaming-indicator {
  margin-top: 0.5rem;
  opacity: 0.7;
}

/* 输入区域 */
.chat-input-area {
  padding: 1.5rem 2rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .top-navigation {
    padding: 0.75rem 1rem;
  }
  
  .nav-btn {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .nav-btn span {
    display: none;
  }
  
  .chat-header {
    padding: 1rem;
  }
  
  .chat-messages-container {
    padding: 0.75rem 1rem;
  }
  
  .message-item {
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }
  
  .message-content {
    padding: 0.75rem 1rem;
  }
  
  .chat-input-area {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .top-navigation {
    padding: 0.5rem;
  }
  
  .chat-header {
    padding: 0.75rem;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .chat-messages-container {
    padding: 0.5rem;
  }
  
  .message-item {
    gap: 0.5rem;
  }
  
  .avatar {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
}
</style> 