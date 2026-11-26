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

    <!-- ============ Tab 1: 队伍档案与能力互补 ============ -->
    <div v-if="activeTab === 'teams'">
      <div class="card" style="margin-bottom:18px;">
        <div class="toolbar" style="margin-bottom:0;">
          <strong style="font-size:14px;">智能组队与能力互补（FR-TEAM-001~005）：</strong>
          <button class="btn" style="margin-left:auto;" @click="loadRecommend">✨ 生成能力互补候选组合</button>
          <button class="btn btn-primary" @click="openTeamModal">+ 组建队伍</button>
        </div>
      </div>

      <!-- 能力互补候选推荐 -->
      <div v-if="recommendations.length" class="card" style="margin-bottom:18px;">
        <div class="card-title">
          <span>能力互补候选组合（基于最新六维能力画像 BR-005）</span>
          <span class="badge badge-purple">{{ recommendations.length }} 组候选</span>
        </div>
        <div class="grid-3">
          <div v-for="r in recommendations" :key="r.id || r.name" class="card" style="border-color:#e9d5ff;">
            <div class="card-title">
              <span>{{ r.name || '候选队伍' }}</span>
              <span class="badge badge-purple">互补度 {{ r.complementarity_score ?? r.score ?? '-' }}</span>
            </div>
            <div v-for="m in (r.members || [])" :key="m.member_id ?? m.id" style="margin-bottom:8px;font-size:13px;">
              <strong>{{ m.name }}</strong>
              <span style="color:#64748b;font-size:12px;">（综合 {{ m.overall_score }}）</span>
              <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:3px;">
                <span v-for="w in (m.weak_points || [])" :key="w" class="badge badge-amber">{{ w }}</span>
              </div>
            </div>
            <div v-if="r.suggestion" style="font-size:12px;color:#475569;margin-top:6px;">{{ r.suggestion }}</div>
          </div>
        </div>
      </div>

      <!-- 队伍档案列表 -->
      <div v-if="teams.length" class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>队伍名称</th>
                <th>赛季</th>
                <th>成员</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in teams" :key="t.id">
                <td><strong>{{ t.name }}</strong></td>
                <td>{{ t.season || '—' }}</td>
                <td>{{ memberNames(t.members || []) }}</td>
                <td><span :class="['badge', t.status === 'ACTIVE' ? 'badge-green' : 'badge-gray']">{{ t.status || 'ACTIVE' }}</span></td>
                <td><button class="btn btn-sm" @click="openTeamDetail(t)">查看档案</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="card" style="text-align:center;padding:40px;color:#94a3b8;">
        暂无队伍档案，点击右上角「生成能力互补候选组合」或「组建队伍」
      </div>
    </div>

    <!-- ============ Tab 2: 校赛管理 ============ -->
    <div v-if="activeTab === 'school'">
      <div class="card" style="margin-bottom:18px;">
        <div class="toolbar" style="margin-bottom:0;">
          <strong style="font-size:14px;">校赛晋级 / 候补流转 / 异常行为核查（FR-CMP / BR-009 / BR-010）：</strong>
          <select v-model="selectedContestId" class="select" style="min-width:260px;" @change="loadContestData">
            <option :value="null">请选择校赛</option>
            <option v-for="c in schoolContests" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <button class="btn btn-primary" style="margin-left:auto;" @click="openContestModal">+ 新建校赛</button>
        </div>
      </div>

      <template v-if="selectedContestId">
        <div class="card" style="margin-bottom:18px;">
          <div class="card-title">
            <span>选手报名与初赛排名（个人制 member_id · BR-009）</span>
            <button class="btn btn-sm" @click="openEntryModal">+ 录入选手/成绩</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>初赛排名</th>
                  <th>选手</th>
                  <th>初赛成绩</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in entries" :key="e.id">
                  <td><strong>#{{ e.prelim_rank ?? '-' }}</strong></td>
                  <td>
                    {{ e.member_name || '—' }}
                    <div style="font-size:12px;color:#64748b;">{{ e.student_no || '' }}</div>
                  </td>
                  <td>{{ e.prelim_score ?? '—' }}</td>
                  <td><span :class="['badge', entryBadge(e.status)]">{{ entryLabel(e.status) }}</span></td>
                  <td>
                    <button v-if="e.status === 'PROMOTED'" class="btn btn-sm btn-success" @click="confirmEntry(e)">确认晋级参赛</button>
                    <button v-if="e.status === 'PROMOTED'" class="btn btn-sm btn-danger" style="margin-left:4px;" @click="abandonEntry(e)">放弃（触发候补递补）</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>线上初赛异常行为核查材料（BR-010 · 仅留存证据，人工裁决）</span>
            <button class="btn btn-sm" @click="openAnomalyModal">+ 登记核查材料</button>
          </div>
          <div v-if="anomalies.length" class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>选手</th>
                  <th>证据材料</th>
                  <th>状态</th>
                  <th>复核结论</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in anomalies" :key="a.id">
                  <td>{{ a.member_name || '—' }}</td>
                  <td>
                    <a v-if="a.evidence_url" :href="a.evidence_url" target="_blank" rel="noreferrer">{{ a.evidence_url }}</a>
                    <div style="font-size:12px;color:#64748b;">{{ a.description || '' }}</div>
                  </td>
                  <td><span :class="['badge', a.status === 'PENDING_REVIEW' ? 'badge-amber' : 'badge-green']">{{ a.status || 'PENDING_REVIEW' }}</span></td>
                  <td>{{ a.review_conclusion || '—' }}</td>
                  <td>
                    <button v-if="a.status === 'PENDING_REVIEW'" class="btn btn-sm" @click="openReviewModal(a)">人工复核</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else style="font-size:13px;color:#94a3b8;">暂无异常行为核查材料</div>
        </div>
      </template>
      <div v-else class="card" style="text-align:center;padding:40px;color:#94a3b8;">
        请先选择或新建一个校赛
      </div>
    </div>

    <!-- ============ Tab 3: 竞赛成绩归档 ============ -->
    <div v-if="activeTab === 'archive'">
      <div class="grid-2">
        <div class="card">
          <div class="card-title">
            <span>XCPC 队伍综合排序（网络预选赛/正赛 · BR-008）</span>
            <button class="btn btn-sm" @click="openXcpcModal">+ 录入 XCPC 成绩</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>排名</th>
                  <th>队伍</th>
                  <th>赛站 / 轮次</th>
                  <th>解题</th>
                  <th>奖项</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="x in sortedXcpc" :key="x.id">
                  <td><strong>#{{ x.rank ?? '-' }}</strong></td>
                  <td>{{ x.team_name || '—' }}</td>
                  <td>{{ x.site || x.round || '—' }}</td>
                  <td>{{ x.solved ?? '—' }}（罚时 {{ x.penalty ?? '-' }}）</td>
                  <td><span class="badge badge-blue">{{ x.award || '—' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>非 XCPC 赛事个人成绩（蓝桥杯/天梯赛等 · BR-008 个人制）</span>
            <button class="btn btn-sm" @click="openNonXcpcModal">+ 登记个人成绩</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>赛事</th>
                  <th>类别</th>
                  <th>选手</th>
                  <th>奖项</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="n in nonXcpc" :key="n.id">
                  <td><strong>{{ n.name }}</strong></td>
                  <td>{{ n.category || '—' }}</td>
                  <td>{{ n.member_name || '—' }}</td>
                  <td><span class="badge badge-green">{{ n.award || n.award_level || '—' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 队伍详情弹窗 ============ -->
    <div v-if="teamDetail" class="modal-mask" @click.self="teamDetail = null">
      <div class="modal-box" style="max-width:920px;">
        <div class="card-title">
          <span>队伍档案 · {{ teamDetail.name }}</span>
          <button class="btn btn-sm" @click="teamDetail = null">关闭</button>
        </div>
        <div class="grid-2">
          <div v-for="m in (teamDetail.members || [])" :key="m.member_id ?? m.id" class="card">
            <div class="card-title">
              <span>{{ m.name }}</span>
              <span class="badge badge-blue">综合 {{ m.overall_score }}</span>
            </div>
            <AbilityRadarChart v-if="m.lang_basic !== undefined" :latest="m" />
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;">
              <span v-for="w in (m.weak_points || [])" :key="w" class="badge badge-amber">{{ w }}</span>
            </div>
          </div>
        </div>
        <div v-if="teamDetail.adjust_logs?.length" style="margin-top:16px;">
          <div class="card-title"><span>成员调整流水（Append-Only · BR-008）</span></div>
          <div v-for="lg in teamDetail.adjust_logs" :key="lg.id" style="padding:8px 10px;border-bottom:1px solid #e2e8f0;font-size:13px;">
            <strong>{{ lg.action }}</strong> {{ lg.member_name }} · {{ lg.reason || '' }}
            <span style="color:#94a3b8;font-size:12px;">{{ formatTime(lg.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============ 组建队伍弹窗 ============ -->
    <div v-if="showTeamModal" class="modal-mask" @click.self="showTeamModal = false">
      <div class="modal-box">
        <div class="card-title"><span>组建正式队伍（留存入队能力快照 FR-TEAM-001）</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>队伍名称</label><input v-model="teamForm.name" class="input" /></div>
          <div class="form-field"><label>赛季</label><input v-model="teamForm.season" class="input" /></div>
          <div class="form-field"><label>队长</label>
            <select v-model="teamForm.leader_member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field full">
            <label>队员（能力互补）</label>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
              <label v-for="m in competitionMembers" :key="m.id" style="display:flex;align-items:center;gap:5px;font-size:13px;">
                <input type="checkbox" :value="m.id" v-model="teamForm.member_ids" />
                {{ m.name }}
              </label>
            </div>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showTeamModal = false">取消</button>
          <button class="btn btn-primary" @click="submitTeam">组建队伍</button>
        </div>
      </div>
    </div>

    <!-- ============ 校赛晋级确认 / 放弃弹窗 ============ -->
    <div v-if="confirmEntryObj" class="modal-mask" @click.self="confirmEntryObj = null">
      <div class="modal-box">
        <div class="card-title"><span>决赛参赛确认 · {{ confirmEntryObj.member_name }}</span></div>
        <p style="font-size:13px;color:#475569;">
          确认晋级选手决赛参赛资格；若放弃或逾期未确认，系统将在同一事务内按初赛排名自动从候补池递补首位选手（BR-009）。
        </p>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="confirmEntryObj = null">取消</button>
          <button class="btn btn-success" @click="doConfirm(true)">确认参赛</button>
          <button class="btn btn-danger" @click="doConfirm(false)">放弃参赛并递补</button>
        </div>
      </div>
    </div>

    <!-- ============ 新建校赛 / 录入选手 / 登记异常 / 复核 等弹窗 ============ -->
    <div v-if="showContestModal" class="modal-mask" @click.self="showContestModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新建校赛方案</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>校赛名称</label><input v-model="contestForm.name" class="input" /></div>
          <div class="form-field"><label>届次</label><input v-model="contestForm.term" class="input" /></div>
          <div class="form-field"><label>轮次</label><input v-model="contestForm.round" class="input" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showContestModal = false">取消</button>
          <button class="btn btn-primary" @click="submitContest">创建校赛</button>
        </div>
      </div>
    </div>

    <div v-if="showEntryModal" class="modal-mask" @click.self="showEntryModal = false">
      <div class="modal-box">
        <div class="card-title"><span>录入校赛选手 / 初赛成绩</span></div>
        <div class="form-grid">
          <div class="form-field"><label>选手</label>
            <select v-model="entryForm.member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field"><label>初赛排名</label><input v-model.number="entryForm.prelim_rank" type="number" class="input" /></div>
          <div class="form-field"><label>初赛成绩</label><input v-model.number="entryForm.prelim_score" type="number" class="input" /></div>
          <div class="form-field"><label>状态</label>
            <select v-model="entryForm.status" class="select">
              <option value="REGISTERED">已报名</option>
              <option value="WAITLISTED">候补</option>
              <option value="PROMOTED">晋级决赛</option>
            </select>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showEntryModal = false">取消</button>
          <button class="btn btn-primary" @click="submitEntry">录入</button>
        </div>
      </div>
    </div>

    <div v-if="showAnomalyModal" class="modal-mask" @click.self="showAnomalyModal = false">
      <div class="modal-box">
        <div class="card-title"><span>登记线上初赛异常行为核查材料（BR-010）</span></div>
        <div class="form-grid">
          <div class="form-field"><label>选手</label>
            <select v-model="anomalyForm.member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field"><label>证据链接</label><input v-model="anomalyForm.evidence_url" class="input" /></div>
          <div class="form-field full"><label>异常描述（材料仅留存，禁止系统自动判作弊）</label><textarea v-model="anomalyForm.description" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showAnomalyModal = false">取消</button>
          <button class="btn btn-primary" @click="submitAnomaly">登记材料</button>
        </div>
      </div>
    </div>

    <div v-if="reviewAnomalyObj" class="modal-mask" @click.self="reviewAnomalyObj = null">
      <div class="modal-box">
        <div class="card-title"><span>人工复核裁决 · {{ reviewAnomalyObj.member_name }}</span></div>
        <div class="form-field full">
          <label>复核结论（三值枚举，不覆盖原始材料）</label>
          <select v-model="reviewForm.review_conclusion" class="select">
            <option value="CONFIRMED_VIOLATION">确认违规</option>
            <option value="EXONERATED">排除嫌疑</option>
            <option value="NEED_MORE_EVIDENCE">证据不足，需补充</option>
          </select>
        </div>
        <div class="form-field full" style="margin-top:10px;"><label>复核人</label><input v-model="reviewForm.reviewer" class="input" /></div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="reviewAnomalyObj = null">取消</button>
          <button class="btn btn-primary" @click="submitReview">提交裁决</button>
        </div>
      </div>
    </div>

    <div v-if="showXcpcModal" class="modal-mask" @click.self="showXcpcModal = false">
      <div class="modal-box">
        <div class="card-title"><span>录入 XCPC 队伍成绩（team_id 非空 BR-008）</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>赛事名称</label><input v-model="xcpcForm.name" class="input" /></div>
          <div class="form-field"><label>队伍</label>
            <select v-model="xcpcForm.team_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="form-field"><label>赛站 / 轮次</label><input v-model="xcpcForm.site" class="input" /></div>
          <div class="form-field"><label>排名</label><input v-model.number="xcpcForm.rank" type="number" class="input" /></div>
          <div class="form-field"><label>解题数</label><input v-model.number="xcpcForm.solved" type="number" class="input" /></div>
          <div class="form-field"><label>罚时</label><input v-model.number="xcpcForm.penalty" type="number" class="input" /></div>
          <div class="form-field full"><label>奖项</label><input v-model="xcpcForm.award" class="input" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showXcpcModal = false">取消</button>
          <button class="btn btn-primary" @click="submitXcpc">录入成绩</button>
        </div>
      </div>
    </div>

    <div v-if="showNonXcpcModal" class="modal-mask" @click.self="showNonXcpcModal = false">
      <div class="modal-box">
        <div class="card-title"><span>登记非 XCPC 赛事个人成绩（个人制 BR-008）</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>赛事名称</label><input v-model="nonXcpcForm.name" class="input" /></div>
          <div class="form-field"><label>赛事类别</label>
            <select v-model="nonXcpcForm.category" class="select">
              <option>蓝桥杯</option>
              <option>天梯赛</option>
              <option>码蹄杯</option>
              <option>百度之星</option>
            </select>
          </div>
          <div class="form-field"><label>选手</label>
            <select v-model="nonXcpcForm.member_id" class="select">
              <option :value="null">请选择</option>
              <option v-for="m in competitionMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-field full"><label>奖项 / 等级</label><input v-model="nonXcpcForm.award" class="input" /></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showNonXcpcModal = false">取消</button>
          <button class="btn btn-primary" @click="submitNonXcpc">登记成绩</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import AbilityRadarChart from '../components/AbilityRadarChart.vue'

const emit = defineEmits(['notify'])

const tabs = [
  { key: 'teams', label: '队伍档案与能力互补' },
  { key: 'school', label: '校赛晋级 / 候补流转' },
  { key: 'archive', label: 'XCPC / 非XCPC 成绩归档' }
]
const activeTab = ref('teams')

const teams = ref([])
const recommendations = ref([])
const competitionMembers = ref([])

const schoolContests = ref([])
const selectedContestId = ref(null)
const entries = ref([])
const anomalies = ref([])

const nonXcpc = ref([])
const xcpc = ref([])

const teamDetail = ref(null)
const showTeamModal = ref(false)
const confirmEntryObj = ref(null)
const showContestModal = ref(false)
const showEntryModal = ref(false)
const showAnomalyModal = ref(false)
const reviewAnomalyObj = ref(null)
const showXcpcModal = ref(false)
const showNonXcpcModal = ref(false)

const teamForm = reactive({ name: '', season: '', leader_member_id: null, member_ids: [] })
const contestForm = reactive({ name: '', term: '', round: '' })
const entryForm = reactive({ member_id: null, prelim_rank: null, prelim_score: null, status: 'PROMOTED' })
const anomalyForm = reactive({ member_id: null, evidence_url: '', description: '' })
const reviewForm = reactive({ review_conclusion: 'CONFIRMED_VIOLATION', reviewer: '' })
const xcpcForm = reactive({ name: '', team_id: null, site: '', rank: null, solved: null, penalty: null, award: '' })
const nonXcpcForm = reactive({ name: '', category: '蓝桥杯', member_id: null, award: '' })

const sortedXcpc = computed(() => {
  return [...xcpc.value].sort((a, b) => (Number(a.rank) || 9999) - (Number(b.rank) || 9999))
})

function switchTab(key) {
  activeTab.value = key
  if (key === 'teams') loadTeams()
  else if (key === 'school') loadSchoolContests()
  else if (key === 'archive') loadArchive()
}

async function loadTeams() {
  try {
    teams.value = await api.getTeams()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadRecommend() {
  try {
    recommendations.value = await api.getTeamRecommend()
    emit('notify', { message: '能力互补候选组合已生成' })
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function openTeamDetail(team) {
  try {
    teamDetail.value = await api.getTeamDetail(team.id)
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadSchoolContests() {
  try {
    schoolContests.value = await api.getSchoolContests()
    if (schoolContests.value.length) {
      selectedContestId.value = schoolContests.value[0].id
      await loadContestData()
    }
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadContestData() {
  if (!selectedContestId.value) return
  try {
    const [e, a] = await Promise.all([
      api.getSchoolContestEntries(selectedContestId.value),
      api.getAnomalies(selectedContestId.value)
    ])
    entries.value = e
    anomalies.value = a
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadArchive() {
  try {
    const [n, x] = await Promise.all([api.getNonXcpc(), api.getXcpc()])
    nonXcpc.value = n
    xcpc.value = x
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openTeamModal() {
  teamForm.name = ''
  teamForm.season = ''
  teamForm.leader_member_id = null
  teamForm.member_ids = []
  showTeamModal.value = true
}

async function submitTeam() {
  if (!teamForm.name.trim()) {
    emit('notify', { message: '请填写队伍名称', type: 'err' })
    return
  }
  try {
    await api.createTeam({ ...teamForm })
    showTeamModal.value = false
    emit('notify', { message: '队伍已组建并留存成员入队能力快照' })
    await loadTeams()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function confirmEntry(entry) {
  confirmEntryObj.value = entry
}

async function abandonEntry(entry) {
  confirmEntryObj.value = entry
}

async function doConfirm(confirmed) {
  try {
    await api.confirmSchoolContestEntry(selectedContestId.value, {
      entry_id: confirmEntryObj.value.id,
      confirmed,
      auto: false
    })
    confirmEntryObj.value = null
    emit('notify', { message: confirmed ? '已确认决赛参赛' : '已放弃参赛，系统已按初赛排名自动递补候补选手 (BR-009)' })
    await loadContestData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openContestModal() {
  contestForm.name = ''
  contestForm.term = ''
  contestForm.round = ''
  showContestModal.value = true
}

async function submitContest() {
  if (!contestForm.name.trim()) {
    emit('notify', { message: '请填写校赛名称', type: 'err' })
    return
  }
  try {
    const created = await api.createSchoolContest({ ...contestForm })
    showContestModal.value = false
    emit('notify', { message: '校赛已创建' })
    await loadSchoolContests()
    selectedContestId.value = created.id
    await loadContestData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openEntryModal() {
  entryForm.member_id = null
  entryForm.prelim_rank = null
  entryForm.prelim_score = null
  entryForm.status = 'PROMOTED'
  showEntryModal.value = true
}

async function submitEntry() {
  try {
    await api.createSchoolContestEntry(selectedContestId.value, { ...entryForm })
    showEntryModal.value = false
    emit('notify', { message: '选手/成绩已录入' })
    await loadContestData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openAnomalyModal() {
  anomalyForm.member_id = null
  anomalyForm.evidence_url = ''
  anomalyForm.description = ''
  showAnomalyModal.value = true
}

async function submitAnomaly() {
  try {
    await api.createAnomaly(selectedContestId.value, { ...anomalyForm })
    showAnomalyModal.value = false
    emit('notify', { message: '核查材料已留存（状态固定为待复核，材料不可覆盖）' })
    await loadContestData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openReviewModal(anomaly) {
  reviewAnomalyObj.value = anomaly
  reviewForm.review_conclusion = 'CONFIRMED_VIOLATION'
  reviewForm.reviewer = ''
}

async function submitReview() {
  try {
    await api.reviewAnomaly(selectedContestId.value, reviewAnomalyObj.value.id, { ...reviewForm })
    reviewAnomalyObj.value = null
    emit('notify', { message: '人工复核结论已写入（不覆盖原始证据材料 BR-010）' })
    await loadContestData()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openXcpcModal() {
  xcpcForm.name = ''
  xcpcForm.team_id = null
  xcpcForm.site = ''
  xcpcForm.rank = null
  xcpcForm.solved = null
  xcpcForm.penalty = null
  xcpcForm.award = ''
  showXcpcModal.value = true
}

async function submitXcpc() {
  try {
    await api.createXcpc({ ...xcpcForm })
    showXcpcModal.value = false
    emit('notify', { message: 'XCPC 成绩已归档至队伍档案 (BR-008)' })
    await loadArchive()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openNonXcpcModal() {
  nonXcpcForm.name = ''
  nonXcpcForm.category = '蓝桥杯'
  nonXcpcForm.member_id = null
  nonXcpcForm.award = ''
  showNonXcpcModal.value = true
}

async function submitNonXcpc() {
  try {
    await api.createNonXcpc({ ...nonXcpcForm })
    showNonXcpcModal.value = false
    emit('notify', { message: '非 XCPC 个人成绩已归档' })
    await loadArchive()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function memberNames(members) {
  return (members || []).map(m => m.name).join('、') || '—'
}

function entryLabel(v) {
  return {
    REGISTERED: '已报名',
    WAITLISTED: '候补',
    PROMOTED: '晋级决赛',
    CONFIRMED: '已确认参赛',
    ABANDONED: '已放弃'
  }[v] || v || '—'
}

function entryBadge(v) {
  return {
    REGISTERED: 'badge-gray',
    WAITLISTED: 'badge-amber',
    PROMOTED: 'badge-blue',
    CONFIRMED: 'badge-green',
    ABANDONED: 'badge-red'
  }[v] || 'badge-gray'
}

function formatTime(t) {
  return t ? new Date(t).toLocaleString('zh-CN') : ''
}

async function loadMeta() {
  try {
    competitionMembers.value = await api.getMembers({ direction: 'COMPETITION' })
  } catch (err) {
    // 忽略，后端未就绪时仍可浏览
  }
}

onMounted(() => {
  loadMeta()
  loadTeams()
})
</script>
