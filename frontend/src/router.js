import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import AssociationView from './views/AssociationView.vue'
import QuestionBankView from './views/QuestionBankView.vue'
import AbilityView from './views/AbilityView.vue'
import RoadmapView from './views/RoadmapView.vue'

const routes = [
  { path: '/', name: 'dashboard', component: DashboardView, meta: { title: '系统总览看板' } },
  { path: '/association', name: 'association', component: AssociationView, meta: { title: '协会管理中心' } },
  { path: '/question-bank', name: 'question-bank', component: QuestionBankView, meta: { title: '算法题库管理' } },
  { path: '/ability', name: 'ability', component: AbilityView, meta: { title: '个人能力评估' } },
  { path: '/roadmap', name: 'roadmap', component: RoadmapView, meta: { title: '后续迭代规划' } }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
