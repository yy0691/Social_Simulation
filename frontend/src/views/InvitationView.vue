<template>
  <div class="invitation-view">
    <div class="invitation-header">
      <h1>社群邀请管理</h1>
      <p>管理社群成员的邀请和好友关系</p>
    </div>

    <div class="invitation-content">
      <!-- 邀请统计 -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📬</div>
            <div class="stat-info">
              <h3>{{ totalInvitations }}</h3>
              <p>总邀请数</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <h3>{{ acceptedInvitations }}</h3>
              <p>已接受</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-info">
              <h3>{{ pendingInvitations }}</h3>
              <p>待处理</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🤝</div>
            <div class="stat-info">
              <h3>{{ totalFriendships }}</h3>
              <p>好友关系</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能选项卡 -->
      <div class="tabs">
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'invitations' }"
          @click="activeTab = 'invitations'"
        >
          邀请记录
        </button>
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'friendships' }"
          @click="activeTab = 'friendships'"
        >
          好友关系
        </button>
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'members' }"
          @click="activeTab = 'members'"
        >
          社群成员
        </button>
        <button 
          class="tab-button"
          :class="{ active: activeTab === 'manual' }"
          @click="activeTab = 'manual'"
        >
          手动邀请
        </button>
      </div>

      <!-- 邀请记录 -->
      <div v-if="activeTab === 'invitations'" class="tab-content">
        <div class="section-header">
          <h2>邀请记录</h2>
          <div class="filters">
            <select v-model="selectedStatus" @change="loadInvitations">
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="accepted">已接受</option>
              <option value="rejected">已拒绝</option>
              <option value="expired">已过期</option>
            </select>
            <button @click="loadInvitations" class="refresh-btn">刷新</button>
          </div>
        </div>
        
        <div class="invitations-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="invitations.length === 0" class="no-data">暂无邀请记录</div>
          <div v-else>
            <div 
              v-for="invitation in invitations" 
              :key="invitation.id"
              class="invitation-card"
              :class="invitation.status"
            >
              <div class="invitation-header">
                <div class="inviter-info">
                  <strong>{{ invitation.inviter_name }}</strong>
                  <span class="action">邀请了</span>
                  <strong>{{ invitation.invitee_name }}</strong>
                </div>
                <div class="invitation-status" :class="invitation.status">
                  {{ getStatusText(invitation.status) }}
                </div>
              </div>
              
              <div class="invitation-details">
                <p class="invitation-message">{{ invitation.invitation_message }}</p>
                <div class="invitation-meta">
                  <span class="invitation-code">邀请码：{{ invitation.invitation_code }}</span>
                  <span class="invitation-email">邮箱：{{ invitation.invitee_email }}</span>
                </div>
                <div class="invitation-time">
                  <span>创建时间：{{ formatTime(invitation.created_at) }}</span>
                  <span v-if="invitation.expires_at">过期时间：{{ formatTime(invitation.expires_at) }}</span>
                  <span v-if="invitation.responded_at">回应时间：{{ formatTime(invitation.responded_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 好友关系 -->
      <div v-if="activeTab === 'friendships'" class="tab-content">
        <div class="section-header">
          <h2>好友关系</h2>
          <button @click="loadFriendships" class="refresh-btn">刷新</button>
        </div>
        
        <div class="friendships-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="friendships.length === 0" class="no-data">暂无好友关系</div>
          <div v-else>
            <div 
              v-for="friendship in friendships" 
              :key="friendship.id"
              class="friendship-card"
            >
              <div class="friendship-info">
                <div class="friends">
                  <span class="friend-name">{{ friendship.agent_name_1 }}</span>
                  <span class="friendship-icon">🤝</span>
                  <span class="friend-name">{{ friendship.agent_name_2 }}</span>
                </div>
                <div class="friendship-level">
                  友谊等级：{{ friendship.friendship_level }}/100
                  <div class="level-bar">
                    <div 
                      class="level-fill" 
                      :style="{ width: friendship.friendship_level + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
              <div class="friendship-meta">
                <span>建立时间：{{ formatTime(friendship.established_at) }}</span>
                <span>最近互动：{{ formatTime(friendship.last_interaction) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 社群成员 -->
      <div v-if="activeTab === 'members'" class="tab-content">
        <div class="section-header">
          <h2>社群成员</h2>
          <div class="filters">
            <select v-model="selectedMemberType" @change="loadMembers">
              <option value="">全部类型</option>
              <option value="agent">AI居民</option>
              <option value="human">人类成员</option>
            </select>
            <button @click="loadMembers" class="refresh-btn">刷新</button>
          </div>
        </div>
        
        <div class="members-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="members.length === 0" class="no-data">暂无成员记录</div>
          <div v-else>
            <div 
              v-for="member in members" 
              :key="member.id"
              class="member-card"
              :class="member.member_type"
            >
              <div class="member-info">
                <div class="member-avatar">
                  <i v-if="member.member_type === 'agent'" class="fas fa-robot"></i>
                  <i v-else class="fas fa-user"></i>
                </div>
                <div class="member-details">
                  <h3>{{ member.member_name }}</h3>
                  <p class="member-type">{{ member.member_type === 'agent' ? 'AI居民' : '人类成员' }}</p>
                  <p class="join-method">加入方式：{{ getJoinMethodText(member.join_method) }}</p>
                </div>
              </div>
              <div class="member-meta">
                <span>加入时间：{{ formatTime(member.joined_at) }}</span>
                <span>最近活跃：{{ formatTime(member.last_active) }}</span>
                <span v-if="member.invited_by" class="inviter">邀请者：{{ member.invited_by }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 手动邀请 -->
      <div v-if="activeTab === 'manual'" class="tab-content">
        <div class="section-header">
          <h2>手动发送邀请</h2>
          <p>选择一个AI居民来邀请外部朋友</p>
        </div>
        
        <div class="manual-invitation">
          <form @submit.prevent="sendManualInvitation" class="invitation-form">
            <div class="form-group">
              <label>邀请者（AI居民）</label>
              <select v-model="manualForm.inviter_agent_name" required>
                <option value="">请选择邀请的居民</option>
                <option v-for="agent in availableAgents" :key="agent.id" :value="agent.name">
                  {{ agent.name }} ({{ agent.occupation }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>被邀请者姓名</label>
              <input 
                v-model="manualForm.invitee_name" 
                type="text" 
                required 
                placeholder="请输入朋友的姓名"
              >
            </div>
            
            <div class="form-group">
              <label>被邀请者邮箱</label>
              <input 
                v-model="manualForm.invitee_email" 
                type="email" 
                required 
                placeholder="请输入朋友的邮箱地址"
              >
            </div>
            
            <div class="form-group">
              <label>邀请消息</label>
              <textarea 
                v-model="manualForm.invitation_message" 
                placeholder="输入个性化的邀请消息"
                rows="3"
              ></textarea>
            </div>
            
            <button type="submit" :disabled="sending" class="send-invitation-btn">
              {{ sending ? '发送中...' : '发送邀请' }}
            </button>
          </form>
          
          <div v-if="invitationResult" class="invitation-result" :class="invitationResult.success ? 'success' : 'error'">
            <p>{{ invitationResult.message }}</p>
            <div v-if="invitationResult.success && invitationResult.data">
              <p>邀请码：<strong>{{ invitationResult.data.invitation_code }}</strong></p>
              <p>过期时间：{{ formatTime(invitationResult.data.expires_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'

export default {
  name: 'InvitationView',
  setup() {
    const activeTab = ref('invitations')
    const loading = ref(false)
    const sending = ref(false)
    
    // 数据
    const invitations = ref([])
    const friendships = ref([])
    const members = ref([])
    const availableAgents = ref([])
    
    // 筛选
    const selectedStatus = ref('')
    const selectedMemberType = ref('')
    
    // 手动邀请表单
    const manualForm = reactive({
      inviter_agent_name: '',
      invitee_name: '',
      invitee_email: '',
      invitation_message: '欢迎加入我们的AI社群！'
    })
    
    const invitationResult = ref(null)
    
    // 计算属性
    const totalInvitations = computed(() => invitations.value.length)
    const acceptedInvitations = computed(() => 
      invitations.value.filter(inv => inv.status === 'accepted').length
    )
    const pendingInvitations = computed(() => 
      invitations.value.filter(inv => inv.status === 'pending').length
    )
    const totalFriendships = computed(() => friendships.value.length)
    
    // 方法
    const loadInvitations = async () => {
      try {
        loading.value = true
        const params = new URLSearchParams()
        if (selectedStatus.value) {
          params.append('status', selectedStatus.value)
        }
        
        const response = await fetch(`/api/v1/invitation/list?${params}`)
        const result = await response.json()
        
        if (result.success) {
          invitations.value = result.data.invitations
        }
      } catch (error) {
        console.error('加载邀请列表失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadFriendships = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/v1/invitation/friendships')
        const result = await response.json()
        
        if (result.success) {
          friendships.value = result.data.friendships
        }
      } catch (error) {
        console.error('加载好友关系失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadMembers = async () => {
      try {
        loading.value = true
        const params = new URLSearchParams()
        if (selectedMemberType.value) {
          params.append('member_type', selectedMemberType.value)
        }
        
        const response = await fetch(`/api/v1/invitation/members?${params}`)
        const result = await response.json()
        
        if (result.success) {
          members.value = result.data.members
        }
      } catch (error) {
        console.error('加载成员列表失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadAvailableAgents = async () => {
      try {
        const response = await fetch('/api/v1/community/agents')
        const result = await response.json()
        
        if (result.success) {
          availableAgents.value = result.data.filter(agent => agent.is_active)
        }
      } catch (error) {
        console.error('加载居民列表失败:', error)
      }
    }
    
    const sendManualInvitation = async () => {
      try {
        sending.value = true
        invitationResult.value = null
        
        const response = await fetch('/api/v1/invitation/send', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(manualForm)
        })
        
        const result = await response.json()
        invitationResult.value = result
        
        if (result.success) {
          // 重置表单
          Object.assign(manualForm, {
            inviter_agent_name: '',
            invitee_name: '',
            invitee_email: '',
            invitation_message: '欢迎加入我们的AI社群！'
          })
          
          // 刷新邀请列表
          await loadInvitations()
        }
      } catch (error) {
        console.error('发送邀请失败:', error)
        invitationResult.value = {
          success: false,
          message: '发送邀请时发生网络错误'
        }
      } finally {
        sending.value = false
      }
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待处理',
        accepted: '已接受',
        rejected: '已拒绝',
        expired: '已过期'
      }
      return statusMap[status] || status
    }
    
    const getJoinMethodText = (method) => {
      const methodMap = {
        system: '系统创建',
        invitation: '邀请加入',
        application: '申请加入'
      }
      return methodMap[method] || method
    }
    
    const formatTime = (timeString) => {
      if (!timeString) return ''
      return new Date(timeString).toLocaleString('zh-CN')
    }
    
    // 生命周期
    onMounted(async () => {
      await loadInvitations()
      await loadFriendships()
      await loadMembers()
      await loadAvailableAgents()
    })
    
    return {
      activeTab,
      loading,
      sending,
      invitations,
      friendships,
      members,
      availableAgents,
      selectedStatus,
      selectedMemberType,
      manualForm,
      invitationResult,
      totalInvitations,
      acceptedInvitations,
      pendingInvitations,
      totalFriendships,
      loadInvitations,
      loadFriendships,
      loadMembers,
      sendManualInvitation,
      getStatusText,
      getJoinMethodText,
      formatTime
    }
  }
}
</script>

<style scoped>
.invitation-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.invitation-header {
  text-align: center;
  margin-bottom: 30px;
}

.invitation-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.invitation-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.stats-section {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2.5em;
}

.stat-info h3 {
  font-size: 2em;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.tabs {
  display: flex;
  border-bottom: 2px solid #ecf0f1;
  margin-bottom: 20px;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  color: #7f8c8d;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-button:hover {
  color: #3498db;
}

.tab-button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  color: #2c3e50;
  margin: 0;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filters select {
  padding: 8px 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  font-size: 14px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease;
}

.refresh-btn:hover {
  background: #2980b9;
}

.loading, .no-data {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
  font-size: 16px;
}

.invitation-card, .friendship-card, .member-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ecf0f1;
}

.invitation-card.pending {
  border-left-color: #f39c12;
}

.invitation-card.accepted {
  border-left-color: #27ae60;
}

.invitation-card.rejected {
  border-left-color: #e74c3c;
}

.invitation-card.expired {
  border-left-color: #95a5a6;
}

.invitation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.inviter-info {
  font-size: 16px;
}

.inviter-info .action {
  color: #7f8c8d;
  margin: 0 8px;
}

.invitation-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.invitation-status.pending {
  background: #fff3cd;
  color: #856404;
}

.invitation-status.accepted {
  background: #d4edda;
  color: #155724;
}

.invitation-status.rejected {
  background: #f8d7da;
  color: #721c24;
}

.invitation-status.expired {
  background: #e2e3e5;
  color: #383d41;
}

.invitation-message {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  color: #495057;
  font-style: italic;
}

.invitation-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #6c757d;
}

.invitation-time {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #868e96;
}

.friendship-info {
  margin-bottom: 15px;
}

.friends {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: bold;
}

.friendship-icon {
  font-size: 1.5em;
}

.friendship-level {
  font-size: 14px;
  color: #6c757d;
}

.level-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  margin-top: 5px;
  overflow: hidden;
}

.level-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

.friendship-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #868e96;
}

.member-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.member-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
  color: #6c757d;
}

.member-card.agent .member-avatar {
  background: #e3f2fd;
  color: #1976d2;
}

.member-card.human .member-avatar {
  background: #f3e5f5;
  color: #7b1fa2;
}

.member-details h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.member-details p {
  margin: 0;
  font-size: 14px;
  color: #6c757d;
}

.member-meta {
  text-align: right;
  font-size: 12px;
  color: #868e96;
}

.member-meta span {
  display: block;
  margin-bottom: 3px;
}

.invitation-form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.send-invitation-btn {
  width: 100%;
  padding: 15px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s ease;
}

.send-invitation-btn:hover:not(:disabled) {
  background: #219a52;
}

.send-invitation-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.invitation-result {
  margin-top: 20px;
  padding: 15px;
  border-radius: 6px;
  border: 2px solid;
}

.invitation-result.success {
  background: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.invitation-result.error {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.invitation-result strong {
  font-family: 'Courier New', monospace;
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

@media (max-width: 768px) {
  .invitation-view {
    padding: 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .filters {
    justify-content: center;
  }
  
  .invitation-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .invitation-meta,
  .invitation-time,
  .friendship-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .member-card {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .member-meta {
    text-align: left;
  }
}
</style> 