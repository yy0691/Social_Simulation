import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiService from '../modules/shared/services/apiService'

export const useGameStore = defineStore('game', () => {
  // 状态数据
  const isLoading = ref(false)
  const currentTab = ref('community')
  const isOnline = ref(true)
  
  // 社群数据
  const communityStats = ref({
    population: 3,
    happiness_level: 75.0,
    activity_level: 85.0
  })
  
  // AI居民数据
  const agents = ref([
    {
      id: 1,
      name: '居民A',
      mood: 80.0,
      status: 'active',
      last_action: '正在准备篝火晚会的零食'
    },
    {
      id: 2,
      name: '居民B', 
      mood: 75.0,
      status: 'active',
      last_action: '在为篝火晚会准备音乐'
    },
    {
      id: 3,
      name: '居民C',
      mood: 70.0,
      status: 'active',
      last_action: '帮助其他居民解决生活中的小问题'
    }
  ])
  
  // 事件历史
  const events = ref([
    {
      id: 1,
      title: '玩家发起了一场篝火晚会',
      description: '玩家输入指令，要求社群居民组织一场温馨的篝火晚会',
      type: 'user_command',
      time: '2分钟前',
      icon: 'fire'
    },
    {
      id: 2,
      title: '社群活跃度提升了10点',
      description: '由于篝火晚会的举办，整个社群的活跃度显著提升',
      type: 'ai_action',
      time: '3分钟前',
      icon: 'star'
    },
    {
      id: 3,
      title: '新成员加入了社群',
      description: '社群的良好氛围吸引了新的居民加入',
      type: 'system_event',
      time: '5分钟前',
      icon: 'users'
    }
  ])
  
  // 聊天消息
  const chatMessages = ref([
    {
      id: 1,
      sender: '居民A',
      content: '太棒了！篝火晚会真是个好主意，我已经开始准备零食了！',
      time: '刚刚',
      type: 'user',
      avatar: 'farmer-a'
    },
    {
      id: 2,
      sender: '居民B',
      content: '我来准备一些音乐吧，让大家一起跳舞！',
      time: '1分钟前',
      type: 'user',
      avatar: 'farmer-b'
    },
    {
      id: 3,
      sender: 'AI助手',
      content: '社群成员们对篝火晚会非常兴奋，活跃度显著提升！',
      time: '2分钟前',
      type: 'ai',
      avatar: 'ai-avatar'
    }
  ])
  
  // 设置数据
  const settings = ref({
    darkMode: false,
    effectsIntensity: 80,
    aiResponseSpeed: 5,
    creativityLevel: 70
  })
  
  // 计算属性
  const onlineAgentsCount = computed(() => {
    return agents.value.filter(agent => agent.status === 'active').length
  })
  
  const averageMood = computed(() => {
    const total = agents.value.reduce((sum, agent) => sum + agent.mood, 0)
    return Math.round(total / agents.value.length)
  })
  
  // 动作方法
  const setCurrentTab = (tab) => {
    currentTab.value = tab
  }
  
  const setLoading = (loading) => {
    isLoading.value = loading
  }
  
  const updateCommunityStats = (stats) => {
    communityStats.value = { ...communityStats.value, ...stats }
  }
  
  const addEvent = (event) => {
    events.value.unshift({
      id: Date.now(),
      time: '刚刚',
      ...event
    })
  }
  
  const addChatMessage = (message) => {
    chatMessages.value.push({
      id: Date.now(),
      time: '刚刚',
      ...message
    })
  }
  
  const updateSettings = (newSettings) => {
    settings.value = { ...settings.value, ...newSettings }
  }
  
  // API调用方法
  const sendCommand = async (command) => {
    try {
      setLoading(true)
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 添加用户指令事件
      addEvent({
        title: `玩家输入指令: ${command}`,
        description: `正在处理玩家的指令: "${command}"`,
        type: 'user_command',
        icon: 'gamepad'
      })
      
      // 模拟AI响应
      setTimeout(() => {
        addEvent({
          title: 'AI正在思考并响应',
          description: 'AI居民们正在根据玩家的指令做出反应...',
          type: 'ai_action',
          icon: 'brain'
        })
      }, 1000)
      
    } catch (error) {
      console.error('发送指令失败:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const sendChatMessage = async (content) => {
    try {
      // 添加用户消息
      addChatMessage({
        sender: '玩家',
        content,
        type: 'user',
        avatar: 'user'
      })
      
      // 模拟AI回复
      setTimeout(() => {
        addChatMessage({
          sender: 'AI助手',
          content: `收到您的消息："${content}"，我会转达给居民们！`,
          type: 'ai',
          avatar: 'ai-avatar'
        })
      }, 1000)
      
    } catch (error) {
      console.error('发送聊天消息失败:', error)
    }
  }
  
  const refreshData = async () => {
    try {
      setLoading(true)
      // 模拟刷新数据
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 可以在这里调用API获取最新数据
      
    } catch (error) {
      console.error('刷新数据失败:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return {
    // 状态
    isLoading,
    currentTab,
    isOnline,
    communityStats,
    agents,
    events,
    chatMessages,
    settings,
    
    // 计算属性
    onlineAgentsCount,
    averageMood,
    
    // 方法
    setCurrentTab,
    setLoading,
    updateCommunityStats,
    addEvent,
    addChatMessage,
    updateSettings,
    sendCommand,
    sendChatMessage,
    refreshData
  }
}) 