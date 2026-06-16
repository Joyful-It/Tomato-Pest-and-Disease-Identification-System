<!--
文件名: ProfileView.vue
功能描述: 用户档案展示组件
作者: ZT
日期: 2026/6/16
-->

<template>
  <div class="profile-view">
    <h2 class="mb-4">
      <i class="bi bi-person"></i> 用户档案
    </h2>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
      <p class="mt-3 text-muted">加载中...</p>
    </div>

    <!-- 用户信息 -->
    <div v-else-if="profile" class="row">
      <!-- 基本信息 -->
      <div class="col-md-4 mb-4">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <div class="mb-3">
              <i class="bi bi-person-circle fs-1 text-success"></i>
            </div>
            <h5>{{ profile.user_info?.username || '默认用户' }}</h5>
            <p class="text-muted">
              <i class="bi bi-geo-alt"></i>
              {{ profile.user_info?.location || '未设置位置' }}
            </p>
            <p class="text-muted small">
              注册时间：{{ profile.user_info?.created_at || '未知' }}
            </p>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="col-md-8 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-bar-chart"></i> 统计信息</h5>
          </div>
          <div class="card-body">
            <div class="row text-center">
              <div class="col-6">
                <div class="display-4 text-success">
                  {{ profile.statistics?.total_diagnoses || 0 }}
                </div>
                <p class="text-muted">诊断次数</p>
              </div>
              <div class="col-6">
                <div class="display-4 text-primary">
                  {{ profile.statistics?.total_memories || 0 }}
                </div>
                <p class="text-muted">记忆条数</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近诊断 -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-clock-history"></i> 最近诊断</h5>
          </div>
          <div class="card-body">
            <div v-if="profile.recent_diagnoses?.length">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>日期</th>
                      <th>诊断结果</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="diagnosis in profile.recent_diagnoses" :key="diagnosis.date">
                      <td>{{ diagnosis.date }}</td>
                      <td>
                        <span class="badge" :class="diagnosis.disease === '番茄-健康' ? 'bg-success' : 'bg-warning'">
                          {{ diagnosis.disease || '未知' }}
                        </span>
                      </td>
                      <td>
                        <router-link to="/history" class="btn btn-outline-success btn-sm">
                          查看详情
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="text-center py-3">
              <p class="text-muted mb-0">暂无诊断记录</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 用户档案展示组件
 * 显示用户信息、统计数据和最近诊断记录
 */
import axios from 'axios'

export default {
  name: 'ProfileView',
  data() {
    return {
      profile: null,
      loading: true
    }
  },
  async created() {
    await this.loadProfile()
  },
  methods: {
    /**
     * 加载用户档案
     */
    async loadProfile() {
      try {
        const response = await axios.get('/api/user/profile')

        if (response.data.success) {
          this.profile = response.data
        }
      } catch (error) {
        console.error('加载用户档案失败:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.display-4 {
  font-weight: bold;
}
</style>
