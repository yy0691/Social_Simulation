<template>
  <div class="settings-view">
    <div class="page-header">
      <h2>
        <i class="fas fa-cog"></i>
        设置
      </h2>
      <p>个性化您的游戏体验</p>
    </div>
    
    <div class="settings-container glass-panel">
      <div class="coming-soon">
        <i class="fas fa-tools"></i>
        <h3>功能开发中</h3>
        <p>设置页面正在开发中，敬请期待...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 临时简化版本，后续完善设置功能
</script>

<style scoped>
.settings-view {
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

.glass-panel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  text-align: center;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dark .glass-panel {
  background: rgba(45, 55, 72, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.coming-soon i {
  font-size: 4rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.coming-soon h3 {
  font-size: 1.5rem;
  margin: 0 0 1rem 0;
}

.coming-soon p {
  color: #6b7280;
  font-size: 1.1rem;
}
</style> 