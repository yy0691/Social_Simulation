<template>
  <div class="community-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <i class="fas fa-users"></i>
        社群中心
      </h2>
      <p>观察AI社群的实时状态和动态</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="community-content">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <!-- 社群统计卡片 -->
        <div class="stats-card glass-panel">
          <div class="card-header">
            <h3>
              <i class="fas fa-chart-line"></i>
              社群统计
            </h3>
            <button @click="refreshStats" class="refresh-btn" :disabled="isLoading">
              <i :class="['fas fa-sync-alt', { 'spinning': isLoading }]"></i>
            </button>
          </div>
          
          <div v-if="stats" class="stats-content">
            <div class="stat-item">
              <div class="stat-icon population">
                <i class="fas fa-users"></i>
              </div>
              <div class="stat-info">
                <span class="stat-label">人口数量</span>
                <span class="stat-value">{{ stats.population }}</span>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon happiness">
                <i class="fas fa-heart"></i>
              </div>
              <div class="stat-info">
                <span class="stat-label">幸福指数</span>
                <span class="stat-value">{{ Math.round(stats.happiness) }}%</span>
                <div class="stat-bar">
                  <div class="stat-fill happiness" :style="{ width: stats.happiness + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon activity">
                <i class="fas fa-bolt"></i>
              </div>
              <div class="stat-info">
                <span class="stat-label">活跃度</span>
                <span class="stat-value">{{ Math.round(stats.activity) }}%</span>
                <div class="stat-bar">
                  <div class="stat-fill activity" :style="{ width: stats.activity + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon resources">
                <i class="fas fa-coins"></i>
              </div>
              <div class="stat-info">
                <span class="stat-label">资源量</span>
                <span class="stat-value">{{ Math.round(stats.resources) }}%</span>
                <div class="stat-bar">
                  <div class="stat-fill resources" :style="{ width: stats.resources + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="loading-state">
            <i class="fas fa-spinner fa-spin"></i>
            <p>加载统计数据中...</p>
          </div>
        </div>

        <!-- 指令控制台 -->
        <div class="command-panel glass-panel">
          <div class="card-header">
            <h3>
              <i class="fas fa-terminal"></i>
              指令控制台
            </h3>
          </div>
          
          <div class="command-form">
            <div class="input-group">
              <input
                v-model="commandInput"
                @keyup.enter="executeCommand"
                type="text"
                placeholder="输入指令（如：举办聚会、建设公园、讨论问题...）"
                class="command-input"
                :disabled="isLoading"
              />
              <button
                @click="executeCommand"
                :disabled="!commandInput.trim() || isLoading"
                class="execute-btn"
              >
                <i class="fas fa-play"></i>
                执行
              </button>
            </div>
            
            <!-- 快捷指令 -->
            <div class="quick-commands">
              <h4>快捷指令</h4>
              <div class="command-buttons">
                <button
                  v-for="cmd in quickCommands"
                  :key="cmd.command"
                  @click="commandInput = cmd.command"
                  :class="['quick-cmd-btn', cmd.type]"
                >
                  <i :class="cmd.icon"></i>
                  {{ cmd.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <!-- AI居民列表 -->
        <div class="agents-card glass-panel">
          <div class="card-header">
            <h3>
              <i class="fas fa-user-friends"></i>
              AI居民 ({{ totalAgents }})
            </h3>
            <div class="agent-stats">
              <span>平均心情: {{ averageMood }}%</span>
            </div>
          </div>
          
          <div class="agents-list">
            <div
              v-for="agent in agents"
              :key="agent.id"
              class="agent-item"
            >
              <div class="agent-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="agent-info">
                <h4>{{ agent.name }}</h4>
                <p class="agent-role">{{ agent.role }}</p>
                <p class="agent-personality">{{ agent.personality }}</p>
                <div class="agent-mood">
                  <span>心情: {{ Math.round(agent.mood) }}%</span>
                  <div class="mood-bar">
                    <div 
                      class="mood-fill" 
                      :style="{ 
                        width: agent.mood + '%',
                        backgroundColor: getMoodColor(agent.mood)
                      }"
                    ></div>
                  </div>
                </div>
                <div class="agent-activity">
                  <span>活跃度: {{ Math.round(agent.activity_level) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近事件 -->
        <div class="events-card glass-panel">
          <div class="card-header">
            <h3>
              <i class="fas fa-history"></i>
              最近事件
            </h3>
            <button @click="loadMoreEvents" class="load-more-btn">
              <i class="fas fa-chevron-down"></i>
              更多
            </button>
          </div>
          
          <div class="events-list">
            <div
              v-for="event in recentEvents"
              :key="event.id"
              :class="['event-item', event.type]"
            >
              <div class="event-icon">
                <i :class="getEventIcon(event.type)"></i>
              </div>
              <div class="event-content">
                <p class="event-description">{{ event.description }}</p>
                <div class="event-impact" v-if="event.impact && Object.keys(event.impact).length > 0">
                  <span
                    v-for="(value, key) in event.impact"
                    :key="key"
                    :class="['impact-tag', { 'positive': value > 0, 'negative': value < 0 }]"
                  >
                    {{ getImpactLabel(key) }}: {{ value > 0 ? '+' : '' }}{{ value }}
                  </span>
                </div>
                <span class="event-time">{{ formatTime(event.timestamp) }}</span>
              </div>
            </div>
          </div>

          <div v-if="events.length === 0" class="empty-state">
            <i class="fas fa-clock"></i>
            <p>暂无事件记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useCommunityStore } from '../stores/community';
import { useAppStore } from '../stores/app';

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
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.page-header p {
  color: #6b7280;
  margin: 0;
}

.community-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.dark .glass-panel {
  background: rgba(45, 55, 72, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark .card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.refresh-btn, .load-more-btn {
  background: transparent;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: inherit;
}

.refresh-btn:hover, .load-more-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 统计卡片样式 */
.stats-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.population { background: linear-gradient(45deg, #3b82f6, #1d4ed8); }
.stat-icon.happiness { background: linear-gradient(45deg, #ef4444, #dc2626); }
.stat-icon.activity { background: linear-gradient(45deg, #f59e0b, #d97706); }
.stat-icon.resources { background: linear-gradient(45deg, #10b981, #047857); }

.stat-info {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  display: block;
  margin-bottom: 0.5rem;
}

.stat-bar {
  width: 100%;
  height: 0.5rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0.25rem;
  overflow: hidden;
}

.dark .stat-bar {
  background: rgba(255, 255, 255, 0.1);
}

.stat-fill {
  height: 100%;
  border-radius: 0.25rem;
  transition: width 0.6s ease;
}

.stat-fill.happiness { background: linear-gradient(90deg, #ef4444, #dc2626); }
.stat-fill.activity { background: linear-gradient(90deg, #f59e0b, #d97706); }
.stat-fill.resources { background: linear-gradient(90deg, #10b981, #047857); }

/* 指令控制台样式 */
.command-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.command-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.dark .command-input {
  background: rgba(45, 55, 72, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
}

.command-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.execute-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-commands h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.command-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
}

.quick-cmd-btn {
  padding: 0.5rem 1rem;
  border: 1px solid;
  border-radius: 0.5rem;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

.quick-cmd-btn.positive {
  border-color: #10b981;
  color: #10b981;
}

.quick-cmd-btn.positive:hover {
  background: rgba(16, 185, 129, 0.1);
}

.quick-cmd-btn.building {
  border-color: #f59e0b;
  color: #f59e0b;
}

.quick-cmd-btn.building:hover {
  background: rgba(245, 158, 11, 0.1);
}

.quick-cmd-btn.neutral {
  border-color: #6b7280;
  color: #6b7280;
}

.quick-cmd-btn.neutral:hover {
  background: rgba(107, 114, 128, 0.1);
}

/* 居民列表样式 */
.agent-stats {
  font-size: 0.875rem;
  color: #6b7280;
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.agent-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 0.75rem;
  transition: all 0.3s ease;
}

.dark .agent-item {
  background: rgba(255, 255, 255, 0.05);
}

.agent-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.agent-avatar {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.agent-info {
  flex: 1;
}

.agent-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.agent-role {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  color: #667eea;
  font-weight: 500;
}

.agent-personality {
  margin: 0 0 0.75rem 0;
  font-size: 0.8rem;
  color: #6b7280;
}

.agent-mood, .agent-activity {
  margin-bottom: 0.5rem;
}

.agent-mood span, .agent-activity span {
  font-size: 0.8rem;
  font-weight: 500;
}

.mood-bar {
  width: 100%;
  height: 0.25rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0.125rem;
  overflow: hidden;
  margin-top: 0.25rem;
}

.dark .mood-bar {
  background: rgba(255, 255, 255, 0.1);
}

.mood-fill {
  height: 100%;
  border-radius: 0.125rem;
  transition: width 0.6s ease;
}

/* 事件列表样式 */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-left: 4px solid;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 0 0.5rem 0.5rem 0;
}

.dark .event-item {
  background: rgba(255, 255, 255, 0.05);
}

.event-item.positive { border-left-color: #10b981; }
.event-item.negative { border-left-color: #ef4444; }
.event-item.neutral { border-left-color: #6b7280; }
.event-item.building { border-left-color: #f59e0b; }
.event-item.system { border-left-color: #3b82f6; }

.event-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  color: white;
  background: #6b7280;
}

.event-content {
  flex: 1;
}

.event-description {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  line-height: 1.4;
}

.event-impact {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.impact-tag {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.impact-tag.positive {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.impact-tag.negative {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.event-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #667eea;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .community-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .command-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .execute-btn {
    justify-content: center;
  }
}
</style> 