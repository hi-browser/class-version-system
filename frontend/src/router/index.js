import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SessionHistory from '../views/SessionHistory.vue'
import CourseManage from '../views/CourseManage.vue'
import ClassManage from '../views/ClassManage.vue'
import BehaviorCategories from '../views/BehaviorCategories.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Verify from '../views/Verify.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login, meta: { title: '登录', noAuth: true } },
  { path: '/register', component: Register, meta: { title: '注册', noAuth: true } },
  { path: '/verify', component: Verify, meta: { title: '邮箱验证', noAuth: true } },
  { path: '/dashboard', component: Dashboard, meta: { title: '数据看板' } },
  { path: '/history', component: SessionHistory, meta: { title: '历史课堂' } },
  { path: '/courses', component: CourseManage, meta: { title: '课程管理' } },
  { path: '/classes', component: ClassManage, meta: { title: '班级管理' } },
  { path: '/categories', component: BehaviorCategories, meta: { title: '行为类别' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else if (to.meta.noAuth && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router