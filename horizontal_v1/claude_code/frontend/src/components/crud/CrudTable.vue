<script setup lang="ts">
/**
 * CRUD Table Component.
 *
 * Features:
 * - Automatic data loading
 * - Pagination
 * - Sorting
 * - Selection
 * - Actions column
 */
import { ref, watch, computed } from 'vue'
import type { TableColumnCtx } from 'element-plus'

export interface Column {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: 'left' | 'right' | boolean
  sortable?: boolean | 'custom'
  align?: 'left' | 'center' | 'right'
  formatter?: (row: any, column: any, cellValue: any, index: number) => any
  slot?: string
}

export interface Pagination {
  page: number
  size: number
  total: number
  sizes?: number[]
}

const props = withDefaults(defineProps<{
  data: any[]
  columns: Column[]
  loading?: boolean
  pagination?: Pagination
  selection?: boolean
  rowKey?: string
  height?: number | string
  maxHeight?: number | string
  stripe?: boolean
  border?: boolean
}>(), {
  loading: false,
  selection: false,
  rowKey: 'id',
  stripe: true,
  border: true,
})

const emit = defineEmits<{
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
  (e: 'sort-change', sort: { prop: string; order: string }): void
  (e: 'selection-change', selection: any[]): void
  (e: 'row-click', row: any): void
}>()

const tableRef = ref()
const selectedRows = ref<any[]>([])

// Handle selection change
function handleSelectionChange(selection: any[]) {
  selectedRows.value = selection
  emit('selection-change', selection)
}

// Handle sort change
function handleSortChange({ prop, order }: { prop: string; order: string }) {
  emit('sort-change', { prop, order })
}

// Handle page change
function handlePageChange(page: number) {
  emit('page-change', page)
}

// Handle size change
function handleSizeChange(size: number) {
  emit('size-change', size)
}

// Handle row click
function handleRowClick(row: any) {
  emit('row-click', row)
}

// Clear selection
function clearSelection() {
  tableRef.value?.clearSelection()
}

// Toggle row selection
function toggleRowSelection(row: any, selected?: boolean) {
  tableRef.value?.toggleRowSelection(row, selected)
}

// Get selected rows
function getSelection() {
  return selectedRows.value
}

defineExpose({
  clearSelection,
  toggleRowSelection,
  getSelection,
  tableRef,
})
</script>

<template>
  <div class="crud-table">
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="data"
      :row-key="rowKey"
      :height="height"
      :max-height="maxHeight"
      :stripe="stripe"
      :border="border"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
    >
      <!-- Selection column -->
      <el-table-column
        v-if="selection"
        type="selection"
        width="55"
        align="center"
        fixed="left"
      />

      <!-- Data columns -->
      <el-table-column
        v-for="col in columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :min-width="col.minWidth"
        :fixed="col.fixed"
        :sortable="col.sortable"
        :align="col.align || 'center'"
        :formatter="col.formatter"
        show-overflow-tooltip
      >
        <template v-if="col.slot" #default="scope">
          <slot :name="col.slot" :row="scope.row" :index="scope.$index" />
        </template>
      </el-table-column>

      <!-- Actions column (slot) -->
      <slot name="actions" />
    </el-table>

    <!-- Pagination -->
    <div v-if="pagination" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="pagination.sizes || [10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.crud-table {
  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    padding: 16px 0;
  }
}
</style>
