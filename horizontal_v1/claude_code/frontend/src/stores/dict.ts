/**
 * Dictionary store for cached dictionary data.
 *
 * Manages:
 * - Dictionary data from API
 * - Local caching
 * - Dictionary lookups
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { http } from '@/api/request'

export interface DictItem {
  id: number
  typeId: number
  name: string
  value: string
  orderNum: number
  remark?: string
}

export interface DictType {
  id: number
  name: string
  key: string
  items: DictItem[]
}

const DICT_CACHE_KEY = 'wa_dict_cache'
const DICT_CACHE_TIME_KEY = 'wa_dict_cache_time'
const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes

export const useDictStore = defineStore('dict', () => {
  // State
  const dictMap = ref<Map<string, DictItem[]>>(new Map())
  const loading = ref(false)

  // Load cache from localStorage
  function loadCache() {
    const cacheTime = localStorage.getItem(DICT_CACHE_TIME_KEY)
    if (cacheTime) {
      const elapsed = Date.now() - parseInt(cacheTime, 10)
      if (elapsed < CACHE_DURATION) {
        const cached = localStorage.getItem(DICT_CACHE_KEY)
        if (cached) {
          const data = JSON.parse(cached)
          dictMap.value = new Map(Object.entries(data))
          return true
        }
      }
    }
    return false
  }

  // Save cache to localStorage
  function saveCache() {
    const data: Record<string, DictItem[]> = {}
    dictMap.value.forEach((items, key) => {
      data[key] = items
    })
    localStorage.setItem(DICT_CACHE_KEY, JSON.stringify(data))
    localStorage.setItem(DICT_CACHE_TIME_KEY, Date.now().toString())
  }

  // Fetch all dictionaries
  async function fetchDicts(types?: string[]) {
    if (loading.value) return

    // Try cache first
    if (!types && loadCache()) {
      return
    }

    loading.value = true
    try {
      const data = await http.post('/v1/dict/info/data', {
        types: types || [],
      })

      // Process response - expected format: { typeKey: [items] }
      if (data && typeof data === 'object') {
        Object.entries(data).forEach(([key, items]) => {
          if (Array.isArray(items)) {
            dictMap.value.set(key, items as DictItem[])
          }
        })
        saveCache()
      }
    } finally {
      loading.value = false
    }
  }

  // Get dictionary items by type key
  function getDict(typeKey: string): DictItem[] {
    return dictMap.value.get(typeKey) || []
  }

  // Get dictionary item label by value
  function getDictLabel(typeKey: string, value: string | number): string {
    const items = getDict(typeKey)
    const item = items.find(i => i.value === String(value))
    return item?.name || String(value)
  }

  // Get dictionary item value by label
  function getDictValue(typeKey: string, label: string): string {
    const items = getDict(typeKey)
    const item = items.find(i => i.name === label)
    return item?.value || ''
  }

  // Clear cache
  function clearCache() {
    dictMap.value.clear()
    localStorage.removeItem(DICT_CACHE_KEY)
    localStorage.removeItem(DICT_CACHE_TIME_KEY)
  }

  return {
    // State
    dictMap,
    loading,

    // Actions
    fetchDicts,
    getDict,
    getDictLabel,
    getDictValue,
    clearCache,
  }
})
