<template>
  <div>
    <div class="tabs">
      <button :class="['tab-btn', activeTab === 'members' && 'active']" @click="activeTab = 'members'">
        会员信息与档案 ({{ members.length }})
      </button>
      <button :class="['tab-btn', activeTab === 'applications' && 'active']" @click="activeTab = 'applications'">
        入会申请与审核 ({{ pendingAppsCount }} 待审)
      </button>
      <button :class="['tab-btn', activeTab === 'assessments' && 'active']" @click="activeTab = 'assessments'">
        周期考核与状态流转 (BR-002/003)
      </button>
      <button :class="['tab-btn', activeTab === 'org' && 'active']" @click="activeTab = 'org'">
        组织任职与奖惩评优
      </button>
    </div>

    <!-- Tab 1: 会员信息与生命周期 -->
    <div v-if="activeTab === 'members'" class="card">
      <div class="toolbar">
        <input v-model="filters.keyword" class="input" placeholder="搜索姓名 / 学号 / 专业..." @keyup.enter="loadMembers" />
        <select v-model="filters.stage" class="select" @change="loadMembers">
          <option value="">全部阶段</option>
          <option value="CANDIDATE">备选会员</option>
          <option value="FORMAL">正式会员</option>
          <option value="EXITED">已退出</option>
        </select>
        <select v-model="filters.direction" class="select" @change="loadMembers">
          <option value="">全部方向</option>
          <option value="COMPETITION">竞赛会员</option>
          <option value="NON_COMPETITION">非竞赛会员</option>
        </select>
        <select v-model="filters.status" class="select" @change="loadMembers">
          <option value="">全部状态</option>
          <option value="ACTIVE">正常状态</option>
          <option value="OBSERVATION">观察状态</option>
          <option value="DISMISSAL_PENDING">待清退</option>
          <option value="DISMISSED">已清退</option>
          <option value="WITHDRAWN">主动退会</option>
        </select>
        <button class="btn" @click="loadMembers">查询</button>
        <button class="btn btn-primary" style="margin-left:auto;" @click="showMemberModal = true">+ 直接新增会员</button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>学号 / 姓名</th>
              <th>专业年级</th>
              <th>部门</th>
              <th>资格阶段</th>
              <th>职责方向</th>
              <th>管理状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in members" :key="m.id">
              <td>
                <strong>{{ m.name }}</strong>
                <div style="font-size:12px;color:#64748b;">{{ m.student_no }}</div>
              </td>
              <td>{{ m.major }} · {{ m.grade }}</td>
              <td>{{ m.department }}</td>
              <td>
                <span :class="['badge', stageBadge(m.stage)]">{{ stageLabel(m.stage) }}</span>
              </td>
              <td>
                <span :class="['badge', m.direction === 'COMPETITION' ? 'badge-blue' : 'badge-purple']">
                  {{ directionLabel(m.direction) }}
                </span>
              </td>
              <td>
                <span :class="['badge', statusBadge(m.status)]">{{ statusLabel(m.status) }}</span>
                <span v-if="m.consecutive_failures > 0" style="font-size:11px;color:#dc2626;margin-left:4px;">
                  (连挂{{ m.consecutive_failures }}次)
                </span>
              </td>
              <td>
                <div style="display:flex;gap:6px;flex-wrap:wrap;">
                  <button class="btn btn-sm" @click="openProfile(m.id)">完整档案</button>
                  <button v-if="m.stage === 'CANDIDATE'" class="btn btn-success btn-sm" @click="openPromote(m)">
                    入会考核转正
                  </button>
                  <button v-if="m.status === 'DISMISSAL_PENDING'" class="btn btn-danger btn-sm" @click="confirmDismiss(m)">
                    执行清退
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 2: 入会申请与资格审核 -->
    <div v-if="activeTab === 'applications'" class="card">
      <div class="card-title">
        <span>入会申请列表（审核通过按 BR-001 自动进入【备选会员】阶段）</span>
        <button class="btn btn-primary btn-sm" @click="showAppModal = true">+ 提交模拟入会申请</button>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>申请学生</th>
              <th>意向方向</th>
              <th>学习与竞赛经历</th>
              <th>审核状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in applications" :key="a.id">
              <td>
                <strong>{{ a.name }}</strong> ({{ a.student_no }})
                <div style="font-size:12px;color:#64748b;">{{ a.major }} · {{ a.grade }}</div>
              </td>
              <td>
                <span :class="['badge', a.target_direction === 'COMPETITION' ? 'badge-blue' : 'badge-purple']">
                  {{ directionLabel(a.target_direction) }}
                </span>
              </td>
              <td style="max-width:340px;font-size:12px;color:#475569;">{{ a.experience || '—' }}</td>
              <td>
                <span :class="['badge', a.status === 'PENDING' ? 'badge-amber' : a.status === 'APPROVED' ? 'badge-green' : 'badge-red']">
                  {{ a.status === 'PENDING' ? '待审核' : a.status === 'APPROVED' ? '已转备选会员' : '已驳回' }}
                </span>
              </td>
              <td>
                <div v-if="a.status === 'PENDING'" style="display:flex;gap:6px;">
                  <button class="btn btn-success btn-sm" @click="handleReview(a, true)">通过→备选</button>
                  <button class="btn btn-danger btn-sm" @click="handleReview(a, false)">驳回</button>
                </div>
                <span v-else style="font-size:12px;color:#64748b;">{{ a.review_note || '已处理' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 3: 周期考核与自动状态流转 -->
    <div v-if="activeTab === 'assessments'" class="grid-2">
      <div class="card">
        <div class="card-title">
          <span>录入周期会员考核（BR-002 双轨指标 / BR-003 自动流转）</span>
        </div>
        <div class="form-grid">
          <div class="form-field full">
            <label>选择正式会员</label>
            <select v-model="assessForm.member_id" class="select">
              <option value="">请选择正式会员...</option>
              <option v-for="m in formalMembers" :key="m.id" :value="m.id">
                {{ m.name }}（{{ directionLabel(m.direction) }} · 当前：{{ statusLabel(m.status) }}）
              </option>
            </select>
          </div>
          <div class="form-field">
            <label>考核周期</label>
            <input v-model="assessForm.cycle" class="input" placeholder="如：2026-2027第一学期期末" />
          </div>
          <div class="form-field">
            <label>综合评分 (0-100)</label>
            <input v-model.number="assessForm.score" type="number" min="0" max="100" class="input" />
          </div>

          <!-- 动态展示竞赛 / 非竞赛差异化考核指标 (BR-002 / BR-004) -->
          <template v-if="selectedAssessMember?.direction === 'COMPETITION'">
            <div class="form-field">
              <label>训练任务完成率 (%)</label>
              <input v-model.number="assessForm.m1" type="number" class="input" />
            </div>
            <div class="form-field">
              <label>训练考勤率 (%)</label>
              <input v-model.number="assessForm.m2" type="number" class="input" />
            </div>
            <div class="form-field full">
              <label>正式竞赛成绩 / 获奖表现（BR-004）</label>
              <input v-model="assessForm.award" class="input" placeholder="如：省赛二等奖 / 校赛一等奖 / 暂无" />
            </div>
          </template>
          <template v-else-if="selectedAssessMember?.direction === 'NON_COMPETITION'">
            <div class="form-field">
              <label>工作任务完成度 (%)</label>
              <input v-model.number="assessForm.m1" type="number" class="input" />
            </div>
            <div class="form-field">
              <label>值班考勤与协作质量 (%)</label>
              <input v-model.number="assessForm.m2" type="number" class="input" />
            </div>
          </template>

          <div class="form-field full">
            <label>考核结论（不合格将自动触发观察/待清退状态机）</label>
            <select v-model="assessForm.passed" class="select">
              <option :value="true">考核合格（保持/恢复正常状态）</option>
              <option :value="false">考核不合格（单次→观察状态，连续2次→待清退流程）</option>
            </select>
          </div>
          <div class="form-field full">
            <label>考核评语</label>
            <textarea v-model="assessForm.comment" class="textarea" placeholder="填写考核说明..."></textarea>
          </div>
        </div>
        <div style="margin-top:14px;">
          <button class="btn btn-primary" @click="submitAssessment">提交考核并触发状态流转</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title"><span>历史周期考核流水</span></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>会员 / 周期</th>
                <th>方向</th>
                <th>得分</th>
                <th>流转结果</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in assessments" :key="a.id">
                <td>
                  <strong>{{ a.member_name }}</strong>
                  <div style="font-size:12px;color:#64748b;">{{ a.cycle }}</div>
                </td>
                <td><span class="badge badge-blue">{{ directionLabel(a.direction) }}</span></td>
                <td>
                  <strong>{{ a.score }}</strong>
                  <span :class="['badge', a.passed ? 'badge-green' : 'badge-red']" style="margin-left:4px;">
                    {{ a.passed ? '合格' : '不合格' }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', statusBadge(a.resulting_status)]">{{ statusLabel(a.resulting_status) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Tab 4: 组织任职与奖惩评优 -->
    <div v-if="activeTab === 'org'" class="grid-2">
      <div class="card">
        <div class="card-title">
          <span>组织架构与任职履历（职务与会员类型解耦）</span>
          <button class="btn btn-primary btn-sm" @click="showPosModal = true">+ 新增任职</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>成员</th>
                <th>部门 / 职务</th>
                <th>任期</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in positions" :key="p.id">
                <td><strong>{{ p.member_name }}</strong></td>
                <td>{{ p.department }} · <strong>{{ p.title }}</strong></td>
                <td>{{ p.term }}</td>
                <td>
                  <span :class="['badge', p.is_current ? 'badge-green' : 'badge-gray']">
                    {{ p.is_current ? '在任' : '历史任职' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>优秀会员公示与奖惩记录 (FR-AM-008)</span>
          <button class="btn btn-primary btn-sm" @click="showRewardModal = true">+ 新增奖惩</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>成员</th>
                <th>类型与事项</th>
                <th>公示</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rewards" :key="r.id">
                <td><strong>{{ r.member_name }}</strong></td>
                <td>
                  <span :class="['badge', r.record_type.includes('EXCELLENT') || r.record_type === 'REWARD' ? 'badge-green' : 'badge-red']">
                    {{ rewardLabel(r.record_type) }}
                  </span>
                  <div style="font-weight:600;margin-top:3px;">{{ r.title }}</div>
                  <div style="font-size:12px;color:#64748b;">{{ r.reason }}</div>
                </td>
                <td>{{ r.is_public ? '已公示' : '内部存档' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 弹窗：完整会员档案 (FR-AM-010) -->
    <div v-if="profileData" class="modal-mask" @click.self="profileData = null">
      <div class="modal-box" style="max-width:740px;">
        <div class="card-title">
          <span>会员全周期个人档案 · {{ profileData.member.name }} ({{ profileData.member.student_no }})</span>
          <button class="btn btn-sm" @click="profileData = null">关闭</button>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">
          <span :class="['badge', stageBadge(profileData.member.stage)]">{{ stageLabel(profileData.member.stage) }}</span>
          <span class="badge badge-blue">{{ directionLabel(profileData.member.direction) }}</span>
          <span :class="['badge', statusBadge(profileData.member.status)]">{{ statusLabel(profileData.member.status) }}</span>
          <span class="badge badge-gray">{{ profileData.member.department }} · {{ profileData.member.major }} {{ profileData.member.grade }}</span>
        </div>
        <p style="font-size:13px;color:#475569;margin-top:0;">经历：{{ profileData.member.experience || '暂无' }}</p>

        <h4 style="margin:14px 0 6px;font-size:13px;">组织任职履历 ({{ profileData.positions.length }})</h4>
        <div v-if="profileData.positions.length" style="display:flex;gap:8px;flex-wrap:wrap;">
          <span v-for="p in profileData.positions" :key="p.id" class="badge badge-purple">
            {{ p.department }} {{ p.title }}（{{ p.term }}）
          </span>
        </div>
        <div v-else style="font-size:12px;color:#94a3b8;">暂无任职记录</div>

        <h4 style="margin:14px 0 6px;font-size:13px;">周期考核记录 ({{ profileData.assessments.length }})</h4>
        <div v-for="a in profileData.assessments" :key="a.id" style="padding:8px 10px;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:6px;font-size:12px;">
          <strong>{{ a.cycle }}</strong> · 得分 {{ a.score }} · {{ a.passed ? '合格' : '不合格' }} → {{ statusLabel(a.resulting_status) }}
          <div style="color:#64748b;">{{ a.comment }}</div>
        </div>

        <h4 style="margin:14px 0 6px;font-size:13px;">个人能力评估快照 ({{ profileData.ability_summary.length }})</h4>
        <div v-for="ab in profileData.ability_summary" :key="ab.id" style="padding:8px 10px;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:6px;font-size:12px;">
          <strong>{{ ab.assessment_name }}</strong>（{{ ab.cycle }}）· 综合分 {{ ab.overall_score }}
        </div>
      </div>
    </div>

    <!-- 弹窗：提交申请 -->
    <div v-if="showAppModal" class="modal-mask" @click.self="showAppModal = false">
      <div class="modal-box">
        <div class="card-title"><span>提交入会申请 (FR-AM-001)</span></div>
        <div class="form-grid">
          <div class="form-field"><label>学号</label><input v-model="appForm.student_no" class="input" /></div>
          <div class="form-field"><label>姓名</label><input v-model="appForm.name" class="input" /></div>
          <div class="form-field"><label>专业</label><input v-model="appForm.major" class="input" /></div>
          <div class="form-field"><label>年级</label><input v-model="appForm.grade" class="input" /></div>
          <div class="form-field full">
            <label>意向方向</label>
            <select v-model="appForm.target_direction" class="select">
              <option value="COMPETITION">竞赛会员</option>
              <option value="NON_COMPETITION">非竞赛会员</option>
            </select>
          </div>
          <div class="form-field full"><label>学习/竞赛经历</label><textarea v-model="appForm.experience" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showAppModal = false">取消</button>
          <button class="btn btn-primary" @click="submitApplication">提交申请</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：直接新增会员 -->
    <div v-if="showMemberModal" class="modal-mask" @click.self="showMemberModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新增会员档案</span></div>
        <div class="form-grid">
          <div class="form-field"><label>学号</label><input v-model="memberForm.student_no" class="input" /></div>
          <div class="form-field"><label>姓名</label><input v-model="memberForm.name" class="input" /></div>
          <div class="form-field"><label>专业</label><input v-model="memberForm.major" class="input" /></div>
          <div class="form-field"><label>部门</label><input v-model="memberForm.department" class="input" /></div>
          <div class="form-field">
            <label>资格阶段</label>
            <select v-model="memberForm.stage" class="select">
              <option value="CANDIDATE">备选会员</option>
              <option value="FORMAL">正式会员</option>
            </select>
          </div>
          <div class="form-field">
            <label>职责方向</label>
            <select v-model="memberForm.direction" class="select">
              <option value="COMPETITION">竞赛会员</option>
              <option value="NON_COMPETITION">非竞赛会员</option>
            </select>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showMemberModal = false">取消</button>
          <button class="btn btn-primary" @click="submitMember">保存</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：备选会员转正 -->
    <div v-if="promoteTarget" class="modal-mask" @click.self="promoteTarget = null">
      <div class="modal-box">
        <div class="card-title"><span>备选会员入会考核转正 · {{ promoteTarget.name }}</span></div>
        <div class="form-grid">
          <div class="form-field">
            <label>正式会员方向 (BR-002)</label>
            <select v-model="promoteForm.direction" class="select">
              <option value="COMPETITION">竞赛会员</option>
              <option value="NON_COMPETITION">非竞赛会员</option>
            </select>
          </div>
          <div class="form-field"><label>所属部门</label><input v-model="promoteForm.department" class="input" /></div>
          <div class="form-field full"><label>入会考核评语</label><input v-model="promoteForm.note" class="input" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="promoteTarget = null">取消</button>
          <button class="btn btn-success" @click="submitPromote">确认转正为正式会员</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：新增任职 -->
    <div v-if="showPosModal" class="modal-mask" @click.self="showPosModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新增协会任职记录 (FR-AM-009)</span></div>
        <div class="form-grid">
          <div class="form-field full">
            <label>选择会员</label>
            <select v-model="posForm.member_id" class="select">
              <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }} ({{ m.student_no }})</option>
            </select>
          </div>
          <div class="form-field"><label>部门</label><input v-model="posForm.department" class="input" placeholder="如：竞赛部" /></div>
          <div class="form-field"><label>职务名称</label><input v-model="posForm.title" class="input" placeholder="会长/副会长/部长/干事" /></div>
          <div class="form-field full"><label>任期</label><input v-model="posForm.term" class="input" placeholder="2026-2027学年" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showPosModal = false">取消</button>
          <button class="btn btn-primary" @click="submitPosition">保存</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：新增奖惩 -->
    <div v-if="showRewardModal" class="modal-mask" @click.self="showRewardModal = false">
      <div class="modal-box">
        <div class="card-title"><span>登记优秀会员或奖惩事项 (FR-AM-008)</span></div>
        <div class="form-grid">
          <div class="form-field">
            <label>选择会员</label>
            <select v-model="rewardForm.member_id" class="select">
              <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field">
            <label>记录类型</label>
            <select v-model="rewardForm.record_type" class="select">
              <option value="EXCELLENT_MEMBER">优秀会员</option>
              <option value="EXCELLENT_STAFF">优秀干事</option>
              <option value="REWARD">其他奖励</option>
              <option value="WARNING">警告提醒</option>
              <option value="CRITICISM">通报批评</option>
            </select>
          </div>
          <div class="form-field full"><label>标题</label><input v-model="rewardForm.title" class="input" /></div>
          <div class="form-field full"><label>说明原因</label><textarea v-model="rewardForm.reason" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showRewardModal = false">取消</button>
          <button class="btn btn-primary" @click="submitReward">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const emit = defineEmits(['notify'])
const activeTab = ref('members')
const members = ref([])
const applications = ref([])
const assessments = ref([])
const positions = ref([])
const rewards = ref([])
const profileData = ref(null)

const filters = reactive({ keyword: '', stage: '', direction: '', status: '' })

const showAppModal = ref(false)
const appForm = reactive({ student_no: '', name: '', major: '软件工程', grade: '2025级', target_direction: 'COMPETITION', experience: '' })

const showMemberModal = ref(false)
const memberForm = reactive({ student_no: '', name: '', major: '软件工程', grade: '2024级', department: '竞赛部', stage: 'FORMAL', direction: 'COMPETITION' })

const promoteTarget = ref(null)
const promoteForm = reactive({ direction: 'COMPETITION', department: '竞赛部', note: '通过上机入会考核，正式转正' })

const assessForm = reactive({ member_id: '', cycle: '2026-2027第一学期期末', score: 85, passed: true, m1: 90, m2: 92, award: '暂无', comment: '' })

const showPosModal = ref(false)
const posForm = reactive({ member_id: '', department: '竞赛部', title: '干事', term: '2026-2027学年', is_current: true })

const showRewardModal = ref(false)
const rewardForm = reactive({ member_id: '', record_type: 'EXCELLENT_MEMBER', title: '', reason: '', is_public: true })

const pendingAppsCount = computed(() => applications.value.filter(a => a.status === 'PENDING').length)
const formalMembers = computed(() => members.value.filter(m => m.stage === 'FORMAL'))
const selectedAssessMember = computed(() => members.value.find(m => m.id === assessForm.member_id))

async function loadMembers() {
  members.value = await api.getMembers(filters)
}

async function loadAll() {
  try {
    const [m, a, asmt, pos, rew] = await Promise.all([
      api.getMembers(filters),
      api.getApplications(),
      api.getMemberAssessments(),
      api.getPositions(),
      api.getRewards()
    ])
    members.value = m
    applications.value = a
    assessments.value = asmt
    positions.value = pos
    rewards.value = rew
    if (!posForm.member_id && m.length) posForm.member_id = m[0].id
    if (!rewardForm.member_id && m.length) rewardForm.member_id = m[0].id
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function openProfile(id) {
  try {
    profileData.value = await api.getMemberProfile(id)
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitApplication() {
  try {
    await api.createApplication({ ...appForm })
    showAppModal.value = false
    Object.assign(appForm, { student_no: '', name: '', experience: '' })
    emit('notify', { message: '入会申请提交成功' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function handleReview(app, approved) {
  try {
    await api.reviewApplication(app.id, {
      approved,
      interview_note: approved ? '面试表现良好' : '暂未达到入会要求',
      review_note: approved ? '审核通过，进入备选会员阶段 (BR-001)' : '资格审核未通过',
      department: app.target_direction === 'COMPETITION' ? '竞赛部' : '办公室'
    })
    emit('notify', { message: approved ? `${app.name} 已通过审核并自动转为【备选会员】` : `已驳回 ${app.name} 的申请` })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openPromote(m) {
  promoteTarget.value = m
  promoteForm.direction = m.direction === 'NON_COMPETITION' ? 'NON_COMPETITION' : 'COMPETITION'
  promoteForm.department = m.department || '竞赛部'
}

async function submitPromote() {
  try {
    await api.promoteMember(promoteTarget.value.id, { ...promoteForm })
    emit('notify', { message: `${promoteTarget.value.name} 已正式转正并定岗！` })
    promoteTarget.value = null
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function confirmDismiss(m) {
  try {
    await api.changeMemberStatus(m.id, { status: 'DISMISSED', reason: '连续两次考核不合格，协会确认执行清退 (BR-003)' })
    emit('notify', { message: `${m.name} 已完成清退归档` })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitMember() {
  try {
    await api.createMember({ ...memberForm })
    showMemberModal.value = false
    emit('notify', { message: '会员档案创建成功' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitAssessment() {
  if (!assessForm.member_id) {
    emit('notify', { message: '请先选择一名正式会员', type: 'err' })
    return
  }
  const metrics = selectedAssessMember.value?.direction === 'COMPETITION'
    ? { training_completion: assessForm.m1, attendance: assessForm.m2, contest_awards: assessForm.award }
    : { task_completion: assessForm.m1, duty_attendance_quality: assessForm.m2 }
  try {
    const res = await api.createMemberAssessment({
      member_id: assessForm.member_id,
      cycle: assessForm.cycle,
      score: assessForm.score,
      passed: assessForm.passed,
      metrics,
      comment: assessForm.comment
    })
    emit('notify', { message: `考核已录入！${res.member_name} 当前状态已流转为【${statusLabel(res.resulting_status)}】` })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitPosition() {
  try {
    await api.createPosition({ ...posForm })
    showPosModal.value = false
    emit('notify', { message: '任职履历新增成功' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitReward() {
  try {
    await api.createReward({ ...rewardForm })
    showRewardModal.value = false
    emit('notify', { message: '奖惩记录已登记' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

const stageLabel = (s) => ({ CANDIDATE: '备选会员', FORMAL: '正式会员', EXITED: '已退出' }[s] || s)
const stageBadge = (s) => ({ CANDIDATE: 'badge-amber', FORMAL: 'badge-green', EXITED: 'badge-gray' }[s] || 'badge-gray')
const directionLabel = (d) => ({ COMPETITION: '竞赛会员', NON_COMPETITION: '非竞赛会员', UNDECIDED: '待定' }[d] || d)
const statusLabel = (s) => ({ ACTIVE: '正常状态', OBSERVATION: '观察状态', DISMISSAL_PENDING: '待清退', DISMISSED: '已清退', WITHDRAWN: '主动退会' }[s] || s)
const statusBadge = (s) => ({ ACTIVE: 'badge-green', OBSERVATION: 'badge-amber', DISMISSAL_PENDING: 'badge-red', DISMISSED: 'badge-gray', WITHDRAWN: 'badge-gray' }[s] || 'badge-gray')
const rewardLabel = (t) => ({ EXCELLENT_MEMBER: '优秀会员', EXCELLENT_STAFF: '优秀干事', REWARD: '奖励', WARNING: '警告', CRITICISM: '通报批评' }[t] || t)

onMounted(loadAll)
</script>
