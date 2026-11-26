<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">ICPC</div>
        <div>
          <div class="brand-title">ICPC 实验室管理系统</div>
          <div class="brand-sub">Kcat · SDD 规范驱动</div>
        </div>
      </div>

      <div class="nav-group-label">总览</div>
      <router-link to="/" class="nav-item">
        <span>系统总览看板</span>
        <span class="nav-pill">100%</span>
      </router-link>

      <div class="nav-group-label">已交付核心模块 (Sprint 1-4)</div>
      <router-link to="/association" class="nav-item">
        <span>协会管理中心</span>
        <span class="nav-pill">FR-AM</span>
      </router-link>
      <router-link to="/question-bank" class="nav-item">
        <span>算法题库管理</span>
        <span class="nav-pill">FR-QB</span>
      </router-link>
      <router-link to="/ability" class="nav-item">
        <span>个人能力评估</span>
        <span class="nav-pill">FR-AB</span>
      </router-link>
      <router-link to="/training" class="nav-item">
        <span>训练与集训管理</span>
        <span class="nav-pill">FR-TRN</span>
      </router-link>
      <router-link to="/contest" class="nav-item">
        <span>队伍与竞赛管理</span>
        <span class="nav-pill">FR-TEAM</span>
      </router-link>

      <div class="nav-group-label">项目交付</div>
      <router-link to="/roadmap" class="nav-item">
        <span>里程碑与交付总览</span>
        <span class="nav-pill">v1.0.0</span>
      </router-link>

      <div class="sidebar-footer">
        <div style="display:flex;justify-content:space-between;color:#e2e8f0;font-weight:600;">
          <span>阶段进度</span>
          <span>100%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:100%"></div>
        </div>
        <div style="margin-top:8px;font-size:11px;line-height:1.4;">
          架构：Vue 3 + FastAPI + SQLite<br />
          版本：v1.0.0 正式版
        </div>
      </div>
    </aside>

    <div class="main-area">
      <header class="topbar">
        <div class="topbar-title">{{ currentTitle }}</div>
        <div class="topbar-meta">
          <span class="badge badge-blue">Scrum + SDD</span>
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
            Swagger API 文档 ↗
          </a>
        </div>
      </header>

      <main class="content">
        <router-view @notify="showToast" />
      </main>
    </div>

    <div v-if="toast.show" :class="['toast', toast.type === 'err' ? 'toast-err' : 'toast-ok']">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTitle = computed(() => route.meta?.title || 'ICPC 实验室管理系统')

const toast = reactive({ show: false, message: '', type: 'ok' })
let timer = null

function showToast({ message, type = 'ok' }) {
  toast.message = message
  toast.type = type
  toast.show = true
  clearTimeout(timer)
  timer = setTimeout(() => {
    toast.show = false
  }, 3200)
}
</script>
