<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>供应商</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">12</div>
            <div class="stat-desc">总计</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>客户</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">8</div>
            <div class="stat-desc">总计</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>简历</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">42</div>
            <div class="stat-desc">总计</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>需求</span>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-number">15</div>
            <div class="stat-desc">总计</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="16">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <div class="activity-list">
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in activities"
                :key="index"
                :timestamp="item.timestamp"
                :type="item.type"
              >
                {{ item.content }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="goToCreateSupply">
              <el-icon><Plus /></el-icon>
              添加简历
            </el-button>
            <el-button type="success" size="large" @click="goToCreateDemand">
              <el-icon><DocumentAdd /></el-icon>
              添加需求
            </el-button>
            <el-button type="warning" size="large" @click="goToChat">
              <el-icon><ChatLineRound /></el-icon>
              AI助手
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { 
  ElRow, 
  ElCol, 
  ElCard, 
  ElTimeline, 
  ElTimelineItem, 
  ElButton,
  ElIcon
} from 'element-plus';
import { 
  Plus, 
  DocumentAdd, 
  ChatLineRound 
} from '@element-plus/icons-vue';

// 路由
const router = useRouter();

// 活动数据
const activities = ref([
  {
    content: '张三上传了新的简历',
    timestamp: '2023-01-01 10:00',
    type: 'primary'
  },
  {
    content: '李四创建了一个新需求',
    timestamp: '2023-01-01 09:30',
    type: 'success'
  },
  {
    content: '王五完成了匹配分析',
    timestamp: '2023-01-01 09:00',
    type: 'warning'
  },
  {
    content: '赵六更新了客户信息',
    timestamp: '2023-01-01 08:30',
    type: 'info'
  }
]);

// 快捷操作
const goToCreateSupply = () => {
  router.push('/rk/supply/create');
};

const goToCreateDemand = () => {
  router.push('/rk/demand/create');
};

const goToChat = () => {
  router.push('/chat');
};
</script>

<style scoped>
.dashboard-container {
  padding: 1rem;
}

.dashboard-row {
  margin-bottom: 1rem;
}

.dashboard-card {
  height: 150px;
}

.card-header {
  font-weight: bold;
}

.card-content {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 0.5rem;
}

.stat-desc {
  color: #909399;
}

.activity-list {
  padding: 1rem 0;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quick-actions .el-button {
  width: 100%;
  justify-content: flex-start;
}

.quick-actions .el-button .el-icon {
  margin-right: 0.5rem;
}
</style>