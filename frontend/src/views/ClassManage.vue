<template>
  <el-card class="card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>班级管理</span>
        <el-button v-if="isAdmin" type="primary" @click="open()">添加班级</el-button>
      </div>
    </template>
    <el-table :data="rows">
      <el-table-column prop="class_name" label="班级名称" />
      <el-table-column prop="expected_count" label="应到人数" />
      <el-table-column prop="major" label="专业" />
      <el-table-column prop="grade" label="年级" />
      <el-table-column prop="teacher_name" label="授课教师" />
      <el-table-column v-if="isAdmin" label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="班级信息">
    <el-form label-width="90px">
      <el-form-item label="班级名称"><el-input v-model="form.class_name" /></el-form-item>
      <el-form-item label="应到人数"><el-input-number v-model="form.expected_count" :min="0" /></el-form-item>
      <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
      <el-form-item label="年级"><el-input v-model="form.grade" /></el-form-item>
      <el-form-item label="授课教师">
        <el-select v-model="form.teacher_id" placeholder="请选择教师" clearable style="width:100%">
          <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getClasses, createClass, updateClass, deleteClass, getTeachers } from '../api'
const rows = ref([])
const teachers = ref([])
const visible = ref(false)
const form = ref({})
const isAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.role === 'admin'
})
async function load() {
  rows.value = await getClasses()
  if (isAdmin.value) {
    try { teachers.value = await getTeachers() } catch {}
  }
  const teacherMap = {}
  teachers.value.forEach(t => { teacherMap[t.id] = t.name })
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
  rows.value = rows.value.map(c => ({ ...c, teacher_name: teacherMap[c.teacher_id] || (c.teacher_id === currentUser.id ? currentUser.name : '') }))
}
function open(row) {
  form.value = row ? { ...row } : { class_name: '', expected_count: 0, major: '', grade: '', teacher_id: null }
  visible.value = true
}
async function save() {
  const payload = { ...form.value }
  if (form.value.id) {
    await updateClass(form.value.id, payload)
  } else {
    await createClass(payload)
  }
  visible.value = false
  load()
}
async function remove(id) { await deleteClass(id); load() }
onMounted(load)
</script>