<!-- frontend/src/components/CommonTable.vue -->
<template>
  <div class="common-table">
    <el-table
      :data="data"
      :loading="loading"
      :row-key="rowKey"
      v-bind="$attrs"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="selectable"
        type="selection"
        width="55"
        :reserve-selection="true"
      />
      
      <!-- 操作列 -->
      <el-table-column
        v-if="hasActions"
        :label="actionColumnLabel"
        :width="actionColumnWidth"
        fixed="right"
        align="center"
      >
        <template #default="{ row }">
          <slot name="actions" :row="row">
            <el-button
              v-if="showEditButton"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="showDeleteButton"
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </slot>
        </template>
      </el-table-column>
      
      <!-- 默认插槽，用于自定义列 -->
      <slot />
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-if="pagination"
      class="pagination"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElTable, ElTableColumn, ElPagination, ElButton } from 'element-plus';

// 定义props
interface Props {
  data: Array<any>;
  loading?: boolean;
  rowKey?: string;
  selectable?: boolean;
  hasActions?: boolean;
  actionColumnLabel?: string;
  actionColumnWidth?: number;
  showEditButton?: boolean;
  showDeleteButton?: boolean;
  pagination?: boolean;
  currentPage?: number;
  pageSize?: number;
  total?: number;
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  rowKey: 'id',
  selectable: false,
  hasActions: true,
  actionColumnLabel: '操作',
  actionColumnWidth: 150,
  showEditButton: true,
  showDeleteButton: true,
  pagination: true,
  currentPage: 1,
  pageSize: 10,
  total: 0
});

// 定义emits
const emits = defineEmits([
  'selection-change',
  'sort-change',
  'size-change',
  'current-change',
  'edit',
  'delete'
]);

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  emits('selection-change', selection);
};

// 处理排序变化
const handleSortChange = (sort: any) => {
  emits('sort-change', sort);
};

// 处理页面大小变化
const handleSizeChange = (size: number) => {
  emits('size-change', size);
};

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  emits('current-change', page);
};

// 处理编辑
const handleEdit = (row: any) => {
  emits('edit', row);
};

// 处理删除
const handleDelete = (row: any) => {
  emits('delete', row);
};
</script>

<style scoped>
.common-table {
  margin: 1rem 0;
}

.pagination {
  margin-top: 1rem;
  text-align: right;
}
</style>