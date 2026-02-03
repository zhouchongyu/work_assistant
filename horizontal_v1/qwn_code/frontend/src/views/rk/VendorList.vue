<!-- frontend/src/views/rk/VendorList.vue -->
<template>
  <div class="vendor-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <el-button type="primary" @click="handleCreate">新增</el-button>
        </div>
      </template>
      
      <el-form :model="queryForm" inline class="query-form">
        <el-form-item label="供应商名称">
          <el-input v-model="queryForm.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="供应商编码">
          <el-input v-model="queryForm.code" placeholder="请输入供应商编码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <CommonTable
        :data="vendorList"
        :loading="loading"
        :total="total"
        :current-page="currentPage"
        :page-size="pageSize"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        @edit="handleEdit"
        @delete="handleDelete"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="供应商名称" />
        <el-table-column prop="code" label="供应商编码" />
        <el-table-column prop="folderId" label="文件夹ID" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="180" />
      </CommonTable>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  ElCard, 
  ElForm, 
  ElFormItem, 
  ElInput, 
  ElButton, 
  ElMessage,
  ElMessageBox
} from 'element-plus';
import CommonTable from '@/components/CommonTable.vue';
import { vendorApi } from '@/api';

// 路由
const router = useRouter();

// 查询表单
const queryForm = reactive({
  name: '',
  code: ''
});

// 分页数据
const vendorList = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 获取供应商列表
const getVendorList = async () => {
  loading.value = true;
  
  try {
    // 这里应该调用API获取供应商列表
    // 示例伪代码：
    // const response = await vendorApi.getVendorList({
    //   page: currentPage.value,
    //   size: pageSize.value,
    //   ...queryForm
    // });
    // vendorList.value = response.data.items;
    // total.value = response.data.total;
    
    // 模拟数据
    vendorList.value = [
      {
        id: 1,
        name: '供应商A',
        code: 'VENDOR_A',
        folderId: 'folder_123',
        description: '这是一个供应商',
        createdAt: '2023-01-01 10:00:00'
      },
      {
        id: 2,
        name: '供应商B',
        code: 'VENDOR_B',
        folderId: 'folder_456',
        description: '另一个供应商',
        createdAt: '2023-01-02 11:00:00'
      }
    ];
    total.value = 2;
  } catch (error) {
    console.error('获取供应商列表失败:', error);
    ElMessage.error('获取供应商列表失败');
  } finally {
    loading.value = false;
  }
};

// 查询
const handleQuery = () => {
  currentPage.value = 1;
  getVendorList();
};

// 重置
const handleReset = () => {
  queryForm.name = '';
  queryForm.code = '';
  currentPage.value = 1;
  getVendorList();
};

// 分页变化
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  getVendorList();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  getVendorList();
};

// 新增
const handleCreate = () => {
  router.push('/rk/vendor/create');
};

// 编辑
const handleEdit = (row: any) => {
  router.push(`/rk/vendor/${row.id}/edit`);
};

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除供应商 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    // 这里应该调用API删除供应商
    // 示例伪代码：
    // await vendorApi.deleteVendor(row.id);
    // ElMessage.success('删除成功');
    // getVendorList(); // 刷新列表
    
    ElMessage.success('删除成功（模拟）');
    getVendorList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除供应商失败:', error);
      ElMessage.error('删除供应商失败');
    }
  }
};

// 页面加载时获取数据
onMounted(() => {
  getVendorList();
});
</script>

<style scoped>
.vendor-list-container {
  padding: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-form {
  margin-bottom: 1rem;
}

.query-form .el-form-item {
  margin-bottom: 1rem;
}
</style>