<template>
  <div v-if="$route.meta.noAuth" class="auth-only">
    <router-view />
  </div>
  <el-container v-else class="layout">
    <el-aside width="240px" class="side">
      <div class="brand">
        <div class="logo">CV</div>
        <div>
          <h2>智慧课堂分析</h2>
          <p>Classroom Vision</p>
        </div>
      </div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item index="/dashboard"><el-icon><DataAnalysis /></el-icon><span>数据看板</span></el-menu-item>
        <el-menu-item index="/history"><el-icon><Clock /></el-icon><span>历史课堂</span></el-menu-item>
        <el-menu-item index="/courses"><el-icon><Reading /></el-icon><span>课程管理</span></el-menu-item>
        <el-menu-item index="/classes"><el-icon><School /></el-icon><span>班级管理</span></el-menu-item>
        <el-menu-item v-if="userRole === 'admin'" index="/categories"><el-icon><Collection /></el-icon><span>行为类别</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="page-title">{{ $route.meta.title }}</div>
        <div class="user">
          <span v-if="userName">{{ userName }}</span>
          <el-tag size="small" :type="userRole === 'admin' ? 'danger' : 'success'" style="margin: 0 8px">{{ userRole === 'admin' ? '管理员' : '教师' }}</el-tag>
          <el-button type="danger" text size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const userName = ref('')
const userRole = ref('')

watch(
  () => route.path,
  () => {
    const user = localStorage.getItem('user')
    if (user) {
      const parsed = JSON.parse(user)
      userName.value = parsed.name || parsed.email
      userRole.value = parsed.role || 'teacher'
    }
  },
  { immediate: true }
)

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.replace('/login')
}
</script>

<style scoped>
.auth-only {
  min-height: 100vh;
}
</style>