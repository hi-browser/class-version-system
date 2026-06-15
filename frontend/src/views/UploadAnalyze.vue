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
      <img v-if="result.result_path && isImageResult" class="result-image" :src="'/' + result.result_path" style="margin-top:16px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCourses, getClasses, uploadAnalyze } from '../api'

const courses = ref([])
const classes = ref([])
const file = ref(null)
const loading = ref(false)
const result = ref(null)
const form = ref({ course_id: null, class_id: null, expected_count: 0, session_time: '' })

const isImageResult = computed(() => {
  const p = result.value?.result_path || ''
  return /\.(jpg|jpeg|png|webp|bmp)$/i.test(p)
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
