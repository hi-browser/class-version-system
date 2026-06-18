<template>
  <div>
    <el-card class="card" style="margin-bottom: 18px">
      <template #header>上传课堂图片或视频</template>
      <el-form label-width="100px" inline>
        <el-form-item label="班级">
          <el-select v-model="form.class_group_id" placeholder="选择班级" style="width: 180px" @change="onClassChange">
            <el-option v-for="c in classes" :key="c.id" :label="c.course_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期">
          <el-date-picker v-model="form.analysis_date" type="date" value-format="YYYY-MM-DD" style="width: 160px" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-select v-model="form.time_slot" style="width: 120px">
            <el-option v-for="n in 9" :key="n" :label="'第'+n+'节'" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课地点">
          <el-select v-model="form.location" placeholder="选择地点" style="width: 160px" filterable allow-create>
            <el-option v-for="loc in locations" :key="loc" :label="loc" :value="loc" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级人数">
          <el-input-number v-model="form.student_count" :min="0" :disabled="true" style="width: 120px" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload ref="uploadRef" drag :auto-upload="false" :limit="1" :on-change="onFileChange" style="width: 280px">
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽或点击上传</div>
            <template #tip><div class="el-upload__tip">支持 jpg/png/mp4/avi/mov</div></template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="submit">开始分析</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="card" v-if="result" style="margin-bottom: 18px">
      <template #header>分析结果</template>
      <div class="grid grid-4">
        <div class="metric"><div class="label">检测人数</div><div class="value">{{ result.detected_count }}</div></div>
        <div class="metric"><div class="label">到课率</div><div class="value">{{ result.attendance_rate }}%</div></div>
        <div class="metric"><div class="label">参与率</div><div class="value">{{ result.participation_rate }}%</div></div>
        <div class="metric"><div class="label">异常率</div><div class="value">{{ result.abnormal_rate }}%</div></div>
      </div>
      <el-table :data="result.behavior_counts" style="margin-top: 16px">
        <el-table-column prop="name" label="行为类别" />
        <el-table-column prop="count" label="数量" />
        <el-table-column prop="rate" label="占比(%)" />
      </el-table>
      <img v-if="result.result_path && isImageResult" class="result-image" :src="'/' + result.result_path" style="margin-top:16px" />
    </el-card>

    <el-card class="card" style="margin-bottom: 18px">
      <template #header>数据看板概览</template>
      <div class="grid grid-4">
        <div class="metric"><div class="label">课堂记录数</div><div class="value">{{ overview.total_sessions || 0 }}</div></div>
        <div class="metric"><div class="label">平均到课率</div><div class="value">{{ overview.avg_attendance || 0 }}%</div></div>
        <div class="metric"><div class="label">平均参与率</div><div class="value">{{ overview.avg_participation || 0 }}%</div></div>
        <div class="metric"><div class="label">异常行为率</div><div class="value">{{ overview.avg_abnormal || 0 }}%</div></div>
      </div>
    </el-card>

    <div class="grid grid-2" style="margin-bottom: 18px">
      <el-card class="card chart-card">
        <template #header>课堂行为分布</template>
        <EChart :option="barOption" />
      </el-card>
      <el-card class="card chart-card">
        <template #header>视频分析趋势（异常率 & 参与率）</template>
        <EChart v-if="videoTrend.length > 0" :option="lineOption" />
        <div v-else class="chart-empty">暂无视频分析数据，请上传视频进行分析</div>
      </el-card>
    </div>

    <el-card class="card analysis-card">
      <template #header>课堂智能分析</template>
      <div class="analysis-content">{{ analysisText }}</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import EChart from '../components/EChart.vue'
import { getOverview, getBehaviorSummary, getVideoTrend, getClasses, getLocations, uploadAnalyze } from '../api'

const overview = ref({})
const behavior = ref([])
const videoTrend = ref([])
const classes = ref([])
const locations = ref([])
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const uploadRef = ref(null)
const form = ref({ class_group_id: null, analysis_date: '', time_slot: 1, location: '', student_count: 0 })

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}
function formatRate(value) {
  return toNumber(value).toFixed(1)
}

const isImageResult = computed(() => {
  const p = result.value?.result_path || ''
  return /\.(jpg|jpeg|png|webp|bmp)$/i.test(p)
})

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', formatter: '{b}<br/>人数：{c}' },
  grid: { left: 50, right: 24, top: 16, bottom: 60 },
  xAxis: {
    type: 'category',
    data: behavior.value.map(x => x.name),
    axisLabel: { rotate: 20, hideOverlap: true }
  },
  yAxis: { type: 'value', name: '人数' },
  series: [{
    type: 'bar',
    data: behavior.value.map(x => toNumber(x.value)),
    itemStyle: {
      color: ({ dataIndex }) => {
        const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#fc8452']
        return colors[dataIndex % colors.length]
      }
    },
    barMaxWidth: 48
  }]
}))

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['异常率', '参与率'], top: 0 },
  grid: { left: 55, right: 24, top: 48, bottom: 42 },
  xAxis: {
    type: 'category',
    data: videoTrend.value.map(x => {
      if (x.time) return x.time
      if (x.timestamp !== undefined) return String(x.timestamp)
      return ''
    }),
    axisLabel: { hideOverlap: true }
  },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [
    { name: '异常率', type: 'line', smooth: true, data: videoTrend.value.map(x => toNumber(x.abnormal_rate ?? x.abnormal)) },
    { name: '参与率', type: 'line', smooth: true, data: videoTrend.value.map(x => toNumber(x.participation_rate ?? x.participation)) }
  ]
}))

const analysisText = computed(() => {
  const total = toNumber(overview.value.total_sessions)
  if (total === 0) return '暂无课堂记录，请先上传课堂图片或视频进行分析。'
  const attendance = toNumber(overview.value.avg_attendance)
  const participation = toNumber(overview.value.avg_participation)
  const abnormal = toNumber(overview.value.avg_abnormal)
  const parts = []
  if (attendance >= 90) parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，整体出勤情况良好。`)
  else if (attendance >= 75) parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，出勤情况基本正常，但仍有提升空间。`)
  else parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，出勤情况偏低，建议重点关注缺勤或迟到情况。`)
  if (participation >= 60) parts.push(`平均参与率为 ${formatRate(participation)}%，学生课堂参与度较高。`)
  else if (participation >= 40) parts.push(`平均参与率为 ${formatRate(participation)}%，课堂参与度中等，建议适当增加互动。`)
  else parts.push(`平均参与率为 ${formatRate(participation)}%，课堂活跃度偏低，建议通过提问、讨论等方式提升参与度。`)
  if (abnormal >= 25) parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂分心现象较明显，需重点关注手机使用、低头、趴桌等行为。`)
  else if (abnormal >= 15) parts.push(`异常行为率为 ${formatRate(abnormal)}%，存在一定分心现象，建议加强提醒和巡视。`)
  else parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂纪律整体较稳定。`)
  parts.push('综合建议：后续可结合检测结果关注后排、角落和遮挡区域学生状态，并通过课堂互动、巡视提醒和任务驱动方式提升课堂参与度。')
  return parts.join('')
})

function onClassChange(id) {
  const cg = classes.value.find(x => x.id === id)
  form.value.student_count = cg ? cg.student_count : 0
}

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}

async function submit() {
  if (!form.value.class_group_id) return ElMessage.warning('请选择班级')
  if (!form.value.analysis_date) return ElMessage.warning('请选择上课日期')
  if (!form.value.location) return ElMessage.warning('请输入上课地点')
  if (!file.value) return ElMessage.warning('请先选择文件')
  loading.value = true
  result.value = null
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('class_group_id', form.value.class_group_id)
    fd.append('analysis_date', form.value.analysis_date)
    fd.append('time_slot', form.value.time_slot)
    fd.append('location', form.value.location)
    result.value = await uploadAnalyze(fd)
    ElMessage.success('分析完成')
    file.value = null
    uploadRef.value?.clearFiles()
    await loadDashboard()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function loadDashboard() {
  overview.value = await getOverview()
  behavior.value = await getBehaviorSummary()
  videoTrend.value = await getVideoTrend()
}

onMounted(() => {
  loadDashboard()
  getClasses().then(data => { classes.value = data }).catch(() => {})
  getLocations().then(data => { locations.value = data }).catch(() => {})
})
</script>

<style scoped>
.chart-card :deep(.echarts),
.chart-card :deep(.chart) {
  min-height: 420px;
}
.chart-empty {
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  user-select: none;
}
.analysis-card { margin-top: 18px; }
.analysis-content {
  font-size: 15px;
  line-height: 1.9;
  color: #303133;
  text-align: justify;
  white-space: pre-line;
  text-indent: 2em;
}
.result-image { max-width: 100%; border-radius: 8px; }
</style>