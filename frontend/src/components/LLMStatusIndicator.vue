<template>
  <div class="llm-status-indicator" @click="showPanel = !showPanel">
    <div :class="['status-dot', statusClass]"></div>
    <span class="status-text">LLM</span>
    
    <!-- 简化面板 -->
    <div v-if="showPanel" class="status-panel">
      <div class="panel-content">
        <h4>LLM 状态</h4>
        <p>{{ statusText }}</p>
        <button @click="testConnection" :disabled="testing">
          {{ testing ? '测试中...' : '测试连接' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const showPanel = ref(false)
const status = ref('unknown')
const testing = ref(false)

// 计算属性
const statusClass = computed(() => {
  switch (status.value) {
    case 'connected': return 'connected'
    case 'error': return 'error'
    default: return 'unknown'
  }
})

const statusText = computed(() => {
  switch (status.value) {
    case 'connected': return 'LLM 已连接'
    case 'error': return 'LLM 连接失败'
    default: return 'LLM 状态未知'
  }
})

// 方法
async function checkStatus() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/system/llm/status')
    const data = await response.json()
    if (data.success && data.data.config_valid && data.data.client_initialized) {
      status.value = 'connected'
    } else {
      status.value = 'error'
    }
  } catch (error) {
    status.value = 'error'
  }
}

async function testConnection() {
  testing.value = true
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/system/llm/test', {
      method: 'POST'
    })
    const data = await response.json()
    if (data.success && data.data.overall_success) {
      status.value = 'connected'
    } else {
      status.value = 'error'
    }
  } catch (error) {
    status.value = 'error'
  } finally {
    testing.value = false
  }
}

// 生命周期
onMounted(() => {
  checkStatus()
  // 每30秒检查一次
  setInterval(checkStatus, 30000)
})
</script>

<style scoped>
.llm-status-indicator {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.llm-status-indicator:hover {
  background: rgba(255, 255, 255, 0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.connected {
  background-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.status-dot.error {
  background-color: #ef4444;
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

.status-dot.unknown {
  background-color: #6b7280;
  box-shadow: 0 0 0 2px rgba(107, 114, 128, 0.2);
}

.status-text {
  font-size: 14px;
  font-weight: 500;
  color: currentColor;
}

.status-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 250px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.panel-content {
  padding: 16px;
}

.panel-content h4 {
  margin: 0 0 8px 0;
  color: #374151;
}

.panel-content p {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 14px;
}

.panel-content button {
  width: 100%;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.panel-content button:hover:not(:disabled) {
  background: #2563eb;
}

.panel-content button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 