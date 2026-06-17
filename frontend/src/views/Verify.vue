<template>
  <div class="auth-page">
    <div class="auth-card" style="text-align:center">
      <el-icon :size="60" v-if="status==='loading'" class="is-loading"><Loading /></el-icon>
      <el-icon :size="60" v-else-if="status==='ok'" style="color:#67c23a"><CircleCheckFilled /></el-icon>
      <el-icon :size="60" v-else style="color:#f56c6c"><CircleCloseFilled /></el-icon>
      <h2 style="margin-top:20px">{{ message }}</h2>
      <el-button v-if="status==='ok'" type="primary" @click="$router.push('/login')" style="margin-top:20px">
        前往登录
      </el-button>
      <el-button v-else-if="status==='fail'" @click="$router.push('/register')" style="margin-top:20px">
        返回注册
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import http from '../api/http'

const route = useRoute()
const status = ref('loading')
const message = ref('正在验证邮箱...')

onMounted(async () => {
  try {
    const res = await http.get('/api/auth/verify', { params: { token: route.query.token } })
    status.value = 'ok'
    message.value = res.message
  } catch (e) {
    status.value = 'fail'
    message.value = e.message
  }
})
</script>