<template>
  <el-card class="card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>班级管理</span>
        <el-button type="primary" @click="open()">添加班级</el-button>
      </div>
    </template>
    <el-table :data="rows">
      <el-table-column prop="class_name" label="班级名称" />
      <el-table-column prop="expected_count" label="应到人数" />
      <el-table-column prop="major" label="专业" />
      <el-table-column prop="grade" label="年级" />
      <el-table-column label="操作" width="150">
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
    </el-form>
    <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getClasses, createClass, updateClass, deleteClass } from '../api'
const rows = ref([])
const visible = ref(false)
const form = ref({})
async function load(){ rows.value = await getClasses() }
function open(row){ form.value = row ? {...row} : {class_name:'', expected_count:0, major:'', grade:''}; visible.value = true }
async function save(){ form.value.id ? await updateClass(form.value.id, form.value) : await createClass(form.value); visible.value=false; load() }
async function remove(id){ await deleteClass(id); load() }
onMounted(load)
</script>
