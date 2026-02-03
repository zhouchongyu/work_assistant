/**
 * Application entry point.
 *
 * Initializes Vue app with:
 * - Element Plus UI
 * - Pinia state management
 * - Vue Router
 * - Global styles
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { setupPermissionDirective } from './directives/permission'

// Styles
import 'element-plus/dist/index.css'
import './styles/main.scss'

// Create app
const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Setup custom directives
setupPermissionDirective(app)

// Mount app
app.mount('#app')
