<template>
  <div class="rk-dashboard">
    <h2>招聘管理</h2>
    <el-tabs type="border-card">
      <el-tab-pane label="简历管理">
        <el-button type="primary" @click="createResume">上传简历</el-button>
        <el-table :data="resumes" style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="简历名称" />
          <el-table-column prop="vendorName" label="供应商" />
          <el-table-column prop="uploadTime" label="上传时间" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewResume(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="analyzeResume(scope.row)">分析</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="需求管理">
        <el-button type="primary" @click="createDemand">创建需求</el-button>
        <el-table :data="demands" style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="需求名称" />
          <el-table-column prop="customerName" label="客户" />
          <el-table-column prop="createTime" label="创建时间" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewDemand(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="matchDemand(scope.row)">匹配</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="匹配结果">
        <el-table :data="matches" style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="demandName" label="需求" />
          <el-table-column prop="supplyName" label="简历" />
          <el-table-column prop="score" label="匹配度" />
          <el-table-column prop="matchTime" label="匹配时间" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="viewMatch(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

// 模拟数据
const resumes = ref([
  { id: 1, name: '张三简历', vendorName: '供应商A', uploadTime: '2023-01-01 10:00:00', status: '已分析' },
  { id: 2, name: '李四简历', vendorName: '供应商B', uploadTime: '2023-01-02 11:00:00', status: '分析中' },
  { id: 3, name: '王五简历', vendorName: '供应商C', uploadTime: '2023-01-03 12:00:00', status: '待分析' }
]);

const demands = ref([
  { id: 1, name: 'Java开发工程师', customerName: '客户A', createTime: '2023-01-01 09:00:00', status: '已分析' },
  { id: 2, name: 'Python开发工程师', customerName: '客户B', createTime: '2023-01-02 10:00:00', status: '分析中' }
]);

const matches = ref([
  { id: 1, demandName: 'Java开发工程师', supplyName: '张三简历', score: '95%', matchTime: '2023-01-01 14:00:00' },
  { id: 2, demandName: 'Python开发工程师', supplyName: '李四简历', score: '87%', matchTime: '2023-01-02 15:00:00' }
]);

const getStatusType = (status: string) => {
  switch (status) {
    case '已分析':
      return 'success';
    case '分析中':
      return 'warning';
    case '待分析':
      return 'info';
    default:
      return 'info';
  }
};

const createResume = () => {
  ElMessage.info('上传简历功能');
};

const viewResume = (row: any) => {
  ElMessage.info(`查看简历: ${row.name}`);
};

const analyzeResume = (row: any) => {
  ElMessage.info(`分析简历: ${row.name}`);
};

const createDemand = () => {
  ElMessage.info('创建需求功能');
};

const viewDemand = (row: any) => {
  ElMessage.info(`查看需求: ${row.name}`);
};

const matchDemand = (row: any) => {
  ElMessage.info(`匹配需求: ${row.name}`);
};

const viewMatch = (row: any) => {
  ElMessage.info(`查看匹配详情: ${row.demandName} - ${row.supplyName}`);
};

onMounted(() => {
  console.log('RK dashboard loaded');
});
</script>

<style scoped>
.rk-dashboard {
  padding: 20px;
}

.el-table {
  margin-top: 20px;
}
</style>