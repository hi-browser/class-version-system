<template>
  <div>
    <!-- 上传表单 -->
    <el-card class="card" style="margin-bottom: 18px">
      <template #header>上传课堂图片或视频</template>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px" inline>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程" style="width: 200px">
            <el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" style="width: 200px" @change="onClassChange">
            <el-option v-for="c in classes" :key="c.id" :label="c.class_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="应到人数">
          <el-input-number v-model="form.expected_count" :min="0" />
        </el-form-item>
        <el-form-item label="上课时间" prop="session_time">
          <el-date-picker v-model="form.session_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 200px" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload drag :auto-upload="false" :limit="1" :on-change="onFileChange" style="width: 320px">
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽或点击上传课堂图片/视频</div>
            <template #tip><div class="el-upload__tip">支持 jpg/png/mp4/avi/mov 等格式</div></template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="submit">开始分析</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分析结果 -->
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

    <!-- 数据看板概览 -->
    <div class="grid grid-4">
      <div class="metric">
        <div class="label">课堂记录数</div>
        <div class="value">{{ overview.total_sessions || 0 }}</div>
      </div>
      <div class="metric">
        <div class="label">平均到课率</div>
        <div class="value">{{ overview.avg_attendance || 0 }}%</div>
      </div>
      <div class="metric">
        <div class="label">平均参与率</div>
        <div class="value">{{ overview.avg_participation || 0 }}%</div>
      </div>
      <div class="metric">
        <div class="label">异常行为率</div>
        <div class="value">{{ overview.avg_abnormal || 0 }}%</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-2" style="margin-top:18px">
      <el-card class="card chart-card">
        <template #header>行为占比分布</template>
        <EChart :option="pieOption" />
      </el-card>
      <el-card class="card chart-card">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
            <span>出勤与参与趋势</span>
            <div style="display:flex;gap:10px">
              <el-select v-model="trendCourseId" placeholder="选择课程" clearable @change="loadFilteredTrend" style="width:140px">
                <el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" />
              </el-select>
              <el-select v-model="trendClassId" placeholder="选择班级" clearable @change="loadFilteredTrend" style="width:140px">
                <el-option v-for="c in classes" :key="c.id" :label="c.class_name" :value="c.id" />
              </el-select>
            </div>
          </div>
        </template>
        <EChart v-if="trend.length > 0" :option="lineOption" />
        <div v-else class="chart-empty">请选择课程或班级查看趋势数据</div>
      </el-card>
    </div>

    <!-- 智能分析 -->
    <el-card class="card analysis-card">
      <template #header>课堂智能分析</template>
      <div class="analysis-content">
        {{ analysisText }}
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import EChart from '../components/EChart.vue'
import {
  getOverview, getBehaviorSummary, getTrendByClassCourse,
  getCourses, getClasses, uploadAnalyze
} from '../api'

const overview = ref({})
const behavior = ref([])
const trend = ref([])
const courses = ref([])
const classes = ref([])
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const trendCourseId = ref(null)
const trendClassId = ref(null)
const formRef = ref(null)
const form = ref({ course_id: null, class_id: null, expected_count: 0, session_time: '' })

const formRules = {
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
  session_time: [{ required: true, message: '请选择上课时间', trigger: 'change' }]
}

const isImageResult = computed(() => {
  const p = result.value?.result_path || ''
  return /\.(jpg|jpeg|png|webp|bmp)$/i.test(p)
})

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function formatRate(value) {
  return toNumber(value).toFixed(1)
}

function getTopBehavior(list) {
  if (!Array.isArray(list) || list.length === 0) return null
  const valid = list.filter(item => toNumber(item.value ?? item.count) > 0)
  if (valid.length === 0) return null
  return [...valid].sort((a, b) => toNumber(b.value ?? b.count) - toNumber(a.value ?? a.count))[0]
}

const pieOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}<br/>数量：{c}<br/>占比：{d}%'
  },
  legend: {
    type: 'scroll',
    orient: 'horizontal',
    bottom: 0,
    left: 'center',
    itemWidth: 14,
    itemHeight: 14,
    textStyle: { fontSize: 12 }
  },
  series: [{
    name: '行为占比',
    type: 'pie',
    radius: ['45%', '68%'],
    center: ['50%', '43%'],
    data: behavior.value,
    avoidLabelOverlap: true,
    minAngle: 8,
    stillShowZeroSum: false,
    label: {
      show: true,
      position: 'outside',
      formatter: params => params.percent < 5 ? '' : params.name,
      fontSize: 12,
      lineHeight: 16
    },
    labelLine: { show: true, length: 14, length2: 18, smooth: true },
    labelLayout: { hideOverlap: true, moveOverlap: 'shiftY' },
    emphasis: {
      label: { show: true, fontSize: 14, fontWeight: 'bold', formatter: '{b}\n{d}%' }
    }
  }]
}))

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['到课率', '参与率', '异常率'], top: 0 },
  grid: { left: 45, right: 24, top: 48, bottom: 42 },
  xAxis: {
    type: 'category',
    data: trend.value.map(x => x.time),
    axisLabel: { hideOverlap: true }
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: { formatter: '{value}%' }
  },
  series: [
    { name: '到课率', type: 'line', smooth: true, data: trend.value.map(x => x.attendance_rate) },
    { name: '参与率', type: 'line', smooth: true, data: trend.value.map(x => x.participation_rate) },
    { name: '异常率', type: 'line', smooth: true, data: trend.value.map(x => x.abnormal_rate) }
  ]
}))

const analysisText = computed(() => {
  const total = toNumber(overview.value.total_sessions)
  if (total === 0) {
    return '暂无课堂记录，请先上传课堂图片或视频进行分析。'
  }

  const attendance = toNumber(overview.value.avg_attendance)
  const participation = toNumber(overview.value.avg_participation)
  const abnormal = toNumber(overview.value.avg_abnormal)
  const topBehavior = getTopBehavior(behavior.value)

  const parts = []

  if (attendance >= 90) {
    parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，整体出勤情况良好。`)
  } else if (attendance >= 75) {
    parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，出勤情况基本正常，但仍有提升空间。`)
  } else {
    parts.push(`当前共分析 ${total} 条课堂记录，平均到课率为 ${formatRate(attendance)}%，出勤情况偏低，建议重点关注缺勤或迟到情况。`)
  }

  if (participation >= 60) {
    parts.push(`平均参与率为 ${formatRate(participation)}%，学生课堂参与度较高，互动状态较好。`)
  } else if (participation >= 40) {
    parts.push(`平均参与率为 ${formatRate(participation)}%，学生课堂参与度处于中等水平，建议适当增加提问、讨论或随堂互动。`)
  } else {
    parts.push(`平均参与率为 ${formatRate(participation)}%，课堂活跃度偏低，建议通过提问、巡视、分组讨论等方式提升学生参与度。`)
  }

  if (abnormal >= 25) {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂分心现象较明显，需要重点关注手机使用、低头、趴桌等行为。`)
  } else if (abnormal >= 15) {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，存在一定分心现象，建议教师在课堂中加强提醒和巡视。`)
  } else {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂纪律整体较稳定。`)
  }

  if (topBehavior) {
    const topValue = toNumber(topBehavior.value ?? topBehavior.count)
    parts.push(`从行为分布看，"${topBehavior.name}"出现次数最多，数量为 ${topValue}，是当前课堂中的主要行为类型。`)
  }

  parts.push('综合建议：后续可结合检测结果关注后排、角落和遮挡区域学生状态，并通过课堂互动、巡视提醒和任务驱动方式提升课堂参与度。')

  return parts.join('')
})

async function loadDashboard() {
  overview.value = await getOverview()
  behavior.value = await getBehaviorSummary()
}

async function loadFilteredTrend() {
  if (trendCourseId.value && trendClassId.value) {
    trend.value = await getTrendByClassCourse(trendCourseId.value, trendClassId.value)
  } else {
    trend.value = []
  }
}

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}

function onClassChange(id) {
  const cls = classes.value.find(x => x.id === id)
  if (cls) form.value.expected_count = cls.expected_count
}

async function submit() {
  if (!file.value) return ElMessage.warning('请先选择文件')
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    Object.entries(form.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') fd.append(k, v)
    })
    result.value = await uploadAnalyze(fd)
    ElMessage.success('分析完成')
    await loadDashboard()
    await loadFilteredTrend()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  courses.value = await getCourses()
  classes.value = await getClasses()
  await loadDashboard()
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

.analysis-card {
  margin-top: 18px;
}

.analysis-content {
  font-size: 15px;
  line-height: 1.9;
  color: #303133;
  text-align: justify;
  white-space: pre-line;
  text-indent: 2em;
}
</style>