<template>
  <el-container class="layout">
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
        <el-menu-item index="/upload"><el-icon><Upload /></el-icon><span>上传分析</span></el-menu-item>
        <el-menu-item index="/history"><el-icon><Clock /></el-icon><span>历史课堂</span></el-menu-item>
        <el-menu-item index="/courses"><el-icon><Reading /></el-icon><span>课程管理</span></el-menu-item>
        <el-menu-item index="/classes"><el-icon><School /></el-icon><span>班级管理</span></el-menu-item>
        <el-menu-item index="/categories"><el-icon><Collection /></el-icon><span>行为类别</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="page-title">{{ $route.meta.title }}</div>
        <div class="user">教师端 · PC访问</div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
