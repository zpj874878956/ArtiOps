import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(router).use(pinia).use(ElementPlus)

app.mount('#app') 