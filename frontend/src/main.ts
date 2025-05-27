import { createApp } from 'vue'
import { createPinia } from 'pinia'
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