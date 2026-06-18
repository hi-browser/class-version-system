<template>
  <el-card class="card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>班级管理</span>
        <el-button v-if="isAdmin" type="primary" @click="open()">添加班级</el-button>
      </div>
    </template>
    <el-table :data="rows">
      <el-table-column prop="course_name" label="课程名称" />
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

  <el-dialog v-model="visible" title="班级信息">
    <el-form label-width="90px">
      <el-form-item label="课程名称">
        <el-input v-model="form.course_name" placeholder="如：高等数学" />
      </el-form-item>
      <el-form-item label="任课教师">
        <el-select v-model="form.teacher_id" placeholder="选择教师" style="width:100%">
          <el-option v-for="t in teachers" :key="t.id" :label="t.name + ' (' + t.email + ')'" :value="t.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班级人数">
        <el-input-number v-model="form.student_count" :min="0" />
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
}
function open(row) {
  form.value = row ? { ...row } : { course_name: '', teacher_id: null, student_count: 0 }
  visible.value = true
}
async function save() {
  if (form.value.id) {
    await updateClass(form.value.id, form.value)
  } else {
    await createClass(form.value)
  }
  visible.value = false
  await load()
}
async function remove(id) { await deleteClass(id); await load() }
onMounted(load)
</script>