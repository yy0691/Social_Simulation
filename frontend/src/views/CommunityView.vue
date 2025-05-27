<template>
  <div class="community-view">
    <!-- 粒子背景 -->
    <ParticleBackground />
    
    <!-- 主要内容区域 -->
    <div class="community-content">
      <!-- 左侧面板 - 社群动态 -->
      <div class="left-panel">
        <!-- 社群动态区域 -->
        <GlassPanel variant="default" glowing class="activity-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-bolt"></i>
              社群动态
            </h3>
            <div class="section-actions">
              <NeonButton 
                size="small" 
                variant="ghost" 
                icon="fas fa-refresh"
                @click="refreshStats"
                :loading="isLoading"
              />
            </div>
          </div>
          
          <div class="activity-feed">
            <div
              v-for="event in recentEvents"
              :key="event.id"
              class="activity-item glow-card"
            >
              <div :class="['activity-icon', getEventTypeClass(event.type)]">
                <i :class="getEventIcon(event.type)"></i>
              </div>
              <div class="activity-content">
                <p class="activity-text">{{ event.description }}</p>
                <span class="activity-time">
                  <i class="fas fa-clock"></i>
                  {{ formatTime(event.timestamp) }}
                </span>
              </div>
              <div class="activity-effect"></div>
            </div>
          </div>
        </GlassPanel>

        <!-- 社群统计面板 -->
        <GlassPanel variant="neon" class="stats-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-chart-line"></i>
              社群状态
            </h3>
          </div>
          
          <div class="stats-grid">
            <div class="stat-card neon-card">
              <div class="stat-icon population">
                <i class="fas fa-users"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats?.population || 0 }}</div>
                <div class="stat-label">社群人口</div>
              </div>
              <div class="stat-glow"></div>
            </div>
            
            <div class="stat-card neon-card">
              <div class="stat-icon energy">
                <i class="fas fa-bolt"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ Math.round(stats?.activity || 0) }}%</div>
                <div class="stat-label">活跃度</div>
              </div>
              <div class="stat-glow"></div>
            </div>
            
            <div class="stat-card neon-card">
              <div class="stat-icon happiness">
                <i class="fas fa-heart"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ Math.round(stats?.happiness || 0) }}%</div>
                <div class="stat-label">幸福指数</div>
              </div>
              <div class="stat-glow"></div>
            </div>
          </div>
        </GlassPanel>
      </div>
      
      <!-- 玩家控制面板 -->
      <GlassPanel variant="default" class="control-panel">
        <div class="section-header">
          <h3 class="section-title">
            <i class="fas fa-gamepad"></i>
            指令控制台
          </h3>
        </div>
        
        <div class="input-container">
          <div class="input-wrapper">
            <GameInput
              v-model="commandInput"
              placeholder="输入你的指令，影响AI社群..."
              :disabled="isLoading"
              clearable
              @enter="executeCommand"
            />
          </div>
          <NeonButton
            variant="primary"
            icon="fas fa-paper-plane"
            :loading="isLoading"
            :disabled="!commandInput.trim()"
            @click="executeCommand"
          >
            发送
          </NeonButton>
        </div>
        
        <!-- 状态指示器 -->
        <div class="status-panel" v-if="isLoading">
          <StatusIndicator
            status="processing"
            :animated="true"
            :pulsing="true"
          >
            AI正在思考中...
          </StatusIndicator>
        </div>
      </GlassPanel>
      
      <!-- 快捷指令面板 -->
      <GlassPanel variant="transparent" class="quick-commands-section">
        <div class="section-header">
          <h3 class="section-title">
            <i class="fas fa-magic"></i>
            快捷指令
          </h3>
        </div>
        
        <div class="quick-commands-grid">
          <NeonButton
            v-for="cmd in quickCommands"
            :key="cmd.command"
            :variant="cmd.type === 'positive' ? 'success' : cmd.type === 'building' ? 'warning' : 'secondary'"
            size="small"
            :icon="cmd.icon"
            @click="commandInput = cmd.command"
            class="quick-cmd-btn"
          >
            {{ cmd.label }}
          </NeonButton>
        </div>
      </GlassPanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useCommunityStore } from '../stores/community';
import { useAppStore } from '../stores/app';
import { GlassPanel, NeonButton, ParticleBackground, GameInput, StatusIndicator } from '../components/ui';

// 状态管理
const communityStore = useCommunityStore();
const appStore = useAppStore();

// 响应式数据
const commandInput = ref('');

// 计算属性
const {
  stats,
  agents,
  events,
  isLoading,
  totalAgents,
  averageMood,
  recentEvents
} = communityStore;

// 快捷指令配置
const quickCommands = [
  { command: '举办聚会', label: '聚会', icon: 'fas fa-party-horn', type: 'positive' },
  { command: '建设公园', label: '建设', icon: 'fas fa-hammer', type: 'building' },
  { command: '组织讨论', label: '讨论', icon: 'fas fa-comments', type: 'neutral' },
  { command: '解决冲突', label: '调解', icon: 'fas fa-handshake', type: 'positive' },
  { command: '举办庆典', label: '庆典', icon: 'fas fa-star', type: 'positive' },
  { command: '改进设施', label: '改进', icon: 'fas fa-tools', type: 'building' }
];

// 方法
const { executeCommand: execCmd, fetchEvents, fetchCommunityStatus } = communityStore;

// 执行指令
const executeCommand = async () => {
  if (!commandInput.value.trim()) return;
  
  try {
    const result = await execCmd({
      command: commandInput.value,
      description: ''
    });
    
    if (result?.success) {
      appStore.addNotification({
        type: 'success',
        title: '指令执行成功',
        message: result.message,
        duration: 3000
      });
      commandInput.value = '';
    } else {
      appStore.addNotification({
        type: 'error',
        title: '指令执行失败',
        message: '请检查指令格式或网络连接',
        duration: 5000
      });
    }
  } catch (error) {
    console.error('执行指令失败:', error);
    appStore.addNotification({
      type: 'error',
      title: '执行错误',
      message: '指令执行过程中发生错误',
      duration: 5000
    });
  }
};

// 刷新统计数据
const refreshStats = async () => {
  await fetchCommunityStatus();
};

// 加载更多事件
const loadMoreEvents = async () => {
  await fetchEvents(20);
};

// 获取心情颜色
const getMoodColor = (mood: number) => {
  if (mood >= 80) return '#10b981'; // 绿色
  if (mood >= 60) return '#f59e0b'; // 黄色
  if (mood >= 40) return '#f97316'; // 橙色
  return '#ef4444'; // 红色
};

// 获取事件图标
const getEventIcon = (type: string) => {
  const icons = {
    positive: 'fas fa-smile',
    negative: 'fas fa-frown',
    neutral: 'fas fa-meh',
    building: 'fas fa-hammer',
    system: 'fas fa-cog'
  };
  return icons[type as keyof typeof icons] || 'fas fa-info-circle';
};

// 获取事件类型样式类
const getEventTypeClass = (type: string) => {
  const typeMap = {
    positive: 'fire',
    building: 'star', 
    neutral: 'users',
    negative: 'warning',
    system: 'cog'
  };
  return typeMap[type as keyof typeof typeMap] || 'info';
};

// 获取影响标签
const getImpactLabel = (key: string) => {
  const labels = {
    happiness: '幸福度',
    activity: '活跃度',
    resources: '资源'
  };
  return labels[key as keyof typeof labels] || key;
};

// 格式化时间
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}小时前`;
  return date.toLocaleDateString('zh-CN');
};

// 组件挂载
onMounted(async () => {
  // 加载初始数据
  await Promise.all([
    communityStore.fetchCommunityStatus(),
    communityStore.fetchAgents(),
    communityStore.fetchEvents()
  ]);
});
</script>

<style scoped>
.community-view {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  min-height: 100vh;
}

.community-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin-top: 20px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 社群动态区域 */
.activity-section {
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: 0.5px;
}

.section-title i {
  font-size: 18px;
  color: #00d4ff;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.activity-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 350px;
  overflow-y: auto;
  padding-right: 8px;
}

.activity-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
}

.activity-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  position: relative;
  flex-shrink: 0;
}

.activity-icon.fire {
  background: linear-gradient(135deg, #ff6b6b, #ff5722);
  color: white;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.4);
}

.activity-icon.star {
  background: linear-gradient(135deg, #ffd700, #ffb347);
  color: white;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
}

.activity-icon.users {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
  box-shadow: 0 0 20px rgba(78, 205, 196, 0.4);
}

.activity-icon.warning {
  background: linear-gradient(135deg, #ff9500, #ff6347);
  color: white;
  box-shadow: 0 0 20px rgba(255, 149, 0, 0.4);
}

.activity-icon.info {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 8px 0;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.5;
  font-weight: 500;
}

.activity-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

.activity-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    45deg,
    rgba(0, 212, 255, 0.1),
    transparent,
    rgba(255, 0, 150, 0.1)
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.activity-item:hover .activity-effect {
  opacity: 1;
}

/* 统计面板 */
.stats-section {
  min-height: 280px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  position: relative;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 12px 48px rgba(0, 212, 255, 0.2);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  position: relative;
  flex-shrink: 0;
}

.stat-icon.population {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 0 24px rgba(102, 126, 234, 0.4);
}

.stat-icon.energy {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  box-shadow: 0 0 24px rgba(240, 147, 251, 0.4);
}

.stat-icon.happiness {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: white;
  box-shadow: 0 0 24px rgba(79, 172, 254, 0.4);
}

.stat-content {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 4px;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.stat-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at center,
    rgba(0, 212, 255, 0.1) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.stat-card:hover .stat-glow {
  opacity: 1;
  animation: stat-pulse 2s ease-in-out infinite;
}

/* 控制面板 */
.control-panel {
  margin-top: 20px;
}

.input-container {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  margin-bottom: 16px;
}

.input-wrapper {
  flex: 1;
}

.status-panel {
  padding: 16px;
  background: rgba(243, 156, 18, 0.1);
  border: 1px solid rgba(243, 156, 18, 0.3);
  border-radius: 12px;
  display: flex;
  justify-content: center;
}

/* 快捷指令面板 */
.quick-commands-section {
  min-height: 160px;
}

.quick-commands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.quick-cmd-btn {
  width: 100%;
  justify-content: flex-start;
  transition: all 0.3s ease;
}

.quick-cmd-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

/* 动画效果 */
@keyframes stat-pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
}

@keyframes glow-rotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .community-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .community-view {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .input-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .activity-item {
    padding: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
}

/* 深色主题优化 */
.dark .activity-item {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.05);
}

.dark .activity-item:hover {
  background: rgba(0, 0, 0, 0.4);
  border-color: rgba(0, 212, 255, 0.3);
}

.dark .stat-card {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.05);
}

.dark .stat-card:hover {
  background: rgba(0, 0, 0, 0.4);
}

/* 滚动条样式 */
.activity-feed::-webkit-scrollbar {
  width: 6px;
}

.activity-feed::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.activity-feed::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.activity-feed::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}
</style> 