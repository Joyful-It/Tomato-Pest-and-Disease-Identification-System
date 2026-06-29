<!--
文件名: HomeView.vue
功能描述: 首页组件，提供图片上传、文字输入和天气显示
作者: ZT
日期: 2026/6/16
-->

<template>
  <div class="home-view">
    <!-- 欢迎区域 -->
    <div class="hero-section text-center mb-4">
      <h1 class="display-5 fw-bold">
        <i class="bi bi-flower1 text-success"></i> 番茄病虫害智能诊断
      </h1>
      <p class="lead text-muted">上传图片或描述症状，AI 助手为您提供专业的防治建议</p>
    </div>

    <!-- 主内容区域 - 左右布局 -->
    <div class="row">
      <!-- 左侧：诊断输入 -->
      <div class="col-lg-7">
        <!-- 诊断方式选择 -->
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-tools"></i> 选择诊断方式</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <div
                  class="diagnosis-option p-3 border rounded text-center cursor-pointer h-100"
                  :class="{ 'border-success bg-light': diagnosisMode === 'image' }"
                  @click="diagnosisMode = 'image'"
                >
                  <i class="bi bi-camera fs-1 text-success"></i>
                  <h6 class="mt-2 mb-0">图片诊断</h6>
                  <small class="text-muted">上传病害图片</small>
                </div>
              </div>
              <div class="col-md-4">
                <div
                  class="diagnosis-option p-3 border rounded text-center cursor-pointer h-100"
                  :class="{ 'border-success bg-light': diagnosisMode === 'text' }"
                  @click="diagnosisMode = 'text'"
                >
                  <i class="bi bi-chat-text fs-1 text-primary"></i>
                  <h6 class="mt-2 mb-0">文字描述</h6>
                  <small class="text-muted">描述症状特征</small>
                </div>
              </div>
              <div class="col-md-4">
                <div
                  class="diagnosis-option p-3 border rounded text-center cursor-pointer h-100"
                  :class="{ 'border-success bg-light': diagnosisMode === 'both' }"
                  @click="diagnosisMode = 'both'"
                >
                  <i class="bi bi-layers fs-1 text-warning"></i>
                  <h6 class="mt-2 mb-0">综合诊断</h6>
                  <small class="text-muted">图片+文字</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 图片上传区域 -->
        <div class="card shadow-sm mb-4" v-if="diagnosisMode === 'image' || diagnosisMode === 'both'">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="bi bi-image"></i> 上传番茄图片</h6>
          </div>
          <div class="card-body">
            <div
              class="upload-area border rounded p-4 text-center"
              :class="{ 'border-success bg-light-green': imagePreview }"
              @click="triggerFileInput"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <div v-if="!imagePreview">
                <i class="bi bi-cloud-arrow-up fs-1 text-success"></i>
                <p class="mt-2 mb-0 fw-bold">点击或拖拽图片到此处</p>
                <small class="text-muted">支持 JPG、PNG、BMP、WebP 格式，最大 10MB</small>
              </div>
              <div v-else>
                <img :src="imagePreview" class="img-fluid rounded" style="max-height: 250px;" alt="预览">
                <p class="mt-2 mb-0 text-success fw-bold">
                  <i class="bi bi-check-circle"></i> 图片已选择
                </p>
                <button class="btn btn-sm btn-outline-danger mt-2" @click.stop="clearImage">
                  <i class="bi bi-x"></i> 移除图片
                </button>
              </div>
            </div>
            <input ref="fileInput" type="file" class="d-none" accept="image/*" @change="handleFileSelect">
          </div>
        </div>

        <!-- 文字输入区域 -->
        <div class="card shadow-sm mb-4" v-if="diagnosisMode === 'text' || diagnosisMode === 'both'">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="bi bi-pencil-square"></i> 描述症状</h6>
          </div>
          <div class="card-body">
            <textarea
              v-model="textInput"
              class="form-control form-control-lg"
              rows="5"
              placeholder="请详细描述番茄的症状，例如：&#10;- 叶子出现黄色斑点，边缘枯萎&#10;- 果实表面有腐烂迹象&#10;- 茎秆出现变色..."
            ></textarea>
            <div class="mt-2">
              <small class="text-muted">常见症状：</small>
              <span
                v-for="symptom in commonSymptoms"
                :key="symptom"
                class="badge bg-light text-dark me-1 mb-1 cursor-pointer symptom-tag"
                @click="addSymptom(symptom)"
              >
                {{ symptom }}
              </span>
            </div>
          </div>
        </div>

        <!-- 位置信息 -->
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="bi bi-geo-alt"></i> 位置信息</h6>
          </div>
          <div class="card-body">
            <div class="input-group">
              <input
                v-model="locationInput"
                type="text"
                class="form-control"
                placeholder="输入位置或点击自动定位"
              >
              <button
                class="btn btn-outline-success"
                type="button"
                @click="getCurrentLocation"
                :disabled="locating"
              >
                <i class="bi bi-geo-alt-fill"></i>
                {{ locating ? '定位中...' : '自动定位' }}
              </button>
            </div>
            <small class="text-muted">位置信息用于天气查询和土壤分析</small>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="d-grid mb-4">
          <button
            class="btn btn-success btn-lg py-3"
            @click="submitDiagnosis"
            :disabled="loading || !canSubmit"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-search-heart me-2"></i>
            {{ loading ? '正在诊断...' : '开始诊断' }}
          </button>
        </div>
      </div>

      <!-- 右侧：天气信息 -->
      <div class="col-lg-5">
        <!-- 天气卡片 -->
        <div class="card shadow-sm mb-4 weather-card" v-if="weatherData && weatherData.success">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0"><i class="bi bi-cloud-sun"></i> 当地天气</h5>
          </div>
          <div class="card-body">
            <!-- 今日天气 -->
            <div class="text-center mb-3">
              <i :class="getWeatherIcon(weatherData.today?.skycon)" class="display-3"></i>
              <h3 class="mt-2 mb-0">{{ weatherData.today?.description }}</h3>
              <p class="text-muted">{{ weatherData.today?.date }}</p>
            </div>

            <div class="row text-center mb-3">
              <div class="col-4">
                <div class="p-2 border rounded">
                  <div class="fs-3 fw-bold text-danger">{{ weatherData.today?.temperature?.max?.toFixed(0) }}°C</div>
                  <small class="text-muted">最高温</small>
                </div>
              </div>
              <div class="col-4">
                <div class="p-2 border rounded">
                  <div class="fs-3 fw-bold text-primary">{{ weatherData.today?.temperature?.min?.toFixed(0) }}°C</div>
                  <small class="text-muted">最低温</small>
                </div>
              </div>
              <div class="col-4">
                <div class="p-2 border rounded">
                  <div class="fs-3 fw-bold text-info">{{ weatherData.today?.humidity?.avg?.toFixed(0) }}%</div>
                  <small class="text-muted">湿度</small>
                </div>
              </div>
            </div>

            <!-- 农事建议 -->
            <div class="alert alert-success mb-3" v-if="farmingAdvice">
              <i class="bi bi-lightbulb"></i> {{ farmingAdvice }}
            </div>

            <!-- 未来预报 -->
            <h6 class="text-muted mb-2">未来预报</h6>
            <div class="row g-2">
              <div v-for="(day, index) in weatherData.forecast" :key="index" class="col text-center">
                <div class="p-2 border rounded bg-light">
                  <div class="fw-bold small">{{ index === 0 ? '今天' : index === 1 ? '明天' : '后天' }}</div>
                  <i :class="getWeatherIcon(day.skycon)" class="fs-5"></i>
                  <div class="small">{{ day.description }}</div>
                  <div class="small">
                    <span class="text-danger">{{ day.temperature?.max?.toFixed(0) }}°</span>
                    <span class="text-muted">/</span>
                    <span class="text-primary">{{ day.temperature?.min?.toFixed(0) }}°</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 定位提示 -->
        <div class="card shadow-sm mb-4" v-if="!weatherData">
          <div class="card-body text-center py-5">
            <i class="bi bi-geo-alt fs-1 text-muted"></i>
            <h5 class="mt-3 text-muted">请先定位获取天气</h5>
            <p class="text-muted">点击左侧"自动定位"按钮</p>
          </div>
        </div>

        <!-- 使用提示 -->
        <div class="card shadow-sm">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="bi bi-info-circle"></i> 使用提示</h6>
          </div>
          <div class="card-body">
            <div class="d-flex mb-3">
              <i class="bi bi-check-circle-fill text-success me-2 mt-1"></i>
              <div>
                <strong>清晰拍摄</strong>
                <p class="mb-0 small text-muted">请在光线充足的环境下拍摄病害部位</p>
              </div>
            </div>
            <div class="d-flex mb-3">
              <i class="bi bi-check-circle-fill text-success me-2 mt-1"></i>
              <div>
                <strong>详细描述</strong>
                <p class="mb-0 small text-muted">描述症状出现的时间、部位和变化过程</p>
              </div>
            </div>
            <div class="d-flex mb-3">
              <i class="bi bi-check-circle-fill text-success me-2 mt-1"></i>
              <div>
                <strong>准确定位</strong>
                <p class="mb-0 small text-muted">提供位置信息可获得更精准的天气和土壤分析</p>
              </div>
            </div>
            <div class="d-flex">
              <i class="bi bi-check-circle-fill text-success me-2 mt-1"></i>
              <div>
                <strong>综合诊断</strong>
                <p class="mb-0 small text-muted">图片+文字描述可获得更准确的诊断结果</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 首页组件
 * 提供图片上传、文字输入和天气显示功能
 */
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      diagnosisMode: 'both', // image, text, both
      imageFile: null,
      imagePreview: null,
      textInput: '',
      locationInput: '',
      latitude: null,
      longitude: null,
      locating: false,
      loading: false,
      weatherData: null,
      commonSymptoms: ['黄叶', '枯萎', '斑点', '腐烂', '卷叶', '虫蛀', '变色', '脱落']
    }
  },
  computed: {
    /**
     * 判断是否可以提交
     */
    canSubmit() {
      if (this.diagnosisMode === 'image') return !!this.imageFile
      if (this.diagnosisMode === 'text') return !!this.textInput.trim()
      if (this.diagnosisMode === 'both') return !!this.imageFile || !!this.textInput.trim()
      return false
    },

    /**
     * 根据天气生成农事建议
     */
    farmingAdvice() {
      if (!this.weatherData || !this.weatherData.today) return ''

      const today = this.weatherData.today
      const temp = today.temperature?.avg || 0
      const humidity = today.humidity?.avg || 0
      const skycon = today.skycon || ''

      if (skycon.includes('RAIN')) {
        return '今日有雨，不宜施药，注意排水防涝'
      }
      if (temp > 35) {
        return '高温天气，注意遮阳降温，避免中午浇水'
      }
      if (temp < 10) {
        return '温度较低，注意防寒保暖'
      }
      if (humidity > 80) {
        return '湿度较高，注意通风，预防病害发生'
      }
      return '天气适宜，适合进行田间管理'
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
      if (file) this.setImage(file)
    },

    /**
     * 处理拖拽上传
     */
    handleDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) this.setImage(file)
    },

    /**
     * 设置图片文件
     */
    setImage(file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('图片大小不能超过 10MB')
        return
      }
      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
    },

    /**
     * 清除图片
     */
    clearImage() {
      this.imageFile = null
      if (this.imagePreview) URL.revokeObjectURL(this.imagePreview)
      this.imagePreview = null
    },

    /**
     * 添加常见症状到输入框
     */
    addSymptom(symptom) {
      if (this.textInput) {
        this.textInput += '，' + symptom
      } else {
        this.textInput = symptom
      }
    },

    /**
     * 获取当前位置
     */
    async getCurrentLocation() {
      this.locating = true

      try {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            async (position) => {
              this.latitude = position.coords.latitude
              this.longitude = position.coords.longitude
              this.locationInput = `${this.latitude.toFixed(4)}, ${this.longitude.toFixed(4)}`

              // 获取天气数据
              await this.loadWeather()

              this.locating = false
            },
            (error) => {
              console.error('定位失败:', error)
              alert('定位失败，请手动输入位置')
              this.locating = false
            },
            {
              timeout: 10000,
              maximumAge: 300000
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
     * 加载天气数据
     */
    async loadWeather() {
      if (!this.latitude || !this.longitude) {
        console.log('缺少经纬度，无法加载天气')
        return
      }

      console.log('正在加载天气数据:', this.latitude, this.longitude)

      try {
        const url = `/api/weather/${this.latitude}/${this.longitude}`
        console.log('请求 URL:', url)

        const response = await axios.get(url)
        console.log('天气 API 响应:', response.data)

        if (response.data && response.data.success) {
          this.weatherData = response.data
          console.log('天气数据加载成功:', this.weatherData)
        } else {
          console.error('天气数据返回失败:', response.data)
        }
      } catch (error) {
        console.error('加载天气失败:', error)
        if (error.response) {
          console.error('错误响应:', error.response.data)
        }
      }
    },

    /**
     * 获取天气图标
     */
    getWeatherIcon(skycon) {
      const icons = {
        'CLEAR_DAY': 'bi bi-sun text-warning',
        'CLEAR_NIGHT': 'bi bi-moon text-primary',
        'PARTLY_CLOUDY_DAY': 'bi bi-cloud-sun text-info',
        'PARTLY_CLOUDY_NIGHT': 'bi bi-cloud-moon text-primary',
        'CLOUDY': 'bi bi-cloud text-secondary',
        'LIGHT_HAZE': 'bi bi-cloud-haze text-secondary',
        'MODERATE_HAZE': 'bi bi-cloud-haze text-secondary',
        'HEAVY_HAZE': 'bi bi-cloud-haze text-dark',
        'LIGHT_RAIN': 'bi bi-cloud-drizzle text-info',
        'MODERATE_RAIN': 'bi bi-cloud-rain text-primary',
        'HEAVY_RAIN': 'bi bi-cloud-rain-heavy text-primary',
        'STORM_RAIN': 'bi bi-cloud-lightning-rain text-dark',
        'FOG': 'bi bi-cloud-fog text-secondary',
        'LIGHT_SNOW': 'bi bi-cloud-snow text-info',
        'MODERATE_SNOW': 'bi bi-cloud-snow text-primary',
        'HEAVY_SNOW': 'bi bi-cloud-snow text-dark',
        'STORM_SNOW': 'bi bi-cloud-snow text-dark',
        'WIND': 'bi bi-wind text-info'
      }
      return icons[skycon] || 'bi bi-cloud text-secondary'
    },

    /**
     * 提交诊断请求
     */
    async submitDiagnosis() {
      if (!this.canSubmit) {
        alert('请上传图片或输入症状描述')
        return
      }

      this.loading = true

      try {
        const formData = new FormData()

        if (this.imageFile) {
          formData.append('file', this.imageFile)
        }

        formData.append('text_input', this.textInput || '')
        if (this.latitude) formData.append('latitude', this.latitude)
        if (this.longitude) formData.append('longitude', this.longitude)
        if (this.locationInput) formData.append('location', this.locationInput)

        const response = await axios.post('/api/diagnosis', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (response.data.success) {
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
    if (this.imagePreview) URL.revokeObjectURL(this.imagePreview)
  }
}
</script>

<style scoped>
.hero-section {
  padding: 2rem 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e9 100%);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.diagnosis-option {
  transition: all 0.3s ease;
  cursor: pointer;
}

.diagnosis-option:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.upload-area {
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #198754 !important;
  background-color: #f0fff0;
}

.upload-area.border-success {
  background-color: #f0fff0;
}

.bg-light-green {
  background-color: #f0fff0 !important;
}

.weather-card {
  position: sticky;
  top: 20px;
}

.cursor-pointer {
  cursor: pointer;
}

.symptom-tag:hover {
  background-color: #198754 !important;
  color: white !important;
}
</style>
