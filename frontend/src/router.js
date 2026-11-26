import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import AssociationView from './views/AssociationView.vue'
import QuestionBankView from './views/QuestionBankView.vue'
import AbilityView from './views/AbilityView.vue'
import TrainingView from './views/TrainingView.vue'
import ContestView from './views/ContestView.vue'
import RoadmapView from './views/RoadmapView.vue'

const routes = [
  { path: '/', name: 'dashboard', component: DashboardView, meta: { title: '系统总览看板' } },
  { path: '/association', name: 'association', component: AssociationView, meta: { title: '协会管理中心' } },
  { path: '/question-bank', name: 'question-bank', component: QuestionBankView, meta: { title: '算法题库管理' } },
  { path: '/ability', name: 'ability', component: AbilityView, meta: { title: '个人能力评估' } },
  { path: '/training', name: 'training', component: TrainingView, meta: { title: '训练与集训管理' } },
  { path: '/contest', name: 'contest', component: ContestView, meta: { title: '队伍与竞赛管理' } },
  { path: '/roadmap', name: 'roadmap', component: RoadmapView, meta: { title: '项目里程碑与交付总览' } }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
