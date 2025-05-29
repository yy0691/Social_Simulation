import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './styles/variables.css'
import './style.css'
import './styles/animations.css'
import './styles/components.css'
import './styles/chat.css'
import './styles/community.css'
import './styles/settings.css'
import './styles/utilities.css'
import './styles/chat-fixes.css'
import './styles/responsive-enhancements.css'
import './styles/micro-interactions.css'
import './styles/final-enhancements.css'
import './styles/chat-layout-fix.css'
//import './styles/background-fix.css'
//import './styles/chat-header-fix.css'
import App from './App.vue'

// 引入FontAwesome样式
import '@fortawesome/fontawesome-free/css/all.css'

// 创建Vue应用
const app = createApp(App)

// 创建并使用Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 挂载应用
app.mount('#app') 