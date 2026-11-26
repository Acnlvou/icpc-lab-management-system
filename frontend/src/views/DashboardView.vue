<template>
  <div v-if="overview">
    <div class="grid-4" style="margin-bottom:18px;">
      <div class="kpi-card">
        <div class="kpi-label">协会在册会员</div>
        <div class="kpi-value" style="color:#2563eb;">{{ overview.kpi.total_members }}</div>
        <div class="kpi-sub">
          正式 {{ overview.kpi.formal_members }}（竞赛 {{ overview.kpi.competition_members }} / 非竞赛 {{ overview.kpi.non_competition_members }}）· 备选 {{ overview.kpi.candidate_members }}
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">待审核 / 观察预警</div>
        <div class="kpi-value" style="color:#d97706;">
          {{ overview.kpi.pending_applications }} / {{ overview.kpi.observation_members }}
        </div>
        <div class="kpi-sub">
          待清退预警 {{ overview.kpi.dismissal_pending }} 人（BR-003 自动状态机）
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">多标签算法题库</div>
        <div class="kpi-value" style="color:#059669;">{{ overview.kpi.total_problems }}</div>
        <div class="kpi-sub">
          覆盖 {{ overview.kpi.total_tags }} 个知识点/能力标签 · {{ overview.kpi.total_lists }} 套专题题单
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">个人能力评估记录</div>
        <div class="kpi-value" style="color:#7c3aed;">{{ overview.kpi.total_ability_assessments }}</div>
        <div class="kpi-sub">六维能力画像与薄弱项补强闭环 (BR-005)</div>
      </div>
    </div>

    <div class="grid-4" style="margin-bottom:18px;">
      <div class="kpi-card">
        <div class="kpi-label">训练计划 / 周任务</div>
        <div class="kpi-value" style="color:#2563eb;">{{ overview.kpi.total_training_plans || 0 }} / {{ overview.kpi.total_training_tasks || 0 }}</div>
        <div class="kpi-sub">个人补强计划与打卡考勤闭环 (BR-007)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">寒暑假集训</div>
        <div class="kpi-value" style="color:#0ea5e9;">{{ overview.kpi.total_training_camps || 0 }}</div>
        <div class="kpi-sub">寒假 / 暑假多校集训看板 (FR-WIN/SUM)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">队伍档案</div>
        <div class="kpi-value" style="color:#7c3aed;">{{ overview.kpi.total_teams || 0 }}</div>
        <div class="kpi-sub">能力互补组队与调整流水 (BR-008)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">校赛 / XCPC 赛事</div>
        <div class="kpi-value" style="color:#059669;">{{ overview.kpi.total_school_contests || 0 }} / {{ overview.kpi.total_xcpc || 0 }}</div>
        <div class="kpi-sub">校赛晋级候补递补 + 成绩归档 (BR-009/010)</div>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:18px;">
      <div class="card">
        <div class="card-title">
          <span>Scrum + SDD 迭代进度总览（当前 {{ overview.progress.overall_percent }}%）</span>
          <span class="badge badge-blue">{{ overview.progress.milestone }}</span>
        </div>
        <div class="progress-bar-light" style="margin-bottom:16px;">
          <div class="progress-fill" :style="{ width: overview.progress.overall_percent + '%' }"></div>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div
            v-for="m in overview.progress.modules"
            :key="m.name"
            style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-radius:8px;background:#f8fafc;"
          >
            <div>
              <strong style="font-size:13px;">{{ m.name }}</strong>
              <span style="font-size:12px;color:#64748b;margin-left:8px;">{{ m.sprint }}</span>
            </div>
            <span :class="['badge', m.status === '已完成' ? 'badge-green' : 'badge-gray']">
              {{ m.status }}
            </span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>题库综合难度分布（与知识点分离维护 BR-006）</span>
          <router-link to="/question-bank" class="btn btn-sm">进入题库 →</router-link>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;margin-top:10px;">
          <div v-for="item in overview.difficulty_distribution" :key="item.difficulty">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
              <strong>{{ item.difficulty }}</strong>
              <span style="color:#64748b;">{{ item.count }} 题</span>
            </div>
            <div class="progress-bar-light">
              <div
                class="progress-fill"
                :style="{ width: Math.min(100, (item.count / Math.max(1, overview.kpi.total_problems)) * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">
          <span>协会通知公告（FR-SYS-002）</span>
          <button class="btn btn-primary btn-sm" @click="showAnnModal = true">+ 发布公告</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;">
          <div
            v-for="ann in overview.announcements"
            :key="ann.id"
            style="padding:12px;border:1px solid #e2e8f0;border-radius:10px;"
          >
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
              <strong style="font-size:14px;">{{ ann.title }}</strong>
              <span class="badge badge-blue">{{ ann.category }}</span>
            </div>
            <p style="margin:6px 0;font-size:13px;color:#475569;">{{ ann.content }}</p>
            <div style="font-size:11px;color:#94a3b8;">
              面向对象：{{ ann.audience }} · 发布方：{{ ann.publisher }} · {{ formatTime(ann.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>近期业务操作审计日志（FR-SYS-003）</span>
          <span class="badge badge-gray">历史可追溯</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>模块</th>
                <th>操作与对象</th>
                <th>摘要</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lg in overview.recent_logs" :key="lg.id">
                <td><span class="badge badge-purple">{{ lg.module }}</span></td>
                <td>
                  <strong>{{ lg.action }}</strong>
                  <div style="font-size:12px;color:#64748b;">{{ lg.target }}</div>
                </td>
                <td style="font-size:12px;color:#475569;">{{ lg.detail }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showAnnModal" class="modal-mask" @click.self="showAnnModal = false">
      <div class="modal-box">
        <div class="card-title">
          <span>发布协会通知公告</span>
          <button class="btn btn-sm" @click="showAnnModal = false">关闭</button>
        </div>
        <div class="form-grid">
          <div class="form-field full">
            <label>公告标题</label>
            <input v-model="annForm.title" class="input" placeholder="如：本周六模拟赛及题单补题通知" />
          </div>
          <div class="form-field">
            <label>分类</label>
            <select v-model="annForm.category" class="select">
              <option>协会事务</option>
              <option>训练安排</option>
              <option>考核通知</option>
              <option>赛事报名</option>
            </select>
          </div>
          <div class="form-field">
            <label>面向对象</label>
            <input v-model="annForm.audience" class="input" placeholder="全体会员 / 竞赛会员 / 备选会员" />
          </div>
          <div class="form-field full">
            <label>公告内容</label>
            <textarea v-model="annForm.content" class="textarea" placeholder="请输入详细通知事项..."></textarea>
          </div>
        </div>
        <div style="margin-top:16px;display:flex;justify-content:flex-end;gap:10px;">
          <button class="btn" @click="showAnnModal = false">取消</button>
          <button class="btn btn-primary" @click="submitAnnouncement">确认发布</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const emit = defineEmits(['notify'])
const overview = ref(null)
const showAnnModal = ref(false)
const annForm = reactive({
  title: '',
  category: '训练安排',
  audience: '全体会员',
  content: '',
  publisher: '协会秘书处'
})

async function loadData() {
  try {
    overview.value = await api.getOverview()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitAnnouncement() {
  if (!annForm.title.trim() || !annForm.content.trim()) {
    emit('notify', { message: '请填写完整的公告标题和内容', type: 'err' })
    return
  }
  try {
    await api.createAnnouncement({ ...annForm })
    showAnnModal.value = false
    annForm.title = ''
    annForm.content = ''
    emit('notify', { message: '公告发布成功并已写入审计日志' })
    await loadData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function formatTime(t) {
  return t ? new Date(t).toLocaleString('zh-CN') : ''
}

onMounted(loadData)
</script>
