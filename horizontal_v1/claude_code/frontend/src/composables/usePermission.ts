/**
 * Permission composable.
 *
 * Provides permission checking utilities.
 */
import { useUserStore } from '@/stores/user'

export function usePermission() {
  const userStore = useUserStore()

  /**
   * Check if user has a specific permission.
   */
  function hasPermission(permission: string): boolean {
    return userStore.hasPermission(permission)
  }

  /**
   * Check if user has any of the specified permissions.
   */
  function hasAnyPermission(permissions: string[]): boolean {
    return userStore.hasAnyPermission(permissions)
  }

  /**
   * Check if user has all of the specified permissions.
   */
  function hasAllPermissions(permissions: string[]): boolean {
    return userStore.hasAllPermissions(permissions)
  }

  /**
   * Check if user is admin.
   */
  function isAdmin(): boolean {
    return userStore.isAdmin
  }

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin,
  }
}

export default usePermission
