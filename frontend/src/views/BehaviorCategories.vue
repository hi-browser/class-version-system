<template>
  <el-card class="card">
    <template #header>行为类别说明</template>
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
    </el-table>
  </el-card>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getBehaviorCategories } from '../api'
const rows = ref([])
onMounted(async () => { rows.value = await getBehaviorCategories() })
</script>
