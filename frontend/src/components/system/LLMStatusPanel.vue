<template>
  <div class="llm-status-panel">
    <!-- 状态头部 -->
    <div class="status-header">
      <div class="status-indicator">
        <div :class="['status-dot', statusClass]"></div>
        <span class="status-text">{{ statusText }}</span>
      </div>
      <button 
        @click="refreshStatus" 
        :disabled="loading"
        class="refresh-btn"
      >
        <svg v-if="loading" class="animate-spin" width="16" height="16" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
          <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" fill="currentColor"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
        </svg>
      </button>
    </div>

    <!-- 配置信息 -->
    <div v-if="llmStatus" class="config-info">
      <div class="config-grid">
        <div class="config-item">
          <span class="label">提供商:</span>
          <span class="value">{{ llmStatus.provider || 'Unknown' }}</span>
        </div>
        <div class="config-item">
          <span class="label">模型:</span>
          <span class="value">{{ llmStatus.model || 'Unknown' }}</span>
        </div>
        <div class="config-item">
          <span class="label">最大tokens:</span>
          <span class="value">{{ llmStatus.max_tokens || 'Unknown' }}</span>
        </div>
        <div class="config-item">
          <span class="label">温度:</span>
          <span class="value">{{ llmStatus.temperature || 'Unknown' }}</span>
        </div>
      </div>
    </div>

    <!-- 测试按钮 -->
    <div class="test-section">
      <button 
        @click="runConnectionTest" 
        :disabled="testLoading"
        class="test-btn"
      >
        <svg v-if="testLoading" class="animate-spin" width="16" height="16" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
          <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" fill="currentColor"/>
        </svg>
        {{ testLoading ? '测试中...' : '运行连接测试' }}
      </button>
    </div>

    <!-- 测试结果 -->
    <div v-if="testResult" class="test-results">
      <h4>测试结果</h4>
      <div class="test-grid">
        <div :class="['test-item', testResult.config_check ? 'success' : 'failed']">
          <span>配置检查</span>
          <svg v-if="testResult.config_check" width="16" height="16" viewBox="0 0 24 24" fill="green">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="red">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </div>
        <div :class="['test-item', testResult.client_init ? 'success' : 'failed']">
          <span>客户端初始化</span>
          <svg v-if="testResult.client_init" width="16" height="16" viewBox="0 0 24 24" fill="green">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="red">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </div>
        <div :class="['test-item', testResult.api_call ? 'success' : 'failed']">
          <span>API调用</span>
          <svg v-if="testResult.api_call" width="16" height="16" viewBox="0 0 24 24" fill="green">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="red">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </div>
        <div :class="['test-item', testResult.command_parse ? 'success' : 'failed']">
          <span>指令解析</span>
          <svg v-if="testResult.command_parse" width="16" height="16" viewBox="0 0 24 24" fill="green">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="red">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 日志输出 -->
    <div v-if="testResult && (testResult.logs.length > 0 || testResult.errors.length > 0)" class="logs-section">
      <h4>详细日志</h4>
      <div class="logs-container">
        <div v-for="(log, index) in testResult.logs" :key="`log-${index}`" class="log-item success">
          {{ log }}
        </div>
        <div v-for="(error, index) in testResult.errors" :key="`error-${index}`" class="log-item error">
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <h4>错误信息</h4>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// 响应式数据
const loading = ref(false)
const testLoading = ref(false)
const llmStatus = ref<any>(null)
const testResult = ref<any>(null)
const error = ref('')

// 计算属性
const statusClass = computed(() => {
  if (!llmStatus.value) return 'unknown'
  if (llmStatus.value.config_valid && llmStatus.value.client_initialized) {
    return 'connected'
  } else if (llmStatus.value.config_valid) {
    return 'warning'
  } else {
    return 'error'
  }
})

const statusText = computed(() => {
  if (!llmStatus.value) return '未知状态'
  if (llmStatus.value.config_valid && llmStatus.value.client_initialized) {
    return 'LLM已连接'
  } else if (llmStatus.value.config_valid) {
    return '配置有效，等待连接'
  } else {
    return 'LLM未配置'
  }
})

// API调用
const API_BASE = 'http://127.0.0.1:8000/api/v1'

async function fetchLLMStatus() {
  try {
    const response = await fetch(`${API_BASE}/system/llm/status`)
    const data = await response.json()
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.error || '获取状态失败')
    }
  } catch (err: any) {
    throw new Error(`网络错误: ${err.message}`)
  }
}

async function runLLMTest() {
  try {
    const response = await fetch(`${API_BASE}/system/llm/test`, {
      method: 'POST'
    })
    const data = await response.json()
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.error || '测试失败')
    }
  } catch (err: any) {
    throw new Error(`网络错误: ${err.message}`)
  }
}

// 方法
async function refreshStatus() {
  loading.value = true
  error.value = ''
  try {
    llmStatus.value = await fetchLLMStatus()
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function runConnectionTest() {
  testLoading.value = true
  error.value = ''
  testResult.value = null
  try {
    testResult.value = await runLLMTest()
  } catch (err: any) {
    error.value = err.message
  } finally {
    testLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.llm-status-panel {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 600px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.connected {
  background-color: #10b981;
}

.status-dot.warning {
  background-color: #f59e0b;
}

.status-dot.error {
  background-color: #ef4444;
}

.status-dot.unknown {
  background-color: #6b7280;
}

.status-text {
  font-weight: 600;
  color: #374151;
}

.refresh-btn, .test-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover, .test-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.refresh-btn:disabled, .test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.config-info {
  margin-bottom: 20px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 4px;
}

.config-item .label {
  color: #6b7280;
  font-size: 14px;
}

.config-item .value {
  color: #374151;
  font-weight: 500;
}

.test-section {
  margin-bottom: 20px;
}

.test-btn {
  width: 100%;
  justify-content: center;
  padding: 12px;
  background: #3b82f6;
  color: white;
  border: none;
  font-weight: 500;
}

.test-btn:hover:not(:disabled) {
  background: #2563eb;
}

.test-results {
  margin-bottom: 20px;
}

.test-results h4 {
  margin: 0 0 12px 0;
  color: #374151;
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.test-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.test-item.success {
  background: #d1fae5;
  color: #065f46;
}

.test-item.failed {
  background: #fee2e2;
  color: #991b1b;
}

.logs-section {
  margin-bottom: 20px;
}

.logs-section h4 {
  margin: 0 0 12px 0;
  color: #374151;
}

.logs-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 8px;
  background: #f9fafb;
}

.log-item {
  padding: 4px 0;
  font-size: 12px;
  font-family: monospace;
  border-bottom: 1px solid #e5e7eb;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.success {
  color: #065f46;
}

.log-item.error {
  color: #991b1b;
}

.error-message {
  padding: 12px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  color: #991b1b;
}

.error-message h4 {
  margin: 0 0 8px 0;
}

.error-message p {
  margin: 0;
  font-size: 14px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style> 