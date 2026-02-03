/**
 * Permission directive (v-permission).
 *
 * Usage:
 * - v-permission="'rk:supply:add'" - single permission
 * - v-permission="['rk:supply:add', 'rk:supply:edit']" - any permission
 * - v-permission.all="['rk:supply:add', 'rk:supply:edit']" - all permissions
 */
import type { App, Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

function checkPermission(el: HTMLElement, binding: DirectiveBinding) {
  const userStore = useUserStore()
  const { value, modifiers } = binding

  if (!value) return

  let hasPermission = false

  if (typeof value === 'string') {
    // Single permission
    hasPermission = userStore.hasPermission(value)
  } else if (Array.isArray(value)) {
    if (modifiers.all) {
      // All permissions required
      hasPermission = userStore.hasAllPermissions(value)
    } else {
      // Any permission sufficient
      hasPermission = userStore.hasAnyPermission(value)
    }
  }

  if (!hasPermission) {
    // Remove element from DOM
    el.parentNode?.removeChild(el)
  }
}

const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  },
}

export function setupPermissionDirective(app: App) {
  app.directive('permission', permissionDirective)
}

export default permissionDirective
