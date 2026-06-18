<template>
  <div class="grid grid-2">
    <el-card class="card">
      <template #header>上传课堂图片或视频</template>
      <el-form label-width="100px">
        <el-form-item label="课程">
          <el-select v-model="form.course_id" placeholder="请选择课程" style="width:100%">
            <el-option v-for="c in courses" :key="c.id" :label="c.course_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class_id" placeholder="请选择班级" style="width:100%" @change="onClassChange">
            <el-option v-for="c in classes" :key="c.id" :label="c.class_name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="应到人数">
          <el-input-number v-model="form.expected_count" :min="0" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-date-picker v-model="form.session_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload drag :auto-upload="false" :limit="1" :on-change="onFileChange">
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

    <el-card class="card" v-if="result">
      <template #header>分析结果</template>
      <div class="grid grid-2">
        <div class="metric"><div class="label">检测人数</div><div class="value">{{ result.detected_count }}</div></div>
        <div class="metric"><div class="label">到课率</div><div class="value">{{ result.attendance_rate }}%</div></div>
        <div class="metric"><div class="label">参与率</div><div class="value">{{ result.participation_rate }}%</div></div>
        <div class="metric"><div class="label">异常率</div><div class="value">{{ result.abnormal_rate }}%</div></div>
      </div>
      <el-table :data="result.behavior_counts" style="margin-top:16px">
        <el-table-column prop="name" label="行为类别" />
        <el-table-column prop="count" label="数量" />
        <el-table-column prop="rate" label="占比(%)" />
      </el-table>
      <img v-if="result.result_path && !isVideoResult" class="result-image" :src="'/' + result.result_path" style="margin-top:16px" />

      <div v-if="isVideoResult && result.result_video_path" class="grid grid-2" style="margin-top:16px">
        <div>
          <h4>原视频</h4>
          <video :src="originalVideoUrl" controls style="width:100%; border-radius: 4px;"></video>
        </div>
        <div>
          <h4>标注后视频</h4>
          <video :src="annotatedVideoUrl" controls style="width:100%; border-radius: 4px;"></video>
        </div>
      </div>

      <div v-if="result.trend && result.trend.length > 0 && activeBehaviors.length > 0" style="margin-top:16px">
        <h3>行为趋势</h3>
        <EChart :option="behaviorTrendOption" class="chart" />
      </div>

      <div v-if="result.analysis_text" class="analysis-content" style="margin-top:16px">
        <h3>智能分析</h3>
        <p>{{ result.analysis_text }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCourses, getClasses, uploadAnalyze } from '../api'
import EChart from '../components/EChart.vue'

const BEHAVIOR_NAMES = {
  0: '举手互动',
  1: '阅读/看书',
  2: '低头书写',
  3: '使用手机',
  4: '低头状态',
  5: '趴桌/疑似睡觉',
}

const courses = ref([])
const classes = ref([])
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const form = ref({ course_id: null, class_id: null, expected_count: 0, session_time: '' })

const isVideoResult = computed(() => {
  return result.value?.source_type === 'video'
})

const originalVideoUrl = computed(() => {
  if (!result.value?.source_path) return ''
  const p = result.value.source_path.replace(/\\/g, '/')
  if (/app\/static\/uploads\//.test(p)) {
    return '/' + p.replace('app/static/', 'static/')
  }
  return ''
})

const annotatedVideoUrl = computed(() => {
  if (!result.value?.result_video_path) return ''
  return '/' + result.value.result_video_path
})

const activeBehaviors = computed(() => {
  if (!result.value?.trend) return []
  const ids = new Set()
  for (const point of result.value.trend) {
    if (!point.behaviors) continue
    for (const [key, val] of Object.entries(point.behaviors)) {
      if (val > 0) ids.add(key)
    }
  }
  return [...ids].sort()
})

const behaviorTrendOption = computed(() => {
  if (!result.value?.trend || activeBehaviors.value.length === 0) return {}
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#fc8452']
  return {
    tooltip: { trigger: 'axis' },
    legend: {
      data: activeBehaviors.value.map(id => BEHAVIOR_NAMES[id] || `类别${id}`),
      top: 0,
    },
    grid: { left: 45, right: 24, top: 48, bottom: 80 },
    xAxis: {
      type: 'category',
      data: result.value.trend.map(p => p.time + 's'),
      axisLabel: { hideOverlap: true },
    },
    yAxis: { type: 'value', minInterval: 1 },
    dataZoom: [
      { type: 'slider', start: 0, end: 100, height: 20, bottom: 50 },
      { type: 'inside', start: 0, end: 100 },
    ],
    series: activeBehaviors.value.map((id, idx) => ({
      name: BEHAVIOR_NAMES[id] || `类别${id}`,
      type: 'line',
      smooth: true,
      data: result.value.trend.map(p => (p.behaviors && p.behaviors[id]) || 0),
      color: colors[idx % colors.length],
    })),
  }
})

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}
function onClassChange(id) {
  const cls = classes.value.find(x => x.id === id)
  if (cls) form.value.expected_count = cls.expected_count
}
async function submit() {
  if (!file.value) return ElMessage.warning('请先选择文件')
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    Object.entries(form.value).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') fd.append(k, v)
    })
    result.value = await uploadAnalyze(fd)
    ElMessage.success('分析完成')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
onMounted(async () => {
  courses.value = await getCourses()
  classes.value = await getClasses()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
}
.analysis-content p {
  font-size: 15px;
  line-height: 1.9;
  color: #303133;
  text-align: justify;
  text-indent: 2em;
}
</style>