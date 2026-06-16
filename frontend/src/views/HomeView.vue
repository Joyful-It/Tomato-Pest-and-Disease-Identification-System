<!--
文件名: HomeView.vue
功能描述: 首页组件，提供图片上传和文字输入功能
作者: ZT
日期: 2026/6/16
-->

<template>
  <div class="home-view">
    <!-- 欢迎区域 -->
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold text-success">
        <i class="bi bi-flower1"></i> 番茄病虫害智能诊断
      </h1>
      <p class="lead text-muted">
        上传番茄图片或描述症状，AI 助手为您提供专业的防治建议
      </p>
    </div>

    <!-- 诊断表单 -->
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h5 class="card-title mb-4">
              <i class="bi bi-pencil-square"></i> 开始诊断
            </h5>

            <!-- 图片上传区域 -->
            <div class="mb-4">
              <label class="form-label fw-bold">上传图片（可选）</label>
              <div
                class="upload-area border rounded p-4 text-center"
                :class="{ 'border-success': imagePreview }"
                @click="triggerFileInput"
                @dragover.prevent
                @drop.prevent="handleDrop"
              >
                <div v-if="!imagePreview">
                  <i class="bi bi-cloud-arrow-up fs-1 text-muted"></i>
                  <p class="mt-2 mb-0 text-muted">
                    点击或拖拽图片到此处上传
                  </p>
                  <small class="text-muted">支持 JPG、PNG、BMP、WebP 格式，最大 10MB</small>
                </div>
                <div v-else>
                  <img :src="imagePreview" class="img-fluid rounded" style="max-height: 300px;" alt="预览">
                  <p class="mt-2 mb-0 text-success">
                    <i class="bi bi-check-circle"></i> 图片已选择
                  </p>
                </div>
              </div>
              <input
                ref="fileInput"
                type="file"
                class="d-none"
                accept="image/*"
                @change="handleFileSelect"
              >
            </div>

            <!-- 文字输入区域 -->
            <div class="mb-4">
              <label class="form-label fw-bold">描述症状（可选）</label>
              <textarea
                v-model="textInput"
                class="form-control"
                rows="4"
                placeholder="请描述番茄的症状，例如：叶子出现黄色斑点，有腐烂迹象..."
              ></textarea>
            </div>

            <!-- 位置信息 -->
            <div class="mb-4">
              <label class="form-label fw-bold">位置信息</label>
              <div class="input-group">
                <input
                  v-model="locationInput"
                  type="text"
                  class="form-control"
                  placeholder="输入位置（如：北京市海淀区）或点击定位按钮"
                >
                <button
                  class="btn btn-outline-success"
                  type="button"
                  @click="getCurrentLocation"
                  :disabled="locating"
                >
                  <i class="bi bi-geo-alt"></i>
                  {{ locating ? '定位中...' : '自动定位' }}
                </button>
              </div>
              <small class="text-muted">
                位置信息用于土壤分析和天气查询，可选填
              </small>
            </div>

            <!-- 提交按钮 -->
            <div class="d-grid">
              <button
                class="btn btn-success btn-lg"
                @click="submitDiagnosis"
                :disabled="loading || (!imageFile && !textInput)"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-search me-2"></i>
                {{ loading ? '诊断中...' : '开始诊断' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能介绍 -->
    <div class="row mt-5">
      <div class="col-md-4 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-camera fs-1 text-success"></i>
            <h5 class="mt-3">图片识别</h5>
            <p class="text-muted">上传番茄图片，AI 自动识别病虫害类型</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-chat-dots fs-1 text-success"></i>
            <h5 class="mt-3">智能分析</h5>
            <p class="text-muted">多维度分析，提供综合防治建议</p>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center">
            <i class="bi bi-calendar-check fs-1 text-success"></i>
            <h5 class="mt-3">农事提醒</h5>
            <p class="text-muted">生成种植日历，智能农事提醒</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 首页组件
 * 提供图片上传、文字输入和位置定位功能
 */
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      imageFile: null,
      imagePreview: null,
      textInput: '',
      locationInput: '',
      latitude: null,
      longitude: null,
      locating: false,
      loading: false
    }
  },
  methods: {
    /**
     * 触发文件选择
     */
    triggerFileInput() {
      this.$refs.fileInput.click()
    },

    /**
     * 处理文件选择
     */
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.setImage(file)
      }
    },

    /**
     * 处理拖拽上传
     */
    handleDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.setImage(file)
      }
    },

    /**
     * 设置图片文件
     */
    setImage(file) {
      // 验证文件大小
      if (file.size > 10 * 1024 * 1024) {
        alert('图片大小不能超过 10MB')
        return
      }

      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
    },

    /**
     * 获取当前位置
     */
    async getCurrentLocation() {
      this.locating = true

      try {
        // 尝试使用浏览器定位
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              this.latitude = position.coords.latitude
              this.longitude = position.coords.longitude
              // 直接使用经纬度作为位置，不调用反向地理编码
              this.locationInput = `${this.latitude.toFixed(4)}, ${this.longitude.toFixed(4)}`
              this.locating = false
            },
            (error) => {
              console.error('定位失败:', error)
              alert('定位失败，请手动输入位置')
              this.locating = false
            },
            {
              timeout: 10000,  // 10秒超时
              maximumAge: 300000  // 5分钟内缓存有效
            }
          )
        } else {
          alert('浏览器不支持定位功能，请手动输入位置')
          this.locating = false
        }
      } catch (error) {
        console.error('定位错误:', error)
        this.locating = false
      }
    },

    /**
     * 提交诊断请求
     */
    async submitDiagnosis() {
      if (!this.imageFile && !this.textInput) {
        alert('请上传图片或输入症状描述')
        return
      }

      this.loading = true

      try {
        // 创建 FormData
        const formData = new FormData()

        if (this.imageFile) {
          formData.append('file', this.imageFile)
        }

        // 添加其他参数
        const requestData = {
          text_input: this.textInput || null,
          latitude: this.latitude,
          longitude: this.longitude,
          location: this.locationInput || null
        }

        formData.append('request', JSON.stringify(requestData))

        // 发送请求
        const response = await axios.post('/api/diagnosis', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          // 跳转到结果页面
          this.$router.push({
            name: 'Result',
            params: { id: response.data.diagnosis_id }
          })
        } else {
          alert('诊断失败：' + (response.data.error || '未知错误'))
        }
      } catch (error) {
        console.error('诊断请求失败:', error)
        alert('诊断请求失败，请稍后重试')
      } finally {
        this.loading = false
      }
    }
  },
  beforeUnmount() {
    // 清理预览 URL
    if (this.imagePreview) {
      URL.revokeObjectURL(this.imagePreview)
    }
  }
}
</script>

<style scoped>
.upload-area {
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #198754 !important;
  background-color: #f0fff0;
}

.upload-area.border-success {
  background-color: #f0fff0;
}
</style>
