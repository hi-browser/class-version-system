<template>
  <el-card class="card">
    <template #header>历史课堂记录</template>

    <el-table :data="rows" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="source_type" label="类型" width="90" />
      <el-table-column prop="detected_count" label="检测人数" />
      <el-table-column prop="expected_count" label="应到人数" />
      <el-table-column prop="attendance_rate" label="到课率(%)" />
      <el-table-column prop="participation_rate" label="参与率(%)" />
      <el-table-column prop="abnormal_rate" label="异常率(%)" />
      <el-table-column prop="created_at" label="创建时间" width="190" />

      <el-table-column label="操作" width="190">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showDetail(row)">
            查看详情
          </el-button>
          <el-button v-if="isAdmin" type="danger" size="small" @click="remove(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="detailVisible" title="课堂分析详情" width="85%" @opened="onDialogOpened">
    <div v-if="detail">
      <div class="grid grid-4" style="margin-bottom: 16px">
        <div class="metric">
          <div class="label">检测人数</div>
          <div class="value">{{ detail.detected_count }}</div>
        </div>
        <div class="metric">
          <div class="label">到课率</div>
          <div class="value">{{ detail.attendance_rate }}%</div>
        </div>
        <div class="metric">
          <div class="label">参与率</div>
          <div class="value">{{ detail.participation_rate }}%</div>
        </div>
        <div class="metric">
          <div class="label">异常率</div>
          <div class="value">{{ detail.abnormal_rate }}%</div>
        </div>
      </div>

      <el-table :data="detail.behavior_counts" style="margin-bottom: 16px">
        <el-table-column prop="name" label="行为类别" />
        <el-table-column prop="count" label="数量" />
        <el-table-column prop="rate" label="占比(%)" />
      </el-table>

      <div v-if="detail.source_type === 'video' && detail.result_video_path" class="grid grid-2" style="margin-bottom: 16px">
        <div>
          <h3>原视频</h3>
          <video :src="videoUrl(detail.source_path)" controls style="width:100%; border-radius: 4px;"></video>
        </div>
        <div>
          <h3>标注后视频</h3>
          <video :src="'/' + detail.result_video_path" controls style="width:100%; border-radius: 4px;"></video>
        </div>
      </div>

      <div v-if="detail.trend && detail.trend.length > 0 && activeBehaviors.length > 0" style="margin-bottom: 16px">
        <h3>行为趋势</h3>
        <EChart :option="behaviorTrendOption" class="chart" />
      </div>

      <div v-if="detail.analysis_text" class="analysis-content" style="margin-bottom: 16px">
        <h3>智能分析</h3>
        <p>{{ detail.analysis_text }}</p>
      </div>

      <div v-if="detail.result_path && detail.source_type !== 'video'">
        <h3>检测结果图</h3>
        <img
          :src="imageUrl(detail.result_path)"
          style="width: 100%; max-height: 600px; object-fit: contain; border-radius: 8px;"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
<<<<<<< HEAD
import { ref, computed, onMounted, nextTick } from 'vue'
=======
import { ref, onMounted, computed } from 'vue'
>>>>>>> gitee/ysy-frontend-checkversiontest
import { ElMessageBox, ElMessage } from 'element-plus'
import { getSessions, deleteSession, getSessionAnalysis } from '../api'
import EChart from '../components/EChart.vue'

const BEHAVIOR_NAMES = {
  0: '举手互动',
  1: '阅读/看书',
  2: '低头书写',
  3: '使用手机',
  4: '低头状态',
  5: '趴桌/疑似睡觉',
}

const rows = ref([])
const detailVisible = ref(false)
const detail = ref(null)

const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.role === 'admin'
})

async function load() {
  rows.value = await getSessions()
}

async function remove(id) {
  await ElMessageBox.confirm('确定删除该课堂记录吗？')
  await deleteSession(id)
  ElMessage.success('删除成功')
  await load()
}

const activeBehaviors = computed(() => {
  if (!detail.value?.trend) return []
  const ids = new Set()
  for (const point of detail.value.trend) {
    if (!point.behaviors) continue
    for (const [key, val] of Object.entries(point.behaviors)) {
      if (val > 0) ids.add(key)
    }
  }
  return [...ids].sort()
})

const behaviorTrendOption = computed(() => {
  if (!detail.value?.trend || activeBehaviors.value.length === 0) return {}
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
      data: detail.value.trend.map(p => p.time + 's'),
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
      data: detail.value.trend.map(p => (p.behaviors && p.behaviors[id]) || 0),
      color: colors[idx % colors.length],
    })),
  }
})

function videoUrl(path) {
  if (!path) return ''
  const p = path.replace(/\\/g, '/')
  if (/app\/static\/uploads\//.test(p)) {
    return '/' + p.replace('app/static/', 'static/')
  }
  return '/' + p
}

function imageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/')) return path
  if (path.startsWith('app/static/')) {
    return '/' + path.replace('app/static/', 'static/')
  }
  return '/' + path
}

async function showDetail(row) {
  try {
    detail.value = await getSessionAnalysis(row.id)
    detailVisible.value = true
  } catch (e) {
    ElMessage.error(e.message || '获取课堂详情失败')
  }
}

function onDialogOpened() {
  nextTick(() => {
    window.dispatchEvent(new Event('resize'))
  })
}

onMounted(load)
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