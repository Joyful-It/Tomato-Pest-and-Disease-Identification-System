<!--
文件名: ResultView.vue
功能描述: 诊断结果展示组件，包含天气信息和追问功能
作者: ZT
日期: 2026/6/16
-->

<template>
  <div class="result-view">
    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">正在加载诊断结果...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-5">
      <i class="bi bi-exclamation-circle fs-1 text-danger"></i>
      <p class="mt-3 text-danger">{{ error }}</p>
      <router-link to="/" class="btn btn-success">返回首页</router-link>
    </div>

    <!-- 诊断结果 -->
    <div v-else-if="result">
      <!-- 返回按钮 -->
      <div class="mb-4">
        <router-link to="/" class="btn btn-outline-success">
          <i class="bi bi-arrow-left"></i> 返回首页
        </router-link>
      </div>

      <!-- 病虫害识别结果 -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-success text-white">
          <h5 class="mb-0">
            <i class="bi bi-search"></i> 病虫害识别结果
          </h5>
        </div>
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h4 class="text-success">
                {{ result.disease_result?.disease_name || '未知' }}
              </h4>
              <p class="mb-2">
                <span class="badge" :class="result.disease_result?.is_healthy ? 'bg-success' : 'bg-warning'">
                  {{ result.disease_result?.is_healthy ? '健康' : '发现病害' }}
                </span>
                <span class="ms-2 text-muted">
                  置信度：{{ (result.disease_result?.confidence || 0).toFixed(1) }}%
                </span>
              </p>
              <div v-if="result.disease_result?.symptoms?.length">
                <p class="mb-1"><strong>症状：</strong></p>
                <span
                  v-for="symptom in result.disease_result.symptoms"
                  :key="symptom"
                  class="badge bg-light text-dark me-1 mb-1"
                >
                  {{ symptom }}
                </span>
              </div>
            </div>
            <div class="col-md-4 text-center">
              <div class="display-4" :class="result.disease_result?.is_healthy ? 'text-success' : 'text-warning'">
                <i :class="result.disease_result?.is_healthy ? 'bi bi-check-circle' : 'bi bi-exclamation-triangle'"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 天气信息卡片 -->
      <div class="card shadow-sm mb-4" v-if="weatherData && weatherData.success">
        <div class="card-header bg-info text-white">
          <h5 class="mb-0">
            <i class="bi bi-cloud-sun"></i> 当地天气信息
          </h5>
        </div>
        <div class="card-body">
          <!-- 今日天气 -->
          <div class="row mb-3">
            <div class="col-md-6">
              <div class="d-flex align-items-center">
                <i :class="getWeatherIcon(weatherData.today?.skycon)" class="fs-1 me-3"></i>
                <div>
                  <h3 class="mb-0">{{ weatherData.today?.description }}</h3>
                  <p class="text-muted mb-0">{{ weatherData.today?.date }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="row text-center">
                <div class="col-4">
                  <div class="fs-4 fw-bold text-danger">{{ weatherData.today?.temperature?.max?.toFixed(0) }}°C</div>
                  <small class="text-muted">最高</small>
                </div>
                <div class="col-4">
                  <div class="fs-4 fw-bold text-primary">{{ weatherData.today?.temperature?.min?.toFixed(0) }}°C</div>
                  <small class="text-muted">最低</small>
                </div>
                <div class="col-4">
                  <div class="fs-4 fw-bold text-info">{{ weatherData.today?.humidity?.avg?.toFixed(0) }}%</div>
                  <small class="text-muted">湿度</small>
                </div>
              </div>
            </div>
          </div>

          <!-- 未来预报 -->
          <div class="row" v-if="weatherData.forecast?.length">
            <div class="col-12">
              <h6 class="text-muted mb-2">未来预报</h6>
            </div>
            <div v-for="(day, index) in weatherData.forecast" :key="index" class="col text-center">
              <div class="p-2 border rounded">
                <div class="fw-bold">{{ index === 0 ? '今天' : index === 1 ? '明天' : '后天' }}</div>
                <i :class="getWeatherIcon(day.skycon)" class="fs-4 my-1"></i>
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

      <!-- 综合建议 -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">
            <i class="bi bi-lightbulb"></i> 综合防治建议
          </h5>
        </div>
        <div class="card-body">
          <div class="advice-content" v-html="formatAdvice(result.final_advice)"></div>
        </div>
      </div>

      <!-- 详细分析（可折叠） -->
      <div class="accordion mb-4" id="analysisAccordion">
        <!-- 天气分析 -->
        <div class="accordion-item" v-if="result.weather_analysis">
          <h2 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#weather">
              <i class="bi bi-cloud-sun me-2"></i> 天气分析
            </button>
          </h2>
          <div id="weather" class="accordion-collapse collapse show" data-bs-parent="#analysisAccordion">
            <div class="accordion-body">
              <div v-if="result.weather_analysis.success">
                <p><strong>天气影响分析：</strong></p>
                <p>{{ result.weather_analysis.analysis }}</p>
                <p class="mt-3"><strong>天气相关建议：</strong></p>
                <p>{{ result.weather_analysis.advice }}</p>
              </div>
              <p v-else class="text-muted">{{ result.weather_analysis.error || '天气分析未完成' }}</p>
            </div>
          </div>
        </div>

        <!-- 土壤分析 -->
        <div class="accordion-item" v-if="result.soil_analysis">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#soil">
              <i class="bi bi-globe me-2"></i> 土壤分析
            </button>
          </h2>
          <div id="soil" class="accordion-collapse collapse" data-bs-parent="#analysisAccordion">
            <div class="accordion-body">
              <div v-if="result.soil_analysis.success">
                <p><strong>土壤与病害关系：</strong></p>
                <p>{{ result.soil_analysis.analysis }}</p>
                <p class="mt-3"><strong>土壤改良建议：</strong></p>
                <p>{{ result.soil_analysis.advice }}</p>
              </div>
              <p v-else class="text-muted">{{ result.soil_analysis.error || '土壤分析未完成' }}</p>
            </div>
          </div>
        </div>

        <!-- 灌溉建议 -->
        <div class="accordion-item" v-if="result.irrigation_advice">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#irrigation">
              <i class="bi bi-droplet me-2"></i> 灌溉建议
            </button>
          </h2>
          <div id="irrigation" class="accordion-collapse collapse" data-bs-parent="#analysisAccordion">
            <div class="accordion-body">
              <div v-if="result.irrigation_advice.success">
                <p><strong>灌溉需求分析：</strong></p>
                <p>{{ result.irrigation_advice.analysis }}</p>
                <p class="mt-3"><strong>灌溉建议：</strong></p>
                <p>{{ result.irrigation_advice.advice }}</p>
              </div>
              <p v-else class="text-muted">{{ result.irrigation_advice.error || '灌溉分析未完成' }}</p>
            </div>
          </div>
        </div>

        <!-- 安全用药 -->
        <div class="accordion-item" v-if="result.safety_advice">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#safety">
              <i class="bi bi-shield-check me-2"></i> 安全用药
            </button>
          </h2>
          <div id="safety" class="accordion-collapse collapse" data-bs-parent="#analysisAccordion">
            <div class="accordion-body">
              <div v-if="result.safety_advice.success">
                <p><strong>用药安全性分析：</strong></p>
                <p>{{ result.safety_advice.analysis }}</p>
                <p class="mt-3"><strong>用药建议：</strong></p>
                <p>{{ result.safety_advice.advice }}</p>
              </div>
              <p v-else class="text-muted">{{ result.safety_advice.error || '用药分析未完成' }}</p>
            </div>
          </div>
        </div>

        <!-- 种植日历 -->
        <div class="accordion-item" v-if="result.calendar_advice">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#calendar">
              <i class="bi bi-calendar me-2"></i> 种植日历
            </button>
          </h2>
          <div id="calendar" class="accordion-collapse collapse" data-bs-parent="#analysisAccordion">
            <div class="accordion-body">
              <div v-if="result.calendar_advice.success">
                <p><strong>农事安排：</strong></p>
                <p>{{ result.calendar_advice.analysis }}</p>
              </div>
              <p v-else class="text-muted">{{ result.calendar_advice.error || '日历分析未完成' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 追问功能 -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-warning text-dark">
          <h5 class="mb-0">
            <i class="bi bi-chat-dots"></i> 继续咨询
          </h5>
        </div>
        <div class="card-body">
          <p class="text-muted mb-3">如有其他疑问，可以继续向 AI 助手提问：</p>

          <!-- 对话历史 -->
          <div class="chat-history mb-3" v-if="chatHistory.length">
            <div v-for="(chat, index) in chatHistory" :key="index" class="chat-message mb-3">
              <!-- 用户消息 -->
              <div class="d-flex justify-content-end mb-2">
                <div class="bg-success text-white p-2 rounded-3" style="max-width: 80%;">
                  {{ chat.question }}
                </div>
              </div>
              <!-- AI 回复 -->
              <div class="d-flex justify-content-start">
                <div class="bg-light p-2 rounded-3" style="max-width: 80%;">
                  <div v-html="formatAdvice(chat.answer)"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="input-group">
            <input
              v-model="chatMessage"
              type="text"
              class="form-control"
              placeholder="输入您的问题，例如：这个病用什么药效果最好？"
              @keyup.enter="sendChat"
              :disabled="chatLoading"
            >
            <button
              class="btn btn-warning"
              type="button"
              @click="sendChat"
              :disabled="chatLoading || !chatMessage.trim()"
            >
              <span v-if="chatLoading" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-send"></i>
              发送
            </button>
          </div>

          <!-- 快捷问题 -->
          <div class="mt-3">
            <small class="text-muted">快捷提问：</small>
            <div class="mt-1">
              <button
                v-for="quickQuestion in quickQuestions"
                :key="quickQuestion"
                class="btn btn-outline-secondary btn-sm me-2 mb-2"
                @click="chatMessage = quickQuestion; sendChat()"
                :disabled="chatLoading"
              >
                {{ quickQuestion }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="text-center mt-4">
        <router-link to="/" class="btn btn-success btn-lg me-3">
          <i class="bi bi-plus-circle"></i> 新的诊断
        </router-link>
        <router-link to="/history" class="btn btn-outline-success btn-lg">
          <i class="bi bi-clock-history"></i> 查看历史
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 诊断结果展示组件
 * 展示病虫害识别结果、天气信息和各 Agent 的分析建议
 * 支持追问功能
 */
import axios from 'axios'

export default {
  name: 'ResultView',
  data() {
    return {
      result: null,
      weatherData: null,
      loading: true,
      error: null,
      chatMessage: '',
      chatLoading: false,
      chatHistory: [],
      quickQuestions: [
        '这个病用什么药效果最好？',
        '施药时需要注意什么？',
        '如何预防这种病害？',
        '近期天气适合施药吗？'
      ]
    }
  },
  async created() {
    await this.loadResult()
  },
  methods: {
    /**
     * 加载诊断结果
     */
    async loadResult() {
      const diagnosisId = this.$route.params.id

      try {
        // 获取诊断详情
        const response = await axios.get(`/api/diagnosis/${diagnosisId}`)

        if (response.data.success) {
          const data = response.data
          this.result = {
            diagnosis_id: data.diagnosis_id,
            disease_result: data.disease_result,
            weather_analysis: data.weather_analysis,
            soil_analysis: data.soil_analysis,
            irrigation_advice: data.irrigation_advice,
            safety_advice: data.safety_advice,
            calendar_advice: data.calendar_advice,
            final_advice: data.final_advice
          }

          // 处理天气数据
          if (data.weather_data && data.weather_data.success) {
            this.weatherData = data.weather_data
          } else if (data.latitude && data.longitude) {
            // 如果没有天气数据，单独请求
            await this.loadWeather(data.latitude, data.longitude)
          }
        } else {
          this.error = '未找到诊断记录'
        }
      } catch (error) {
        console.error('加载诊断结果失败:', error)
        this.error = '加载诊断结果失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载天气数据
     */
    async loadWeather(latitude, longitude) {
      try {
        const response = await axios.get(`/api/weather/${latitude}/${longitude}`)
        if (response.data.success) {
          this.weatherData = response.data
        }
      } catch (error) {
        console.error('加载天气数据失败:', error)
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
     * 发送追问
     */
    async sendChat() {
      if (!this.chatMessage.trim() || this.chatLoading) return

      const question = this.chatMessage.trim()
      this.chatMessage = ''
      this.chatLoading = true

      try {
        const response = await axios.post('/api/chat', {
          diagnosis_id: this.result.diagnosis_id,
          message: question
        })

        if (response.data.success) {
          this.chatHistory.push({
            question: question,
            answer: response.data.message
          })

          // 滚动到底部
          this.$nextTick(() => {
            const chatContainer = this.$el.querySelector('.chat-history')
            if (chatContainer) {
              chatContainer.scrollTop = chatContainer.scrollHeight
            }
          })
        } else {
          alert('提问失败：' + (response.data.error || '未知错误'))
        }
      } catch (error) {
        console.error('追问失败:', error)
        alert('提问失败，请稍后重试')
      } finally {
        this.chatLoading = false
      }
    },

    /**
     * 格式化建议内容
     */
    formatAdvice(advice) {
      if (!advice) return ''

      // 将换行符转换为 <br>
      let formatted = advice.replace(/\n/g, '<br>')

      // 将 **text** 转换为 <strong>text</strong>
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

      // 将数字列表转换为有序列表样式
      formatted = formatted.replace(/(\d+)\.\s/g, '<br><strong>$1.</strong> ')

      return formatted
    }
  }
}
</script>

<style scoped>
.advice-content {
  line-height: 1.8;
  font-size: 1.05rem;
}

.advice-content strong {
  color: #198754;
}

.chat-history {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chat-message {
  margin-bottom: 15px;
}

.chat-message .rounded-3 {
  border-radius: 12px !important;
}
</style>