<template>
  <div class="grid grid-2">
    <el-card class="card">
      <template #header>上传课堂图片或视频</template>
      <el-form label-width="100px">
        <el-form-item label="上课日期">
          <el-date-picker v-model="form.analysis_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-select v-model="form.time_slot" placeholder="第几节课" style="width:100%">
            <el-option v-for="n in 9" :key="n" :label="'第'+n+'节'" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课地点">
          <el-input v-model="form.location" placeholder="如：教学楼A301" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload ref="uploadRef" drag :auto-upload="false" :limit="1" :on-change="onFileChange">
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
      <img v-if="result.result_path && isImageResult" class="result-image" :src="'/' + result.result_path" style="margin-top:16px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadAnalyze } from '../api'

const uploadRef = ref(null)
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const form = ref({ analysis_date: '', time_slot: 1, location: '' })

const isImageResult = computed(() => {
  const p = result.value?.result_path || ''
  return /\.(jpg|jpeg|png|webp|bmp)$/i.test(p)
})

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}
async function submit() {
  if (!form.value.analysis_date) return ElMessage.warning('请选择上课日期')
  if (!form.value.location) return ElMessage.warning('请输入上课地点')
  if (!file.value) return ElMessage.warning('请先选择文件')
  loading.value = true
  result.value = null
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('analysis_date', form.value.analysis_date)
    fd.append('time_slot', form.value.time_slot)
    fd.append('location', form.value.location)
    result.value = await uploadAnalyze(fd)
    ElMessage.success('分析完成')
    file.value = null
    uploadRef.value?.clearFiles()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>