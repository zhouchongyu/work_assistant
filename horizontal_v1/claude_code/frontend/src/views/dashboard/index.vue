<script setup lang="ts">
/**
 * Dashboard page.
 *
 * Overview of system status and quick access.
 */
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// Statistics
const stats = ref([
  { title: '待处理简历', value: 0, icon: 'Document', color: '#409eff' },
  { title: '进行中案例', value: 0, icon: 'Briefcase', color: '#67c23a' },
  { title: '待跟进需求', value: 0, icon: 'List', color: '#e6a23c' },
  { title: '本月成交', value: 0, icon: 'TrendCharts', color: '#f56c6c' },
])

// Quick actions
const quickActions = [
  { title: '新增简历', icon: 'Plus', route: '/rk/supply/add' },
  { title: '简历管理', icon: 'Document', route: '/rk/supply' },
  { title: '需求管理', icon: 'List', route: '/rk/demand' },
  { title: '案例管理', icon: 'Briefcase', route: '/rk/case' },
]

onMounted(async () => {
  // TODO: Fetch dashboard statistics
})
</script>

<template>
  <div class="dashboard">
    <!-- Welcome section -->
    <div class="welcome-card page-card">
      <div class="welcome-content">
        <h2>欢迎回来，{{ userStore.nickName }}</h2>
        <p>今天是 {{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
      </div>
    </div>

    <!-- Statistics -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
        <div class="stat-card page-card">
          <div class="stat-icon" :style="{ backgroundColor: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Quick actions -->
    <div class="page-card">
      <h3 class="section-title">快捷操作</h3>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" v-for="action in quickActions" :key="action.title">
          <router-link :to="action.route" class="quick-action">
            <el-icon :size="32"><component :is="action.icon" /></el-icon>
            <span>{{ action.title }}</span>
          </router-link>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dashboard {
  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;

    .welcome-content {
      h2 {
        font-size: 24px;
        margin-bottom: 8px;
      }

      p {
        opacity: 0.9;
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      display: flex;
      align-items: center;
      padding: 20px;

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        margin-right: 16px;
      }

      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #303133;
        }

        .stat-title {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: #303133;
  }

  .quick-action {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    text-decoration: none;
    color: #606266;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
      color: #409eff;
      box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
    }

    .el-icon {
      margin-bottom: 8px;
    }

    span {
      font-size: 14px;
    }
  }
}
</style>
