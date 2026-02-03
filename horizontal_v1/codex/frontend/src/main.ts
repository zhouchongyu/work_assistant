import { createApp } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()
setActivePinia(pinia)
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')

