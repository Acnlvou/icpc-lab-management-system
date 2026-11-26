<template>
  <div>
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        :class="['tab-btn', { active: activeTab === t.key }]"
        @click="switchTab(t.key)"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- ============ Tab 1: 训练计划 ============ -->
    <div v-if="activeTab === 'plans'">
      <div class="card" style="margin-bottom:18px;">
        <div class="toolbar" style="margin-bottom:0;">
          <strong style="font-size:14px;">训练计划（整体节奏 + 个人补强 · BR-007 薄弱项驱动）：</strong>
          <select v-model="planFilter.plan_type" class="select" @change="loadPlans">
            <option value="">全部类型</option>
            <option value="OVERALL">整体训练计划</option>
            <option value="PERSONAL">个人补强计划</option>
          </select>
          <button class="btn btn-primary" style="margin-left:auto;" @click="openPlanModal">+ 新建训练计划</button>
        </div>
      </div>

      <div v-if="plans.length" class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>计划名称</th>
                <th>类型</th>
                <th>面向会员</th>
                <th>能力薄弱项快照 (BR-007)</th>
                <th>关联题单</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in plans" :key="p.id">
                <td>
                  <strong>{{ p.name }}</strong>
                  <div style="font-size:12px;color:#64748b;">{{ p.cycle }} · {{ p.description || '—' }}</div>
                </td>
                <td>
                  <span :class="['badge', p.plan_type === 'PERSONAL' ? 'badge-purple' : 'badge-blue']">
                    {{ p.plan_type === 'PERSONAL' ? '个人补强' : '整体训练' }}
                  </span>
                </td>
                <td>{{ p.member_name || '全体竞赛会员' }}</td>
                <td>
                  <span v-if="p.source_assessment_id" class="badge badge-amber">评估 #{{ p.source_assessment_id }}</span>
                  <span v-else style="font-size:12px;color:#94a3b8;">整体计划无评估快照</span>
                </td>
                <td>{{ p.problem_list_title || '—' }}</td>
                <td><span class="badge badge-green">{{ p.status || 'ACTIVE' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="card" style="text-align:center;padding:40px;color:#94a3b8;">
        暂无训练计划，点击右上角「新建训练计划」开始（个人计划将自动读取最近一次能力评估薄弱项）
      </div>
    </div>

    <!-- ============ Tab 2: 周任务打卡与考勤 ============ -->
    <div v-if="activeTab === 'tasks'">
      <div class="card" style="margin-bottom:18px;">
        <div class="toolbar" style="margin-bottom:0;">
          <strong style="font-size:14px;">周训练任务打卡与考勤（FR-TRN-003~006）：</strong>
          <button class="btn btn-primary" style="margin-left:auto;" @click="openTaskModal">+ 下发训练任务</button>
        </div>
      </div>

      <div v-if="tasks.length" class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>任务 / 周次</th>
                <th>指派会员</th>
                <th>关联题单</th>
                <th>补题进度</th>
                <th>考勤</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in tasks" :key="t.id">
                <td>
                  <strong>{{ t.title }}</strong>
                  <div style="font-size:12px;color:#64748b;">{{ t.week || '周任务' }}</div>
                </td>
                <td>{{ t.member_name || '—' }}</td>
                <td>{{ t.problem_list_title || '—' }}</td>
                <td style="min-width:150px;">
                  <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                    <span>{{ t.solved_count || 0 }} / {{ t.total_count || 0 }} 题</span>
                    <span style="color:#64748b;">{{ percent(t.solved_count, t.total_count) }}%</span>
                  </div>
                  <div class="progress-bar-light">
                    <div class="progress-fill" :style="{ width: percent(t.solved_count, t.total_count) + '%' }"></div>
                  </div>
                </td>
                <td>
                  <span :class="['badge', attendanceBadge(t.attendance)]">{{ attendanceLabel(t.attendance) }}</span>
                </td>
                <td><span :class="['badge', t.status === 'DONE' ? 'badge-green' : 'badge-amber']">{{ t.status || 'PENDING' }}</span></td>
                <td><button class="btn btn-sm" @click="openCheckinModal(t)">打卡 / 记录考勤</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="card" style="text-align:center;padding:40px;color:#94a3b8;">
        暂无训练任务，点击右上角「下发训练任务」关联专题题单
      </div>
    </div>

    <!-- ============ Tab 3: 寒暑假集训看板 ============ -->
    <div v-if="activeTab === 'camps'">
      <div class="card" style="margin-bottom:18px;">
        <div class="toolbar" style="margin-bottom:0;">
          <strong style="font-size:14px;">寒暑假集训与多校联训看板（FR-WIN / FR-SUM）：</strong>
          <select v-model="campFilter.camp_type" class="select" @change="loadCamps">
            <option value="">全部集训</option>
            <option value="WINTER">寒假集训</option>
            <option value="SUMMER">暑假多校集训</option>
          </select>
          <button class="btn btn-primary" style="margin-left:auto;" @click="openCampModal">+ 新建集训</button>
        </div>
      </div>

      <div v-if="camps.length" class="grid-3">
        <div v-for="c in camps" :key="c.id" class="card">
          <div class="card-title">
            <span>{{ c.name }}</span>
            <span :class="['badge', c.camp_type === 'WINTER' ? 'badge-blue' : 'badge-purple']">
              {{ c.camp_type === 'WINTER' ? '寒假' : '暑假' }}
            </span>
          </div>
          <div style="font-size:13px;color:#475569;line-height:1.9;">
            <div>周期：{{ c.term || '—' }}</div>
            <div>地点：{{ c.location || '—' }}</div>
            <div>关联队伍：{{ c.team_name || '—' }}（BR-008 队伍档案关联）</div>
            <div>时间：{{ c.start_date || '—' }} ~ {{ c.end_date || '—' }}</div>
            <div>状态：{{ c.status || 'ACTIVE' }}</div>
          </div>
          <div v-if="c.summary" style="margin-top:10px;padding:8px 10px;background:#f8fafc;border-radius:8px;font-size:12px;color:#334155;">
            <strong>集训总结：</strong>{{ c.summary }}
          </div>
          <button class="btn btn-sm" style="margin-top:12px;" @click="openSummaryModal(c)">记录集训总结</button>
        </div>
      </div>
      <div v-else class="card" style="text-align:center;padding:40px;color:#94a3b8;">
        暂无集训记录，点击右上角「新建集训」创建寒假/暑假集训计划
      </div>
    </div>

    <!-- ============ 新建训练计划弹窗 ============ -->
    <div v-if="showPlanModal" class="modal-mask" @click.self="showPlanModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新建训练计划（个人计划自动衔接能力评估薄弱项 BR-007）</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>计划名称</label><input v-model="planForm.name" class="input" /></div>
          <div class="form-field"><label>计划类型</label>
            <select v-model="planForm.plan_type" class="select">
              <option value="OVERALL">整体训练计划</option>
              <option value="PERSONAL">个人补强计划</option>
            </select>
          </div>
          <div class="form-field"><label>训练周期</label><input v-model="planForm.cycle" class="input" /></div>
          <div class="form-field" v-if="planForm.plan_type === 'PERSONAL'"><label>面向竞赛会员</label>
            <select v-model="planForm.member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}（{{ m.student_no }}）</option>
            </select>
          </div>
          <div class="form-field"><label>关联专题题单</label>
            <select v-model="planForm.problem_list_id" class="select">
              <option :value="null">暂不关联</option>
              <option v-for="pl in problemLists" :key="pl.id" :value="pl.id">{{ pl.title }}</option>
            </select>
          </div>
          <div class="form-field full"><label>计划说明</label><textarea v-model="planForm.description" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showPlanModal = false">取消</button>
          <button class="btn btn-primary" @click="submitPlan">创建计划</button>
        </div>
      </div>
    </div>

    <!-- ============ 下发训练任务弹窗 ============ -->
    <div v-if="showTaskModal" class="modal-mask" @click.self="showTaskModal = false">
      <div class="modal-box">
        <div class="card-title"><span>下发周训练任务（关联题库题单 FR-TRN-003）</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>任务标题</label><input v-model="taskForm.title" class="input" /></div>
          <div class="form-field"><label>所属训练计划</label>
            <select v-model="taskForm.plan_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="form-field"><label>周次</label><input v-model="taskForm.week" class="input" /></div>
          <div class="form-field"><label>指派竞赛会员</label>
            <select v-model="taskForm.member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field"><label>关联题单</label>
            <select v-model="taskForm.problem_list_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="pl in problemLists" :key="pl.id" :value="pl.id">{{ pl.title }}</option>
            </select>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showTaskModal = false">取消</button>
          <button class="btn btn-primary" @click="submitTask">下发任务</button>
        </div>
      </div>
    </div>

    <!-- ============ 打卡考勤弹窗 ============ -->
    <div v-if="showCheckinModal" class="modal-mask" @click.self="showCheckinModal = false">
      <div class="modal-box">
        <div class="card-title"><span>训练打卡与考勤记录 · {{ checkinTarget?.title }}</span></div>
        <div class="form-grid">
          <div class="form-field"><label>考勤状态</label>
            <select v-model="checkinForm.attendance" class="select">
              <option value="PRESENT">正常出勤</option>
              <option value="LATE">迟到</option>
              <option value="ABSENT">缺勤</option>
            </select>
          </div>
          <div class="form-field"><label>补题数量</label><input v-model.number="checkinForm.solved_count" type="number" min="0" class="input" /></div>
          <div class="form-field full"><label>阶段反馈 / 备注</label><textarea v-model="checkinForm.remark" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showCheckinModal = false">取消</button>
          <button class="btn btn-primary" @click="submitCheckin">提交打卡</button>
        </div>
      </div>
    </div>

    <!-- ============ 新建集训弹窗 ============ -->
    <div v-if="showCampModal" class="modal-mask" @click.self="showCampModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新建寒假/暑假集训计划</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>集训名称</label><input v-model="campForm.name" class="input" /></div>
          <div class="form-field"><label>集训类型</label>
            <select v-model="campForm.camp_type" class="select">
              <option value="WINTER">寒假集训</option>
              <option value="SUMMER">暑假多校集训</option>
            </select>
          </div>
          <div class="form-field"><label>届次 / 周期</label><input v-model="campForm.term" class="input" /></div>
          <div class="form-field"><label>集训地点</label><input v-model="campForm.location" class="input" /></div>
          <div class="form-field"><label>开始日期</label><input v-model="campForm.start_date" type="date" class="input" /></div>
          <div class="form-field"><label>结束日期</label><input v-model="campForm.end_date" type="date" class="input" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showCampModal = false">取消</button>
          <button class="btn btn-primary" @click="submitCamp">创建集训</button>
        </div>
      </div>
    </div>

    <!-- ============ 集训总结弹窗 ============ -->
    <div v-if="showSummaryModal" class="modal-mask" @click.self="showSummaryModal = false">
      <div class="modal-box">
        <div class="card-title"><span>记录集训总结 · {{ summaryTarget?.name }}</span></div>
        <div class="form-field full"><label>阶段复盘总结（衔接下一轮能力评估）</label><textarea v-model="summaryText" class="textarea" style="min-height:120px;"></textarea></div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showSummaryModal = false">取消</button>
          <button class="btn btn-primary" @click="submitSummary">保存总结</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const emit = defineEmits(['notify'])

const tabs = [
  { key: 'plans', label: '训练计划（个人补强）' },
  { key: 'tasks', label: '周任务打卡与考勤' },
  { key: 'camps', label: '寒暑假集训看板' }
]
const activeTab = ref('plans')

const plans = ref([])
const tasks = ref([])
const camps = ref([])
const competitionMembers = ref([])
const problemLists = ref([])

const planFilter = reactive({ plan_type: '' })
const campFilter = reactive({ camp_type: '' })

const showPlanModal = ref(false)
const showTaskModal = ref(false)
const showCheckinModal = ref(false)
const showCampModal = ref(false)
const showSummaryModal = ref(false)

const planForm = reactive({ name: '', plan_type: 'PERSONAL', cycle: '', member_id: null, problem_list_id: null, description: '' })
const taskForm = reactive({ title: '', plan_id: null, week: '', member_id: null, problem_list_id: null })
const checkinForm = reactive({ attendance: 'PRESENT', solved_count: 0, remark: '' })
const campForm = reactive({ name: '', camp_type: 'WINTER', term: '', location: '', start_date: '', end_date: '' })
const checkinTarget = ref(null)
const summaryTarget = ref(null)
const summaryText = ref('')

function switchTab(key) {
  activeTab.value = key
  if (key === 'plans') loadPlans()
  else if (key === 'tasks') loadTasks()
  else if (key === 'camps') loadCamps()
}

async function loadPlans() {
  try {
    plans.value = await api.getTrainingPlans(planFilter)
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadTasks() {
  try {
    tasks.value = await api.getTrainingTasks()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadCamps() {
  try {
    camps.value = await api.getTrainingCamps(campFilter)
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadMeta() {
  try {
    const [members, lists] = await Promise.all([
      api.getMembers({ direction: 'COMPETITION' }),
      api.getProblemLists()
    ])
    competitionMembers.value = members
    problemLists.value = lists
  } catch (err) {
    // 后端 Sprint 3/4 未合入前可容忍，页面仍可正常浏览
  }
}

function openPlanModal() {
  planForm.name = ''
  planForm.plan_type = 'PERSONAL'
  planForm.cycle = ''
  planForm.member_id = null
  planForm.problem_list_id = null
  planForm.description = ''
  showPlanModal.value = true
}

async function submitPlan() {
  if (!planForm.name.trim()) {
    emit('notify', { message: '请填写计划名称', type: 'err' })
    return
  }
  try {
    await api.createTrainingPlan({ ...planForm })
    showPlanModal.value = false
    emit('notify', { message: '训练计划已创建，个人计划已自动读取最近一次能力评估薄弱项 (BR-007)' })
    await loadPlans()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openTaskModal() {
  taskForm.title = ''
  taskForm.plan_id = null
  taskForm.week = ''
  taskForm.member_id = null
  taskForm.problem_list_id = null
  showTaskModal.value = true
}

async function submitTask() {
  if (!taskForm.title.trim()) {
    emit('notify', { message: '请填写任务标题', type: 'err' })
    return
  }
  try {
    await api.createTrainingTask({ ...taskForm })
    showTaskModal.value = false
    emit('notify', { message: '训练任务已下发并关联题库题单' })
    await loadTasks()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openCheckinModal(task) {
  checkinTarget.value = task
  checkinForm.attendance = 'PRESENT'
  checkinForm.solved_count = task.solved_count || 0
  checkinForm.remark = ''
  showCheckinModal.value = true
}

async function submitCheckin() {
  try {
    await api.checkinTrainingTask(checkinTarget.value.id, { ...checkinForm })
    showCheckinModal.value = false
    emit('notify', { message: '打卡与考勤已记录' })
    await loadTasks()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openCampModal() {
  campForm.name = ''
  campForm.camp_type = 'WINTER'
  campForm.term = ''
  campForm.location = ''
  campForm.start_date = ''
  campForm.end_date = ''
  showCampModal.value = true
}

async function submitCamp() {
  if (!campForm.name.trim()) {
    emit('notify', { message: '请填写集训名称', type: 'err' })
    return
  }
  try {
    await api.createTrainingCamp({ ...campForm })
    showCampModal.value = false
    emit('notify', { message: '集训计划已创建' })
    await loadCamps()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openSummaryModal(camp) {
  summaryTarget.value = camp
  summaryText.value = camp.summary || ''
  showSummaryModal.value = true
}

async function submitSummary() {
  try {
    await api.summarizeCamp(summaryTarget.value.id, { summary: summaryText.value })
    showSummaryModal.value = false
    emit('notify', { message: '集训总结已保存，可衔接下一轮能力评估' })
    await loadCamps()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function percent(a, b) {
  const t = Number(b) || 0
  if (!t) return 0
  return Math.min(100, Math.round((Number(a) || 0) / t * 100))
}

function attendanceLabel(v) {
  return { PRESENT: '正常', LATE: '迟到', ABSENT: '缺勤' }[v] || v || '未记录'
}

function attendanceBadge(v) {
  return { PRESENT: 'badge-green', LATE: 'badge-amber', ABSENT: 'badge-red' }[v] || 'badge-gray'
}

onMounted(() => {
  loadMeta()
  loadPlans()
})
</script>
