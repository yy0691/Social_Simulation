import { createRouter, createWebHistory } from 'vue-router'
import GameMain from '../views/GameMain.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'game',
      component: GameMain,
      meta: {
        title: 'AI社群模拟小游戏'
      }
    },
    {
      path: '/community',
      name: 'community',
      component: GameMain,
      meta: {
        title: '社群中心'
      }
    },
    {
      path: '/chat',
      name: 'chat', 
      component: GameMain,
      meta: {
        title: '聊天室'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: GameMain,
      meta: {
        title: '设置'
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router 