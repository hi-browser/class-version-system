import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import SessionHistory from '../views/SessionHistory.vue'
import CourseManage from '../views/CourseManage.vue'
import ClassManage from '../views/ClassManage.vue'
import BehaviorCategories from '../views/BehaviorCategories.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: '数据看板' } },
  { path: '/history', component: SessionHistory, meta: { title: '历史课堂' } },
  { path: '/courses', component: CourseManage, meta: { title: '课程管理' } },
  { path: '/classes', component: ClassManage, meta: { title: '班级管理' } },
  { path: '/categories', component: BehaviorCategories, meta: { title: '行为类别' } }
]

export default createRouter({
  history: createWebHistory(),
  routes
})