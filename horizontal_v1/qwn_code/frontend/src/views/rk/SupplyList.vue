<!-- frontend/src/views/rk/SupplyList.vue -->
<template>
  <div class="supply-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>简历管理</span>
          <el-button type="primary" @click="handleCreate">新增</el-button>
        </div>
      </template>
      
      <el-form :model="queryForm" inline class="query-form">
        <el-form-item label="简历名称">
          <el-input v-model="queryForm.name" placeholder="请输入简历名称" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="queryForm.vendorId" placeholder="请选择供应商">
            <el-option label="供应商A" value="1" />
            <el-option label="供应商B" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <CommonTable
        :data="supplyList"
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
        <el-table-column prop="name" label="简历名称" show-overflow-tooltip />
        <el-table-column prop="vendorName" label="供应商" />
        <el-table-column prop="fileName" label="文件名" show-overflow-tooltip />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="analysisStatus" label="分析状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.analysisStatus)">
              {{ getStatusText(row.analysisStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handlePreview(row)">预览</el-button>
            <el-button size="small" type="primary" @click="handleAnalysis(row)">分析</el-button>
          </template>
        </el-table-column>
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
  ElSelect, 
  ElOption, 
  ElButton, 
  ElMessage,
  ElMessageBox,
  ElTag
} from 'element-plus';
import CommonTable from '@/components/CommonTable.vue';
import { supplyApi } from '@/api';

// 路由
const router = useRouter();

// 查询表单
const queryForm = reactive({
  name: '',
  vendorId: ''
});

// 分页数据
const supplyList = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

// 获取简历列表
const getSupplyList = async () => {
  loading.value = true;
  
  try {
    // 这里应该调用API获取简历列表
    // 示例伪代码：
    // const response = await supplyApi.getSupplyList({
    //   page: currentPage.value,
    //   size: pageSize.value,
    //   ...queryForm
    // });
    // supplyList.value = response.data.items;
    // total.value = response.data.total;
    
    // 模拟数据
    supplyList.value = [
      {
        id: 1,
        name: '张三的简历',
        vendorName: '供应商A',
        fileName: 'zhangsan_resume.pdf',
        version: 1,
        analysisStatus: 'DONE',
        createdAt: '2023-01-01 10:00:00'
      },
      {
        id: 2,
        name: '李四的简历',
        vendorName: '供应商B',
        fileName: 'lisi_resume.docx',
        version: 1,
        analysisStatus: 'ANALYZING',
        createdAt: '2023-01-02 11:00:00'
      }
    ];
    total.value = 2;
  } catch (error) {
    console.error('获取简历列表失败:', error);
    ElMessage.error('获取简历列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'INIT':
      return 'info';
    case 'ANALYZING':
      return 'warning';
    case 'DONE':
      return 'success';
    case 'ERROR':
      return 'danger';
    default:
      return 'info';
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'INIT':
      return '初始';
    case 'ANALYZING':
      return '分析中';
    case 'DONE':
      return '已完成';
    case 'ERROR':
      return '错误';
    default:
      return status;
  }
};

// 查询
const handleQuery = () => {
  currentPage.value = 1;
  getSupplyList();
};

// 重置
const handleReset = () => {
  queryForm.name = '';
  queryForm.vendorId = '';
  currentPage.value = 1;
  getSupplyList();
};

// 分页变化
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  getSupplyList();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  getSupplyList();
};

// 新增
const handleCreate = () => {
  router.push('/rk/supply/create');
};

// 编辑
const handleEdit = (row: any) => {
  router.push(`/rk/supply/${row.id}/edit`);
};

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除简历 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    // 这里应该调用API删除简历
    // 示例伪代码：
    // await supplyApi.deleteSupply(row.id);
    // ElMessage.success('删除成功');
    // getSupplyList(); // 刷新列表
    
    ElMessage.success('删除成功（模拟）');
    getSupplyList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除简历失败:', error);
      ElMessage.error('删除简历失败');
    }
  }
};

// 预览
const handlePreview = (row: any) => {
  // 实现预览逻辑
  ElMessage.info(`预览简历: ${row.name}（模拟）`);
};

// 分析
const handleAnalysis = async (row: any) => {
  try {
    // 这里应该调用API触发分析
    // 示例伪代码：
    // const response = await supplyApi.triggerSupplyAnalysis({ supplyId: row.id });
    // if (response.data.success) {
    //   ElMessage.success('分析已触发');
    //   getSupplyList(); // 刷新列表
    // } else {
    //   ElMessage.error(response.data.message);
    // }
    
    ElMessage.success('分析已触发（模拟）');
    // 更新状态为分析中
    const index = supplyList.value.findIndex(item => item.id === row.id);
    if (index !== -1) {
      supplyList.value[index].analysisStatus = 'ANALYZING';
    }
  } catch (error) {
    console.error('触发分析失败:', error);
    ElMessage.error('触发分析失败');
  }
};

// 页面加载时获取数据
onMounted(() => {
  getSupplyList();
});
</script>

<style scoped>
.supply-list-container {
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