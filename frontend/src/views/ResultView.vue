<!--
文件名: ResultView.vue
功能描述: 诊断结果展示组件
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
                  置信度：{{ (result.disease_result?.confidence * 100).toFixed(1) }}%
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
      <div class="accordion" id="analysisAccordion">
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
 * 展示病虫害识别结果和各 Agent 的分析建议
 */
import axios from 'axios'

export default {
  name: 'ResultView',
  data() {
    return {
      result: null,
      loading: true,
      error: null
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
        // 从历史记录中获取诊断结果
        const response = await axios.get(`/api/history`)

        if (response.data.success) {
          const record = response.data.records.find(r => r.id === parseInt(diagnosisId))

          if (record) {
            // 这里简化处理，实际应该有专门的接口获取单条记录的详细信息
            this.result = {
              diagnosis_id: record.id,
              disease_result: {
                disease_name: record.disease_name,
                confidence: 0.85,
                symptoms: [],
                is_healthy: record.disease_name === '番茄-健康'
              },
              final_advice: '正在加载详细建议...'
            }

            // 加载详细信息
            await this.loadDetail(diagnosisId)
          } else {
            this.error = '未找到诊断记录'
          }
        } else {
          this.error = '加载失败'
        }
      } catch (error) {
        console.error('加载诊断结果失败:', error)
        this.error = '加载诊断结果失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载详细信息
     */
    async loadDetail(diagnosisId) {
      // 这里应该调用专门的接口获取详细信息
      // 目前使用模拟数据
      this.result = {
        ...this.result,
        weather_analysis: {
          success: true,
          analysis: '当前天气多云，温度适中，有利于番茄生长，但需注意湿度变化。',
          advice: '建议在晴天进行施药，避免雨天操作。'
        },
        soil_analysis: {
          success: true,
          analysis: '土壤 pH 值适中，有机质含量良好。',
          advice: '建议增施有机肥，改善土壤结构。'
        },
        irrigation_advice: {
          success: true,
          analysis: '当前土壤湿度适中，无需立即灌溉。',
          advice: '建议采用滴灌方式，保持土壤湿润但不积水。'
        },
        safety_advice: {
          success: true,
          analysis: '推荐使用低毒农药，注意安全间隔期。',
          advice: '建议使用百菌清或多菌灵进行防治，施药时佩戴防护装备。'
        },
        calendar_advice: {
          success: true,
          analysis: '未来一周适合进行病害防治和田间管理。',
          advice: null
        },
        final_advice: `根据诊断结果，您的番茄可能存在病害问题。建议采取以下措施：

1. **病害防治**：及时使用推荐的农药进行防治，注意按照说明书使用。

2. **田间管理**：加强通风透光，及时清除病叶病果，减少病害传播。

3. **水肥管理**：合理灌溉，避免积水，增施有机肥提高植株抗病能力。

4. **预防措施**：定期巡查，发现病害及时处理，防止扩散。

5. **安全用药**：施药时注意防护，遵守安全间隔期，确保农产品安全。

请根据实际情况调整管理措施，如有疑问可随时咨询。`
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
</style>
