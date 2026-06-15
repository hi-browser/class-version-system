<template>
  <div>
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

    <div class="grid grid-2" style="margin-top:18px">
      <el-card class="card chart-card">
        <template #header>行为占比分布</template>
        <EChart :option="pieOption" />
      </el-card>
      <el-card class="card chart-card">
        <template #header>出勤与参与趋势</template>
        <EChart :option="lineOption" />
      </el-card>
    </div>

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
import EChart from '../components/EChart.vue'
import { getOverview, getBehaviorSummary, getAttendanceTrend } from '../api'

const overview = ref({})
const behavior = ref([])
const trend = ref([])

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
    textStyle: {
      fontSize: 12
    }
  },
  series: [
    {
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
        formatter: params => {
          // 占比很小的行为不在外侧显示文字，避免标签堆叠；仍可在图例和 tooltip 中查看。
          if (params.percent < 5) return ''
          return params.name
        },
        fontSize: 12,
        lineHeight: 16
      },
      labelLine: {
        show: true,
        length: 14,
        length2: 18,
        smooth: true
      },
      labelLayout: {
        hideOverlap: true,
        moveOverlap: 'shiftY'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          formatter: '{b}\n{d}%'
        }
      }
    }
  ]
}))

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: {
    data: ['到课率', '参与率', '异常率'],
    top: 0
  },
  grid: {
    left: 45,
    right: 24,
    top: 48,
    bottom: 42
  },
  xAxis: {
    type: 'category',
    data: trend.value.map(x => x.time),
    axisLabel: {
      hideOverlap: true
    }
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
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
    return '暂无课堂记录，暂时无法生成分析结论。请先完成至少一次课堂图片或视频分析。'
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

  if (abnormal >= 30) {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂分心现象较明显，需要重点关注手机使用、低头、趴桌等行为。`)
  } else if (abnormal >= 15) {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，存在一定分心现象，建议教师在课堂中加强提醒和巡视。`)
  } else {
    parts.push(`异常行为率为 ${formatRate(abnormal)}%，课堂纪律整体较稳定。`)
  }

  if (topBehavior) {
    const topValue = toNumber(topBehavior.value ?? topBehavior.count)
    parts.push(`从行为分布看，“${topBehavior.name}”出现次数最多，数量为 ${topValue}，是当前课堂中的主要行为类型。`)
  }

  parts.push('综合建议：后续可结合检测结果关注后排、角落和遮挡区域学生状态，并通过课堂互动、巡视提醒和任务驱动方式提升课堂参与度。')

  return parts.join('')
})

onMounted(async () => {
  overview.value = await getOverview()
  behavior.value = await getBehaviorSummary()
  trend.value = await getAttendanceTrend()
})
</script>

<style scoped>
.chart-card :deep(.echarts),
.chart-card :deep(.chart) {
  min-height: 420px;
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
