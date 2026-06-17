<template>
  <el-card class="card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>行为类别说明</span>
        <el-button type="primary" @click="open()">添加类别</el-button>
      </div>
    </template>
    <el-alert type="info" show-icon :closable="false" title="系统当前按照 SCB-Dataset3 六类行为进行统计：举手、阅读、写字、使用手机、低头、趴桌/疑似睡觉。" />
    <el-table :data="rows" style="margin-top:16px">
      <el-table-column prop="class_id" label="类别编号" />
      <el-table-column prop="code" label="英文编码" />
      <el-table-column prop="name_cn" label="中文名称" />
      <el-table-column prop="is_positive" label="是否参与行为">
        <template #default="{ row }">
          <el-tag :type="row.is_positive ? 'success' : 'danger'">{{ row.is_positive ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="行为类别">
    <el-form label-width="110px">
      <el-form-item label="类别编号"><el-input-number v-model="form.class_id" :min="0" /></el-form-item>
      <el-form-item label="英文编码"><el-input v-model="form.code" /></el-form-item>
      <el-form-item label="中文名称"><el-input v-model="form.name_cn" /></el-form-item>
      <el-form-item label="是否参与行为">
        <el-switch v-model="form.is_positive" />
      </el-form-item>
    </el-form>
    <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
  </el-dialog>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getBehaviorCategories } from '../api'
import http from '../api/http'

const rows = ref([])
const visible = ref(false)
const form = ref({})

async function load() {
  try { rows.value = await getBehaviorCategories() } catch {}
}

function open(row) {
  form.value = row ? { ...row } : { class_id: 0, code: '', name_cn: '', is_positive: true }
  visible.value = true
}

async function save() {
  if (form.value.id) {
    await http.put(`/api/behavior-categories/${form.value.id}`, form.value)
  } else {
    await http.post('/api/behavior-categories', form.value)
  }
  visible.value = false
  load()
}

async function remove(id) {
  await http.delete(`/api/behavior-categories/${id}`)
  load()
}

onMounted(load)
</script>