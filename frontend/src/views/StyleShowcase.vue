<template>
  <div class="style-showcase">
    <div class="showcase-header">
      <h1>AI社群模拟小游戏 - 样式展示</h1>
      <p>展示所有优化后的UI组件和交互效果</p>
    </div>

    <!-- 按钮展示 -->
    <section class="showcase-section card-enter">
      <h2>霓虹按钮组件</h2>
      <div class="button-grid">
        <button class="neon-button">默认按钮</button>
        <button class="neon-button primary">主要按钮</button>
        <button class="neon-button secondary">次要按钮</button>
        <button class="neon-button success">成功按钮</button>
        <button class="neon-button danger">危险按钮</button>
        <button class="neon-button small">小型按钮</button>
        <button class="neon-button large">大型按钮</button>
        <button class="neon-button icon-only">
          <i class="fas fa-star"></i>
        </button>
      </div>
    </section>

    <!-- 状态指示器展示 -->
    <section class="showcase-section card-enter">
      <h2>状态指示器</h2>
      <div class="status-grid">
        <div class="status-indicator online">
          <div class="status-dot pulse"></div>
          <span>在线状态</span>
        </div>
        <div class="status-indicator offline">
          <div class="status-dot"></div>
          <span>离线状态</span>
        </div>
        <div class="status-indicator warning">
          <div class="status-dot pulse"></div>
          <span>警告状态</span>
        </div>
        <div class="status-indicator info">
          <div class="status-dot pulse"></div>
          <span>信息状态</span>
        </div>
      </div>
    </section>

    <!-- 输入框展示 -->
    <section class="showcase-section card-enter">
      <h2>输入框组件</h2>
      <div class="input-grid">
        <div class="neon-input">
          <label class="neon-input-label">用户名</label>
          <input type="text" class="neon-input-field" placeholder="请输入用户名">
        </div>
        <div class="neon-input">
          <label class="neon-input-label">邮箱地址</label>
          <input type="email" class="neon-input-field" placeholder="请输入邮箱">
          <i class="neon-input-icon fas fa-envelope"></i>
        </div>
        <div class="neon-input">
          <label class="neon-input-label">消息内容</label>
          <textarea class="neon-input-field" placeholder="请输入消息内容" rows="3"></textarea>
        </div>
      </div>
    </section>

    <!-- 卡片展示 -->
    <section class="showcase-section card-enter">
      <h2>毛玻璃卡片</h2>
      <div class="card-grid">
        <div class="neon-card">
          <h3>基础卡片</h3>
          <p>这是一个基础的毛玻璃卡片，具有霓虹边框和悬浮效果。</p>
          <div class="badge primary">新功能</div>
        </div>
        <div class="neon-card">
          <h3>统计卡片</h3>
          <div class="stat-number">1,234</div>
          <p>当前在线用户数</p>
          <div class="progress-bar">
            <div class="progress-fill animated" style="width: 75%"></div>
          </div>
        </div>
        <div class="neon-card">
          <h3>交互卡片</h3>
          <p>悬浮在此卡片上查看效果</p>
          <div class="toggle-switch">
            <input type="checkbox" id="toggle1">
            <label class="toggle-slider" for="toggle1"></label>
          </div>
        </div>
      </div>
    </section>

    <!-- 徽章展示 -->
    <section class="showcase-section card-enter">
      <h2>徽章组件</h2>
      <div class="badge-grid">
        <span class="badge primary">主要</span>
        <span class="badge secondary">次要</span>
        <span class="badge success">成功</span>
        <span class="badge warning">警告</span>
        <span class="badge danger">危险</span>
        <span class="badge badge-count updated">99+</span>
      </div>
    </section>

    <!-- 加载指示器展示 -->
    <section class="showcase-section card-enter">
      <h2>加载效果</h2>
      <div class="loading-grid">
        <div class="loading-spinner"></div>
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
        <div class="loading-skeleton" style="height: 20px; border-radius: 4px;"></div>
        <div class="connection-indicator connecting">
          <i class="fas fa-wifi"></i>
          <span>连接中...</span>
        </div>
      </div>
    </section>

    <!-- 消息气泡展示 -->
    <section class="showcase-section card-enter">
      <h2>聊天消息样式</h2>
      <div class="message-showcase">
        <div class="message-item">
          <div class="message-avatar">
            <i class="fas fa-user"></i>
          </div>
          <div class="message-bubble">
            <div class="message-content">你好！这是一个用户消息示例。</div>
            <div class="message-time">10:30</div>
          </div>
        </div>
        <div class="message-item user">
          <div class="message-bubble user">
            <div class="message-content">这是一个AI助手的回复消息。</div>
            <div class="message-time">10:31</div>
          </div>
          <div class="message-avatar">
            <i class="fas fa-robot"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- 工具提示展示 -->
    <section class="showcase-section card-enter">
      <h2>工具提示</h2>
      <div class="tooltip-grid">
        <div class="tooltip-container">
          <button class="neon-button">悬浮查看</button>
          <div class="tooltip">这是一个工具提示</div>
        </div>
      </div>
    </section>

    <!-- 动画展示 -->
    <section class="showcase-section card-enter">
      <h2>动画效果</h2>
      <div class="animation-grid">
        <button class="neon-button" @click="triggerAnimation">触发成功动画</button>
        <button class="neon-button" @click="triggerError">触发错误动画</button>
        <div class="icon-rotate" :class="{ active: isRotating }" @click="rotateIcon">
          <i class="fas fa-sync-alt"></i>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'StyleShowcase',
  setup() {
    const isRotating = ref(false)

    const triggerAnimation = () => {
      // 触发成功动画
      const target = event.target
      target.classList.add('success-animation')
      setTimeout(() => {
        target.classList.remove('success-animation')
      }, 600)
    }

    const triggerError = () => {
      // 触发错误动画
      const target = event.target
      target.classList.add('error-animation')
      setTimeout(() => {
        target.classList.remove('error-animation')
      }, 600)
    }

    const rotateIcon = () => {
      isRotating.value = true
      setTimeout(() => {
        isRotating.value = false
      }, 500)
    }

    return {
      isRotating,
      triggerAnimation,
      triggerError,
      rotateIcon
    }
  }
}
</script>

<style scoped>
.style-showcase {
  padding: var(--spacing-xl);
  max-width: 1200px;
  margin: 0 auto;
}

.showcase-header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
}

.showcase-header h1 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
  background: linear-gradient(45deg, var(--neon-blue), var(--neon-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.showcase-section {
  margin-bottom: var(--spacing-3xl);
  padding: var(--spacing-xl);
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.showcase-section h2 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-xl);
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  padding-bottom: var(--spacing-md);
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-lg);
  align-items: center;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-xl);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-xl);
}

.badge-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: center;
}

.loading-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xl);
  align-items: center;
}

.message-showcase {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  max-width: 600px;
}

.message-item {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-end;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-darker);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--neon-blue);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.message-bubble {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  max-width: 70%;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.message-bubble.user {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
}

.message-content {
  margin-bottom: var(--spacing-xs);
  color: var(--text-primary);
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  opacity: 0.7;
  transition: all 0.3s ease;
}

.tooltip-grid {
  display: flex;
  gap: var(--spacing-xl);
  justify-content: center;
}

.animation-grid {
  display: flex;
  gap: var(--spacing-xl);
  align-items: center;
}

.icon-rotate {
  font-size: 2rem;
  color: var(--neon-blue);
  cursor: pointer;
  padding: var(--spacing-md);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--neon-blue);
  margin-bottom: var(--spacing-sm);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .style-showcase {
    padding: var(--spacing-lg);
  }
  
  .showcase-section {
    padding: var(--spacing-lg);
  }
  
  .button-grid,
  .status-grid,
  .input-grid,
  .card-grid {
    grid-template-columns: 1fr;
  }
  
  .message-showcase {
    max-width: 100%;
  }
  
  .message-bubble {
    max-width: 85%;
  }
}
</style> 