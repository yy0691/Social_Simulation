<template>
  <div class="settings-view">
    <!-- 粒子背景 -->
    <ParticleBackground />
    
    <!-- 主要内容区域 -->
    <div class="settings-content">
      <!-- 设置头部 -->
      <GlassPanel variant="default" class="settings-header">
        <div class="header-content">
          <div class="settings-info">
            <div class="settings-icon">
              <i class="fas fa-cog"></i>
            </div>
            <div class="settings-details">
              <h2 class="settings-title">游戏设置</h2>
              <p class="settings-subtitle">个性化你的AI社群体验</p>
            </div>
          </div>
        </div>
      </GlassPanel>

      <!-- 设置主体 -->
      <div class="settings-body">
        <!-- 外观设置 -->
        <GlassPanel variant="neon" class="setting-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-palette"></i>
              外观设置
            </h3>
          </div>
          
          <div class="setting-items">
            <!-- 主题切换 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">主题模式</label>
                <p class="setting-description">选择你喜欢的界面主题</p>
              </div>
              <div class="theme-switcher">
                <NeonButton
                  v-for="theme in themes"
                  :key="theme.value"
                  :variant="currentTheme === theme.value ? 'primary' : 'ghost'"
                  size="small"
                  :icon="theme.icon"
                  @click="changeTheme(theme.value)"
                  class="theme-btn"
                >
                  {{ theme.label }}
                </NeonButton>
              </div>
            </div>

            <!-- 动画效果 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">动画效果</label>
                <p class="setting-description">启用界面动画和过渡效果</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.animations"
                  @change="updateSetting('animations', $event)"
                />
              </div>
            </div>

            <!-- 粒子背景 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">粒子背景</label>
                <p class="setting-description">显示动态粒子背景效果</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.particleBackground"
                  @change="updateSetting('particleBackground', $event)"
                />
              </div>
            </div>

            <!-- 粒子密度 -->
            <div class="setting-item" v-if="settings.particleBackground">
              <div class="setting-info">
                <label class="setting-label">粒子密度</label>
                <p class="setting-description">调整粒子背景的密度</p>
              </div>
              <div class="setting-control">
                <CustomSlider
                  v-model="settings.particleDensity"
                  :min="20"
                  :max="200"
                  :step="10"
                  @change="updateSetting('particleDensity', $event)"
                />
                <span class="setting-value">{{ settings.particleDensity }}</span>
              </div>
            </div>
          </div>
        </GlassPanel>

        <!-- 音频设置 -->
        <GlassPanel variant="default" class="setting-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-volume-up"></i>
              音频设置
            </h3>
          </div>
          
          <div class="setting-items">
            <!-- 主音量 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">主音量</label>
                <p class="setting-description">调整游戏整体音量</p>
              </div>
              <div class="setting-control">
                <CustomSlider
                  v-model="settings.masterVolume"
                  :min="0"
                  :max="100"
                  :step="5"
                  @change="updateSetting('masterVolume', $event)"
                />
                <span class="setting-value">{{ settings.masterVolume }}%</span>
              </div>
            </div>

            <!-- 音效音量 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">音效音量</label>
                <p class="setting-description">调整按钮点击等音效音量</p>
              </div>
              <div class="setting-control">
                <CustomSlider
                  v-model="settings.soundEffectVolume"
                  :min="0"
                  :max="100"
                  :step="5"
                  @change="updateSetting('soundEffectVolume', $event)"
                />
                <span class="setting-value">{{ settings.soundEffectVolume }}%</span>
              </div>
            </div>

            <!-- 静音模式 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">静音模式</label>
                <p class="setting-description">关闭所有音频</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.muteAll"
                  @change="updateSetting('muteAll', $event)"
                />
              </div>
            </div>
          </div>
        </GlassPanel>

        <!-- 通知设置 -->
        <GlassPanel variant="transparent" class="setting-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-bell"></i>
              通知设置
            </h3>
          </div>
          
          <div class="setting-items">
            <!-- 桌面通知 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">桌面通知</label>
                <p class="setting-description">允许发送桌面通知</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.desktopNotifications"
                  @change="updateSetting('desktopNotifications', $event)"
                />
              </div>
            </div>

            <!-- 社群事件通知 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">社群事件通知</label>
                <p class="setting-description">当社群发生重要事件时通知</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.communityNotifications"
                  @change="updateSetting('communityNotifications', $event)"
                />
              </div>
            </div>

            <!-- AI消息通知 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">AI消息通知</label>
                <p class="setting-description">收到AI消息时显示通知</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.chatNotifications"
                  @change="updateSetting('chatNotifications', $event)"
                />
              </div>
            </div>
          </div>
        </GlassPanel>

        <!-- 性能设置 -->
        <GlassPanel variant="default" class="setting-section">
          <div class="section-header">
            <h3 class="section-title">
              <i class="fas fa-tachometer-alt"></i>
              性能设置
            </h3>
          </div>
          
          <div class="setting-items">
            <!-- 自动刷新间隔 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">自动刷新间隔</label>
                <p class="setting-description">社群数据自动更新的时间间隔（秒）</p>
              </div>
              <div class="setting-control">
                <CustomSlider
                  v-model="settings.refreshInterval"
                  :min="5"
                  :max="60"
                  :step="5"
                  @change="updateSetting('refreshInterval', $event)"
                />
                <span class="setting-value">{{ settings.refreshInterval }}s</span>
              </div>
            </div>

            <!-- 减少动画 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">减少动画</label>
                <p class="setting-description">减少动画效果以提升性能</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.reducedMotion"
                  @change="updateSetting('reducedMotion', $event)"
                />
              </div>
            </div>

            <!-- 低质量模式 -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label">低质量模式</label>
                <p class="setting-description">降低视觉质量以提升性能</p>
              </div>
              <div class="setting-control">
                <ToggleSwitch
                  v-model="settings.lowQualityMode"
                  @change="updateSetting('lowQualityMode', $event)"
                />
              </div>
            </div>
          </div>
        </GlassPanel>

        <!-- 操作按钮 -->
        <div class="settings-actions">
          <NeonButton
            variant="success"
            icon="fas fa-save"
            @click="saveSettings"
            :loading="saving"
          >
            保存设置
          </NeonButton>
          
          <NeonButton
            variant="warning"
            icon="fas fa-undo"
            @click="resetSettings"
            :disabled="saving"
          >
            重置为默认
          </NeonButton>
          
          <NeonButton
            variant="danger"
            icon="fas fa-trash"
            @click="clearAllData"
            :disabled="saving"
          >
            清除所有数据
          </NeonButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { 
  ParticleBackground, 
  GlassPanel, 
  NeonButton,
  ToggleSwitch,
  CustomSlider
} from '../components/ui'

// 状态管理
const appStore = useAppStore()

// 响应式数据
const saving = ref(false)
const currentTheme = ref('dark')

// 主题选项
const themes = [
  { value: 'light', label: '明亮', icon: 'fas fa-sun' },
  { value: 'dark', label: '暗黑', icon: 'fas fa-moon' },
  { value: 'auto', label: '自动', icon: 'fas fa-adjust' }
]

// 设置数据
const settings = reactive({
  // 外观设置
  theme: 'dark',
  animations: true,
  particleBackground: true,
  particleDensity: 100,
  
  // 音频设置
  masterVolume: 70,
  soundEffectVolume: 50,
  muteAll: false,
  
  // 通知设置
  desktopNotifications: true,
  communityNotifications: true,
  chatNotifications: true,
  
  // 性能设置
  refreshInterval: 30,
  reducedMotion: false,
  lowQualityMode: false
})

// 默认设置
const defaultSettings = { ...settings }

// 监听主题变化
watch(() => settings.theme, (newTheme) => {
  currentTheme.value = newTheme
  applyTheme(newTheme)
})

// 监听音频设置变化
watch(() => settings.muteAll, (muted) => {
  if (muted) {
    // 全局静音逻辑
    document.documentElement.style.setProperty('--audio-enabled', '0')
  } else {
    document.documentElement.style.setProperty('--audio-enabled', '1')
  }
})

// 监听性能设置变化
watch(() => settings.reducedMotion, (reduced) => {
  if (reduced) {
    document.documentElement.classList.add('reduced-motion')
  } else {
    document.documentElement.classList.remove('reduced-motion')
  }
})

// 方法
const changeTheme = (theme: string) => {
  settings.theme = theme
  updateSetting('theme', theme)
}

const applyTheme = (theme: string) => {
  const html = document.documentElement
  
  // 移除现有主题类
  html.classList.remove('light', 'dark')
  
  if (theme === 'auto') {
    // 根据系统主题自动切换
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    html.classList.add(prefersDark ? 'dark' : 'light')
  } else {
    html.classList.add(theme)
  }
}

const updateSetting = <K extends keyof typeof settings>(key: K, value: typeof settings[K]) => {
  // 更新设置值
  settings[key] = value
  
  // 立即保存到本地存储
  localStorage.setItem('gameSettings', JSON.stringify(settings))
  
  // 显示提示
  appStore.addNotification({
    type: 'info',
    title: '设置已更新',
    message: '你的设置更改已自动保存',
    duration: 2000
  })
}

const saveSettings = async () => {
  saving.value = true
  
  try {
    // 模拟保存到服务器
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 保存到本地存储
    localStorage.setItem('gameSettings', JSON.stringify(settings))
    
    appStore.addNotification({
      type: 'success',
      title: '保存成功',
      message: '所有设置已成功保存',
      duration: 3000
    })
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '保存失败',
      message: '设置保存时发生错误',
      duration: 5000
    })
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  // 重置为默认设置
  Object.assign(settings, defaultSettings)
  
  // 保存到本地存储
  localStorage.setItem('gameSettings', JSON.stringify(settings))
  
  appStore.addNotification({
    type: 'info',
    title: '设置已重置',
    message: '所有设置已恢复为默认值',
    duration: 3000
  })
}

const clearAllData = () => {
  if (confirm('确定要清除所有数据吗？这将删除你的所有游戏进度和设置。')) {
    // 清除本地存储
    localStorage.clear()
    
    // 重置设置
    Object.assign(settings, defaultSettings)
    
    appStore.addNotification({
      type: 'warning',
      title: '数据已清除',
      message: '所有本地数据已被删除',
      duration: 5000
    })
    
    // 刷新页面
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  }
}

// 加载设置
const loadSettings = () => {
  try {
    const savedSettings = localStorage.getItem('gameSettings')
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings)
      Object.assign(settings, parsed)
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 组件挂载
onMounted(() => {
  loadSettings()
  applyTheme(settings.theme)
  currentTheme.value = settings.theme
})
</script>

<style scoped>
.settings-view {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
}

.settings-content {
  position: relative;
  z-index: 1;
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 设置头部 */
.settings-header {
  flex-shrink: 0;
}

.header-content {
  padding: 2rem;
}

.settings-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.settings-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}

.settings-details h2 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.settings-details p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

/* 设置主体 */
.settings-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.setting-section {
  padding: 0;
}

.section-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-title i {
  font-size: 1.2rem;
  color: #00d4ff;
}

.setting-items {
  padding: 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  gap: 2rem;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-label {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.setting-description {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.setting-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #00d4ff;
  min-width: 3rem;
  text-align: center;
}

/* 主题切换器 */
.theme-switcher {
  display: flex;
  gap: 0.5rem;
}

.theme-btn {
  min-width: 5rem;
}

/* 操作按钮 */
.settings-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding: 2rem 0;
}

/* 动画效果 */
.setting-item {
  transition: all 0.3s ease;
}

.setting-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-content {
    padding: 1rem;
  }
  
  .header-content {
    padding: 1.5rem;
  }
  
  .settings-info {
    gap: 1rem;
  }
  
  .settings-icon {
    width: 3rem;
    height: 3rem;
    font-size: 1.5rem;
  }
  
  .settings-details h2 {
    font-size: 1.5rem;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .setting-control {
    width: 100%;
    justify-content: space-between;
  }
  
  .settings-actions {
    flex-direction: column;
  }
  
  .theme-switcher {
    width: 100%;
    justify-content: space-between;
  }
}

/* 深色主题适配 */
.dark .section-header {
  border-bottom-color: rgba(255, 255, 255, 0.05);
}

.dark .setting-item {
  border-bottom-color: rgba(255, 255, 255, 0.03);
}

.dark .setting-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* 减少动画模式 */
.reduced-motion * {
  animation-duration: 0.001s !important;
  transition-duration: 0.001s !important;
}
</style> 