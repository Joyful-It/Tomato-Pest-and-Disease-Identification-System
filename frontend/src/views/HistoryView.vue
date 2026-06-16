<!--
文件名: HistoryView.vue
功能描述: 历史记录展示组件
作者: ZT
日期: 2026/6/16
-->

<template>
  <div class="history-view">
    <h2 class="mb-4">
      <i class="bi bi-clock-history"></i> 诊断历史记录
    </h2>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
      <p class="mt-3 text-muted">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="records.length === 0" class="text-center py-5">
      <i class="bi bi-inbox fs-1 text-muted"></i>
      <p class="mt-3 text-muted">暂无诊断记录</p>
      <router-link to="/" class="btn btn-success">
        <i class="bi bi-plus-circle"></i> 开始诊断
      </router-link>
    </div>

    <!-- 记录列表 -->
    <div v-else>
      <div class="row">
        <div v-for="record in records" :key="record.id" class="col-md-6 col-lg-4 mb-4">
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h6 class="card-title mb-0">
                  <span class="badge" :class="record.disease_name === '番茄-健康' ? 'bg-success' : 'bg-warning'">
                    {{ record.disease_name || '未知' }}
                  </span>
                </h6>
                <small class="text-muted">{{ formatDate(record.date) }}</small>
              </div>

              <p class="card-text text-muted small">
                <i class="bi bi-geo-alt"></i> {{ record.location || '未记录位置' }}
              </p>

              <p v-if="record.text_input" class="card-text small">
                {{ truncateText(record.text_input, 50) }}
              </p>

              <router-link
                :to="{ name: 'Result', params: { id: record.id } }"
                class="btn btn-outline-success btn-sm"
              >
                查看详情
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="text-center mt-4">
        <button class="btn btn-outline-success" @click="loadMore" :disabled="loadingMore">
          <span v-if="loadingMore" class="spinner-border spinner-border-sm me-2"></span>
          加载更多
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 历史记录展示组件
 * 显示用户的诊断历史列表
 */
import axios from 'axios'

export default {
  name: 'HistoryView',
  data() {
    return {
      records: [],
      loading: true,
      loadingMore: false,
      hasMore: true,
      limit: 12
    }
  },
  async created() {
    await this.loadHistory()
  },
  methods: {
    /**
     * 加载历史记录
     */
    async loadHistory() {
      try {
        const response = await axios.get(`/api/history?limit=${this.limit}`)

        if (response.data.success) {
          this.records = response.data.records
          this.hasMore = response.data.records.length >= this.limit
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载更多记录
     */
    async loadMore() {
      this.loadingMore = true

      try {
        this.limit += 12
        await this.loadHistory()
      } finally {
        this.loadingMore = false
      }
    },

    /**
     * 格式化日期
     */
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    /**
     * 截断文本
     */
    truncateText(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
