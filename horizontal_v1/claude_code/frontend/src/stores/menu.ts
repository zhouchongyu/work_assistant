/**
 * Menu store for dynamic menu and routing.
 *
 * Manages:
 * - Dynamic menu tree from API
 * - Route generation from menu
 * - Menu state (collapsed, active)
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { http } from '@/api/request'
import type { RouteRecordRaw } from 'vue-router'

export interface MenuItem {
  id: number
  parentId: number | null
  name: string
  router?: string
  perms?: string
  type: number // 0=directory, 1=menu, 2=permission
  icon?: string
  orderNum: number
  isShow: boolean
  keepAlive: boolean
  children?: MenuItem[]
}

export const useMenuStore = defineStore('menu', () => {
  // State
  const menus = ref<MenuItem[]>([])
  const isCollapsed = ref(false)
  const activeMenu = ref('')

  // Getters
  const visibleMenus = computed(() => {
    return filterVisibleMenus(menus.value)
  })

  // Filter to only show visible menus (type 0 or 1, isShow true)
  function filterVisibleMenus(items: MenuItem[]): MenuItem[] {
    return items
      .filter(item => item.isShow && item.type !== 2)
      .map(item => ({
        ...item,
        children: item.children ? filterVisibleMenus(item.children) : undefined,
      }))
      .sort((a, b) => a.orderNum - b.orderNum)
  }

  // Actions
  async function fetchMenus() {
    const data = await http.post('/v1/comm/menu')
    menus.value = buildMenuTree(data || [])
    return menus.value
  }

  // Build menu tree from flat list
  function buildMenuTree(items: MenuItem[]): MenuItem[] {
    const map = new Map<number, MenuItem>()
    const roots: MenuItem[] = []

    // First pass: create map
    items.forEach(item => {
      map.set(item.id, { ...item, children: [] })
    })

    // Second pass: build tree
    items.forEach(item => {
      const node = map.get(item.id)!
      if (item.parentId && map.has(item.parentId)) {
        const parent = map.get(item.parentId)!
        parent.children = parent.children || []
        parent.children.push(node)
      } else {
        roots.push(node)
      }
    })

    return roots
  }

  // Generate routes from menus
  function generateRoutes(): RouteRecordRaw[] {
    const routes: RouteRecordRaw[] = []

    function traverse(items: MenuItem[]) {
      items.forEach(item => {
        if (item.type === 1 && item.router) {
          // Menu item with route
          const route: RouteRecordRaw = {
            path: item.router,
            name: item.name,
            meta: {
              title: item.name,
              icon: item.icon,
              keepAlive: item.keepAlive,
              perms: item.perms,
            },
            // Dynamic import based on router path
            component: () => resolveComponent(item.router!),
          }
          routes.push(route)
        }

        if (item.children?.length) {
          traverse(item.children)
        }
      })
    }

    traverse(menus.value)
    return routes
  }

  // Resolve component path
  function resolveComponent(router: string) {
    // Remove leading slash if present
    const path = router.startsWith('/') ? router.slice(1) : router

    // Import from views directory
    const modules = import.meta.glob('@/views/**/*.vue')
    const componentPath = `/src/views/${path}.vue`

    if (modules[componentPath]) {
      return modules[componentPath]
    }

    // Try with index.vue
    const indexPath = `/src/views/${path}/index.vue`
    if (modules[indexPath]) {
      return modules[indexPath]
    }

    // Fallback to 404
    return () => import('@/views/error/404.vue')
  }

  function toggleCollapse() {
    isCollapsed.value = !isCollapsed.value
  }

  function setActiveMenu(path: string) {
    activeMenu.value = path
  }

  return {
    // State
    menus,
    isCollapsed,
    activeMenu,

    // Getters
    visibleMenus,

    // Actions
    fetchMenus,
    generateRoutes,
    toggleCollapse,
    setActiveMenu,
  }
})
