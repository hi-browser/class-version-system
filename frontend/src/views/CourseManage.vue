<template>
  <el-card class="card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>排课管理</span>
        <el-button v-if="isAdmin" type="primary" @click="open()">添加排课</el-button>
      </div>
    </template>
    <el-table :data="rows">
      <el-table-column prop="date" label="上课日期" />
      <el-table-column label="上课时间">
        <template #default="{ row }">第{{ row.time_slot }}节</template>
      </el-table-column>
      <el-table-column prop="location" label="上课地点" />
      <el-table-column prop="class_group_name" label="班级" />
      <el-table-column prop="teacher_name" label="任课教师" />
      <el-table-column prop="student_count" label="班级人数" />
      <el-table-column v-if="isAdmin" label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="排课信息" width="500px">
    <el-form label-width="90px">
      <el-form-item label="上课日期">
        <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
      </el-form-item>
      <el-form-item label="上课时间">
        <el-select v-model="form.time_slot" placeholder="第几节课" style="width:100%">
          <el-option v-for="n in 9" :key="n" :label="'第'+n+'节'" :value="n" />
        </el-select>
      </el-form-item>
      <el-form-item label="上课地点">
        <el-input v-model="form.location" placeholder="如：教学楼A301" />
      </el-form-item>
      <el-form-item label="班级">
        <el-select v-model="form.class_group_id" placeholder="选择班级" clearable style="width:100%">
          <el-option v-for="c in classGroups" :key="c.id" :label="c.course_name" :value="c.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getCourses, createCourse, updateCourse, deleteCourse, getClasses } from '../api'
const rows = ref([])
const classGroups = ref([])
const visible = ref(false)
const form = ref({})
const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.role === 'admin'
})
async function load(){
  rows.value = await getCourses()
  if (isAdmin.value) {
    try { classGroups.value = await getClasses() } catch {}
  }
}
function open(row){
  form.value = row ? { ...row } : { class_group_id: null, date: '', time_slot: 1, location: '' }
  visible.value = true
}
async function save(){
  const payload = {
    class_group_id: form.value.class_group_id || null,
    date: form.value.date,
    time_slot: form.value.time_slot,
    location: form.value.location,
  }
  try {
    if (form.value.id) {
      await updateCourse(form.value.id, payload)
    } else {
      await createCourse(payload)
    }
    visible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}
async function remove(id){ await deleteCourse(id); await load() }
onMounted(load)
</script>