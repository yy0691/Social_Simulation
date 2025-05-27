<template>
  <div class="particle-background">
    <!-- 星星背景 -->
    <div ref="starsContainer" class="stars-layer"></div>
    
    <!-- 浮动粒子 -->
    <div ref="particlesContainer" class="particles-layer"></div>
    
    <!-- 渐变遮罩 -->
    <div class="gradient-overlay" :style="{ opacity: overlayOpacity }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

interface Props {
  starCount?: number;
  particleCount?: number;
  animationSpeed?: number;
  overlayOpacity?: number;
  theme?: 'dark' | 'light' | 'cosmic';
}

const props = withDefaults(defineProps<Props>(), {
  starCount: 100,
  particleCount: 50,
  animationSpeed: 1,
  overlayOpacity: 0.1,
  theme: 'dark'
});

const starsContainer = ref<HTMLElement>();
const particlesContainer = ref<HTMLElement>();
const animationFrame = ref<number>();

const stars: Array<{
  element: HTMLElement;
  x: number;
  y: number;
  twinkleDelay: number;
}> = [];

const particles: Array<{
  element: HTMLElement;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  rotation: number;
  rotationSpeed: number;
}> = [];

// 创建星星
const createStars = () => {
  if (!starsContainer.value) return;
  
  for (let i = 0; i < props.starCount; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    const size = Math.random() * 3 + 1;
    const brightness = Math.random() * 0.8 + 0.2;
    const twinkleDelay = Math.random() * 3;
    
    star.style.left = `${x}%`;
    star.style.top = `${y}%`;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.opacity = `${brightness}`;
    star.style.animationDelay = `${twinkleDelay}s`;
    
    // 随机选择星星颜色
    const colors = ['#ffffff', '#00d4ff', '#ff0096', '#ffcc00'];
    star.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    
    starsContainer.value.appendChild(star);
    
    stars.push({
      element: star,
      x,
      y,
      twinkleDelay
    });
  }
};

// 创建粒子
const createParticles = () => {
  if (!particlesContainer.value) return;
  
  for (let i = 0; i < props.particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    const size = Math.random() * 8 + 2;
    const vx = (Math.random() - 0.5) * 0.5 * props.animationSpeed;
    const vy = (Math.random() - 0.5) * 0.5 * props.animationSpeed;
    const rotation = Math.random() * 360;
    const rotationSpeed = (Math.random() - 0.5) * 2 * props.animationSpeed;
    
    particle.style.left = `${x}%`;
    particle.style.top = `${y}%`;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.transform = `rotate(${rotation}deg)`;
    
    // 设置粒子形状和颜色
    const shapes = ['circle', 'diamond', 'triangle'];
    const shape = shapes[Math.floor(Math.random() * shapes.length)];
    particle.classList.add(shape);
    
    particlesContainer.value.appendChild(particle);
    
    particles.push({
      element: particle,
      x,
      y,
      vx,
      vy,
      size,
      rotation,
      rotationSpeed
    });
  }
};

// 动画更新
const updateAnimation = () => {
  // 更新粒子位置
  particles.forEach(particle => {
    particle.x += particle.vx;
    particle.y += particle.vy;
    particle.rotation += particle.rotationSpeed;
    
    // 边界处理
    if (particle.x < 0) particle.x = 100;
    if (particle.x > 100) particle.x = 0;
    if (particle.y < 0) particle.y = 100;
    if (particle.y > 100) particle.y = 0;
    
    // 应用变换
    particle.element.style.left = `${particle.x}%`;
    particle.element.style.top = `${particle.y}%`;
    particle.element.style.transform = `rotate(${particle.rotation}deg)`;
  });
  
  animationFrame.value = requestAnimationFrame(updateAnimation);
};

// 初始化
const init = () => {
  createStars();
  createParticles();
  updateAnimation();
};

// 清理
const cleanup = () => {
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value);
  }
  
  stars.length = 0;
  particles.length = 0;
  
  if (starsContainer.value) {
    starsContainer.value.innerHTML = '';
  }
  
  if (particlesContainer.value) {
    particlesContainer.value.innerHTML = '';
  }
};

onMounted(() => {
  init();
});

onUnmounted(() => {
  cleanup();
});

// 暴露重新初始化方法
const reinitialize = () => {
  cleanup();
  setTimeout(init, 100);
};

defineExpose({
  reinitialize
});
</script>

<style scoped>
.particle-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
  background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
}

.stars-layer,
.particles-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 212, 255, 0.1) 0%,
    rgba(255, 0, 150, 0.05) 50%,
    transparent 100%
  );
  pointer-events: none;
}

/* 星星样式 */
:deep(.star) {
  position: absolute;
  border-radius: 50%;
  background: #ffffff;
  animation: twinkle 3s ease-in-out infinite;
  box-shadow: 0 0 6px currentColor;
}

/* 粒子样式 */
:deep(.particle) {
  position: absolute;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

:deep(.particle.circle) {
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.8) 0%, transparent 70%);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

:deep(.particle.diamond) {
  background: linear-gradient(45deg, rgba(255, 0, 150, 0.8), rgba(255, 204, 0, 0.8));
  transform-origin: center;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  box-shadow: 0 0 8px rgba(255, 0, 150, 0.4);
}

:deep(.particle.triangle) {
  width: 0;
  height: 0;
  background: transparent;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 8px solid rgba(255, 204, 0, 0.8);
  box-shadow: 0 0 6px rgba(255, 204, 0, 0.4);
}

/* 动画 */
@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-10px) rotate(120deg);
  }
  66% {
    transform: translateY(5px) rotate(240deg);
  }
}

/* 主题变体 */
.particle-background.light {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #dee2e6 100%);
}

.particle-background.light .gradient-overlay {
  background: radial-gradient(
    ellipse at center,
    rgba(0, 123, 255, 0.05) 0%,
    rgba(108, 117, 125, 0.03) 50%,
    transparent 100%
  );
}

.particle-background.cosmic {
  background: linear-gradient(135deg, #000428 0%, #004e92 100%);
}

.particle-background.cosmic .gradient-overlay {
  background: radial-gradient(
    ellipse at center,
    rgba(0, 212, 255, 0.15) 0%,
    rgba(138, 43, 226, 0.1) 50%,
    transparent 100%
  );
}

/* 响应式优化 */
@media (max-width: 768px) {
  .particle-background {
    background-attachment: fixed;
  }
  
  :deep(.particle) {
    opacity: 0.4;
  }
  
  :deep(.star) {
    animation-duration: 2s;
  }
}

/* 性能优化：减少移动设备上的动画 */
@media (prefers-reduced-motion: reduce) {
  :deep(.star),
  :deep(.particle) {
    animation: none;
  }
  
  .gradient-overlay {
    animation: none;
  }
}

/* 深色主题适配 */
.dark .particle-background {
  background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
}

.dark :deep(.star) {
  box-shadow: 0 0 8px currentColor;
}

.dark :deep(.particle.circle) {
  background: radial-gradient(circle, rgba(0, 212, 255, 0.9) 0%, transparent 70%);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.6);
}
</style> 