import { createRouter, createWebHistory } from 'vue-router'
import CommunityView from '../views/CommunityView.vue'
import ChatView from '../views/ChatView.vue'
import InvitationView from '../views/InvitationView.vue'
import SettingsView from '../views/SettingsView.vue'
import StyleShowcase from '../views/StyleShowcase.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'community',
      component: CommunityView,
      meta: {
        title: 'AI社群模拟小游戏 - 社群中心'
      }
    },
    {
      path: '/community',
      name: 'community-redirect',
      redirect: '/'
    },
    {
      path: '/chat',
      name: 'chat', 
      component: ChatView,
      meta: {
        title: 'AI社群模拟小游戏 - 聊天室'
      }
    },
    {
      path: '/invitation',
      name: 'invitation',
      component: InvitationView,
      meta: {
        title: 'AI社群模拟小游戏 - 邀请管理'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: {
        title: 'AI社群模拟小游戏 - 设置'
      }
    },
    {
      path: '/showcase',
      name: 'showcase',
      component: StyleShowcase,
      meta: {
        title: 'AI社群模拟小游戏 - 样式展示'
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