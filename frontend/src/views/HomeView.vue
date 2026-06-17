<!--
文件名: HomeView.vue
功能描述: 主页面 - 清新自然的农业诊断界面
作者: ZT
日期: 2026/6/17
-->

<template>
  <div class="app">
    <!-- 顶部栏 -->
    <header class="header">
      <div class="header-inner">
        <div class="brand">
          <span class="brand-icon">🍅</span>
          <div>
            <h1>番茄卫士</h1>
            <p>病虫害智能诊断</p>
          </div>
        </div>
        <div class="status-badge ready">
          ✓ 知识库就绪
        </div>
      </div>
    </header>

    <div class="main">
      <!-- 左侧面板 -->
      <aside class="panel">
        <!-- 位置信息 -->
        <div class="card">
          <h3 class="card-title">📍 我的位置</h3>
          <div class="location-box" v-if="latitude">
            <span>{{ latitude.toFixed(4) }}, {{ longitude.toFixed(4) }}</span>
          </div>
          <button class="btn btn-green" @click="getLocation" :disabled="locating">
            {{ locating ? '定位中...' : '获取当前位置' }}
          </button>
          <input v-model="manualLocation" class="input" placeholder="或手动输入地区名称">
        </div>

        <!-- 天气信息 -->
        <div class="card" v-if="weather">
          <h3 class="card-title">🌤️ 今日天气</h3>
          <div class="weather-box">
            <div class="weather-main">
              <span class="weather-icon">{{ getWeatherEmoji(weather.today?.skycon) }}</span>
              <div>
                <span class="weather-temp">{{ weather.today?.temperature?.avg?.toFixed(0) }}°C</span>
                <span class="weather-desc">{{ weather.today?.description }}</span>
              </div>
            </div>
            <div class="weather-detail">
              <span>最高 {{ weather.today?.temperature?.max?.toFixed(0) }}°C</span>
              <span>最低 {{ weather.today?.temperature?.min?.toFixed(0) }}°C</span>
              <span>湿度 {{ (weather.today?.humidity?.avg * 100)?.toFixed(0) }}%</span>
            </div>
          </div>
          <div class="weather-tip" v-if="weatherTip">{{ weatherTip }}</div>
        </div>

        <!-- 土壤选择 -->
        <div class="card">
          <h3 class="card-title">🌱 当地土质</h3>
          <div class="soil-detected" v-if="detectedSoil">
            <span class="soil-tag">{{ detectedSoil }}</span>
          </div>
          <select v-model="selectedSoil" class="select" @change="onSoilChange">
            <option value="">选择当地土质...</option>
            <option v-for="s in soilOptions" :key="s.name" :value="s.name">
              {{ s.name }} (pH {{ s.ph }})
            </option>
          </select>
          <p class="soil-desc" v-if="soilDesc">{{ soilDesc }}</p>
        </div>
      </aside>

      <!-- 聊天区 -->
      <div class="chat">
        <!-- 欢迎 -->
        <div class="welcome" v-if="messages.length === 0">
          <div class="welcome-icon">🍅</div>
          <h2>你好，我是番茄卫士</h2>
          <p>上传图片或描述症状，帮你诊断番茄病虫害</p>
          <div class="quick-questions">
            <button class="quick-btn" @click="quickAsk('叶子发黄了')">叶子发黄</button>
            <button class="quick-btn" @click="quickAsk('果实烂了')">果实腐烂</button>
            <button class="quick-btn" @click="quickAsk('叶子上有小虫子')">有虫子</button>
            <button class="quick-btn" @click="quickAsk('叶子长斑了')">叶子长斑</button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages" ref="msgList">
          <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
            <div class="msg-avatar">{{ msg.role === 'user' ? '👨‍🌾' : '🌱' }}</div>
            <div class="msg-body">
              <div class="msg-bubble" v-html="renderMsg(msg.content)"></div>
              <img v-if="msg.image" :src="msg.image" class="msg-image">
              <span class="msg-time">{{ msg.time }}</span>
            </div>
          </div>

          <!-- 加载 -->
          <div class="msg assistant" v-if="loading">
            <div class="msg-avatar">🌱</div>
            <div class="msg-body">
              <div class="msg-bubble loading">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="input-area">
          <div class="preview-box" v-if="imagePreview">
            <img :src="imagePreview" class="preview-img">
            <button class="preview-close" @click="clearImage">✕</button>
          </div>
          <div class="input-row">
            <label class="btn-icon" title="上传图片">
              📷
              <input type="file" accept="image/*" @change="onFileSelect" class="hidden">
            </label>
            <textarea
              v-model="inputText"
              class="textarea"
              placeholder="描述番茄症状，如：叶子发黄、长斑、有虫..."
              @keydown.enter.exact.prevent="send"
              rows="1"
            ></textarea>
            <button class="btn btn-send" @click="send" :disabled="loading || (!inputText.trim() && !imageFile)">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      systemReady: false,
      latitude: null,
      longitude: null,
      manualLocation: '',
      locating: false,
      weather: null,
      selectedSoil: '',
      detectedSoil: '',
      soilDesc: '',
      soilOptions: [
        { name: '潮土', ph: '7.7~9.0', region: '豫东豫北', desc: '弱碱性，适合大多数作物，保水保肥好' },
        { name: '褐土', ph: '7.0~8.5', region: '豫西豫中', desc: '中弱碱性，肥力较高，适合小麦玉米' },
        { name: '砂姜黑土', ph: '5.0~8.1', region: '豫南', desc: '粘重，需增施有机肥改良' },
        { name: '黄棕壤', ph: '5.5~7.5', region: '豫西南山区', desc: '微酸中性，适合果树种植' },
        { name: '黄褐土', ph: '6.5~7.5', region: '南阳驻马店', desc: '质地粘重，需配合施肥' },
        { name: '水稻土', ph: '5.0~8.0', region: '信阳', desc: '有机质丰富，适合水旱轮作' },
        { name: '紫色土', ph: '7.0~7.9', region: '西峡内乡', desc: '中性，注意水土保持' }
      ],
      messages: [],
      inputText: '',
      imageFile: null,
      imagePreview: null,
      loading: false
    }
  },
  computed: {
    weatherTip() {
      if (!this.weather?.today) return ''
      const t = this.weather.today
      const skycon = t.skycon || ''
      if (skycon.includes('RAIN')) return '今天有雨，不宜施药，注意排水'
      if (t.temperature?.avg > 35) return '高温天气，注意遮阳降温'
      if (t.humidity?.avg > 0.8) return '湿度较高，注意通风防病'
      return '天气适合田间管理'
    }
  },
  created() {
    // 直接标记为就绪，避免加载中显示
    this.systemReady = true
  },
  methods: {
    // 定位
    async getLocation() {
      this.locating = true
      try {
        if (!navigator.geolocation) {
          alert('浏览器不支持定位')
          this.locating = false
          return
        }
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            this.latitude = pos.coords.latitude
            this.longitude = pos.coords.longitude
            this.locating = false
            await this.loadWeather()
            this.guessSoil()
          },
          () => {
            alert('定位失败，请手动输入')
            this.locating = false
          },
          { timeout: 10000 }
        )
      } catch (e) {
        this.locating = false
      }
    },

    async loadWeather() {
      if (!this.latitude) return
      try {
        const res = await axios.get(`/api/weather/${this.latitude}/${this.longitude}`)
        if (res.data.success) this.weather = res.data
      } catch (e) {
        console.error('天气加载失败', e)
      }
    },

    guessSoil() {
      if (!this.latitude) return
      // 简单推断
      if (this.latitude > 35.5) {
        this.selectedSoil = '潮土'
        this.detectedSoil = '潮土'
      } else if (this.latitude < 33) {
        this.selectedSoil = '黄棕壤'
        this.detectedSoil = '黄棕壤'
      } else {
        this.selectedSoil = '褐土'
        this.detectedSoil = '褐土'
      }
      this.soilDesc = this.soilOptions.find(s => s.name === this.selectedSoil)?.desc || ''
    },

    onSoilChange() {
      this.detectedSoil = this.selectedSoil
      this.soilDesc = this.soilOptions.find(s => s.name === this.selectedSoil)?.desc || ''
    },

    // 图片
    onFileSelect(e) {
      const file = e.target.files[0]
      if (!file) return
      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
    },

    clearImage() {
      this.imageFile = null
      if (this.imagePreview) URL.revokeObjectURL(this.imagePreview)
      this.imagePreview = null
    },

    // 聊天
    quickAsk(text) {
      this.inputText = text
      this.send()
    },

    async send() {
      const text = this.inputText.trim()
      if (!text && !this.imageFile) return

      // 添加用户消息
      this.messages.push({
        role: 'user',
        content: text || '请看这张图片',
        image: this.imagePreview,
        time: this.now()
      })

      // 保存并清空
      const img = this.imageFile
      const preview = this.imagePreview
      this.inputText = ''
      this.imageFile = null
      this.imagePreview = null
      this.$nextTick(() => this.scrollBottom())

      // 请求
      this.loading = true
      try {
        const fd = new FormData()
        if (img) fd.append('file', img)
        fd.append('request', JSON.stringify({
          text_input: text || null,
          latitude: this.latitude,
          longitude: this.longitude,
          location: this.manualLocation || null,
          soil_type: this.selectedSoil || null,
          chat_history: this.messages.slice(-10).map(m => ({ role: m.role, content: m.content }))
        }))

        const res = await axios.post('/api/diagnosis', fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (res.data.success) {
          let parts = []
          const d = res.data.disease_result
          if (d) {
            // 显示多种可能的病症及概率
            if (d.candidates && d.candidates.length > 0) {
              parts.push('🔍 **可能的病症：**')
              d.candidates.forEach(c => {
                const filled = Math.round(c.probability / 10)
                const bar = '█'.repeat(filled) + '░'.repeat(10 - filled)
                parts.push(`${bar} ${c.probability}% **${c.name}**`)
              })
              parts.push('')
            }

            const icon = d.is_healthy ? '✅' : '⚠️'
            parts.push(`${icon} **最可能：${d.disease_name}**`)

            if (d.symptoms?.length) {
              parts.push(`症状：${d.symptoms.join('、')}`)
            }
            parts.push('')
          }

          if (res.data.final_advice) {
            parts.push('---')
            parts.push(res.data.final_advice)
          }

          this.messages.push({ role: 'assistant', content: parts.join('\n'), time: this.now() })
        } else {
          this.messages.push({ role: 'assistant', content: '诊断失败，请重试', time: this.now() })
        }
      } catch (e) {
        this.messages.push({ role: 'assistant', content: '请求失败，请稍后重试', time: this.now() })
      } finally {
        this.loading = false
        this.$nextTick(() => this.scrollBottom())
      }
    },

    renderMsg(text) {
      if (!text) return ''
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
    },

    getWeatherEmoji(s) {
      const m = { 'CLEAR_DAY': '☀️', 'PARTLY_CLOUDY_DAY': '⛅', 'CLOUDY': '☁️', 'LIGHT_RAIN': '🌦️', 'MODERATE_RAIN': '🌧️', 'HEAVY_RAIN': '⛈️' }
      return m[s] || '🌤️'
    },

    now() {
      const d = new Date()
      return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
    },

    scrollBottom() {
      const el = this.$refs.msgList
      if (el) el.scrollTop = el.scrollHeight
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f7f0;
}

/* 头部 */
.header {
  background: #fff;
  border-bottom: 2px solid #8bc34a;
  padding: 12px 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  font-size: 32px;
}

.brand h1 {
  font-size: 20px;
  color: #2e7d32;
  font-weight: 700;
}

.brand p {
  font-size: 12px;
  color: #888;
}

.status-badge {
  padding: 6px 14px;
  background: #eee;
  border-radius: 20px;
  font-size: 13px;
  color: #999;
}

.status-badge.ready {
  background: #e8f5e9;
  color: #2e7d32;
}

/* 主布局 */
.main {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 20px;
  padding: 20px;
  height: calc(100vh - 70px);
}

/* 左侧面板 */
.panel {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.card-title {
  font-size: 15px;
  color: #555;
  margin-bottom: 12px;
}

.location-box {
  background: #f5f5f5;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-green {
  background: #4caf50;
  color: #fff;
  width: 100%;
}

.btn-green:hover {
  background: #388e3c;
}

.btn-green:disabled {
  background: #a5d6a7;
  cursor: not-allowed;
}

.input, .select, .textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #333;
  margin-top: 10px;
}

.input:focus, .select:focus, .textarea:focus {
  outline: none;
  border-color: #4caf50;
}

.input::placeholder, .textarea::placeholder {
  color: #aaa;
}

/* 天气 */
.weather-box {
  margin-bottom: 10px;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.weather-icon {
  font-size: 36px;
}

.weather-temp {
  font-size: 24px;
  font-weight: 700;
  color: #ff9800;
  display: block;
}

.weather-desc {
  font-size: 13px;
  color: #888;
}

.weather-detail {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #888;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.weather-tip {
  margin-top: 10px;
  padding: 8px 12px;
  background: #fff3e0;
  border-radius: 8px;
  font-size: 13px;
  color: #e65100;
}

/* 土壤 */
.soil-detected {
  margin-bottom: 10px;
}

.soil-tag {
  display: inline-block;
  padding: 4px 12px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 12px;
  font-size: 13px;
}

.soil-desc {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
  padding: 8px;
  background: #f9fbe7;
  border-radius: 6px;
}

/* 聊天区 */
.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
}

/* 欢迎 */
.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.welcome h2 {
  font-size: 24px;
  color: #2e7d32;
  margin-bottom: 8px;
}

.welcome p {
  color: #888;
  margin-bottom: 24px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.quick-btn {
  padding: 8px 16px;
  background: #f1f8e9;
  border: 1px solid #c5e1a5;
  border-radius: 20px;
  color: #558b2f;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #dcedc8;
}

/* 消息 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.msg {
  display: flex;
  gap: 10px;
  max-width: 80%;
}

.msg.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f8e9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.msg.user .msg-avatar {
  background: #fff3e0;
}

.msg-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.msg.user .msg-body {
  align-items: flex-end;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.msg.assistant .msg-bubble {
  background: #f5f5f5;
  border-top-left-radius: 4px;
}

.msg.user .msg-bubble {
  background: #4caf50;
  color: #fff;
  border-top-right-radius: 4px;
}

.msg-bubble strong {
  color: #e65100;
}

.msg.user .msg-bubble strong {
  color: #fff;
  text-decoration: underline;
}

.msg-image {
  max-width: 160px;
  border-radius: 8px;
}

.msg-time {
  font-size: 11px;
  color: #bbb;
}

/* 加载动画 */
.msg-bubble.loading {
  display: flex;
  gap: 6px;
  padding: 14px 18px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #aaa;
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

/* 输入区 */
.input-area {
  padding: 12px 16px;
  background: #fafafa;
  border-top: 1px solid #eee;
}

.preview-box {
  display: inline-block;
  position: relative;
  margin-bottom: 8px;
}

.preview-img {
  max-width: 80px;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: #f44336;
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.btn-icon {
  width: 40px;
  height: 40px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  flex-shrink: 0;
}

.btn-icon:hover {
  background: #e8f5e9;
}

.hidden {
  display: none;
}

.textarea {
  flex: 1;
  resize: none;
  min-height: 40px;
  max-height: 100px;
  margin-top: 0;
}

.btn-send {
  background: #4caf50;
  color: #fff;
  padding: 0 20px;
  height: 40px;
  border-radius: 8px;
  font-weight: 600;
  flex-shrink: 0;
}

.btn-send:hover {
  background: #388e3c;
}

.btn-send:disabled {
  background: #a5d6a7;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .main {
    flex-direction: column;
    height: auto;
  }

  .panel {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    gap: 10px;
  }

  .card {
    min-width: 250px;
  }

  .chat {
    min-height: 500px;
  }
}
</style>