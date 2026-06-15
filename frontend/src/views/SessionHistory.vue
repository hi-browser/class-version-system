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
          <el-button type="danger" size="small" @click="remove(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="detailVisible" title="课堂分析详情" width="80%">
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

      <div v-if="detail.result_path">
        <h3>检测结果图</h3>
        <img
          :src="imageUrl(detail.result_path)"
          style="width: 100%; max-height: 600px; object-fit: contain; border-radius: 8px;"
        />
      </div>

      <div v-else>
        暂无检测结果图
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getSessions, deleteSession, getSessionAnalysis } from '../api'

const rows = ref([])
const detailVisible = ref(false)
const detail = ref(null)

async function load() {
  rows.value = await getSessions()
}

async function remove(id) {
  await ElMessageBox.confirm('确定删除该课堂记录吗？')
  await deleteSession(id)
  ElMessage.success('删除成功')
  await load()
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

onMounted(load)
</script>