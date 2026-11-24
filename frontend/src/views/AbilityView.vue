<template>
  <div>
    <!-- 顶部选择竞赛会员 -->
    <div class="card" style="margin-bottom:18px;">
      <div class="toolbar" style="margin-bottom:0;">
        <strong style="font-size:14px;">选择竞赛会员（BR-005 独立于会员考核）：</strong>
        <select v-model="selectedMemberId" class="select" style="min-width:260px;" @change="loadProfile">
          <option v-for="m in competitionMembers" :key="m.id" :value="m.id">
            {{ m.name }}（{{ m.student_no }} · {{ m.department }} · {{ m.status === 'OBSERVATION' ? '观察期' : '正常' }}）
          </option>
        </select>
        <button class="btn btn-primary" style="margin-left:auto;" @click="openNewModal">+ 发起新一轮六维评估</button>
      </div>
    </div>

    <div v-if="profile" class="grid-2" style="margin-bottom:18px;">
      <!-- 左：六维能力雷达图 -->
      <div class="card">
        <div class="card-title">
          <span>六维个人能力画像 · {{ profile.member.name }}</span>
          <span v-if="profile.latest" class="badge badge-blue">综合均分 {{ profile.latest.overall_score }}</span>
        </div>
        <AbilityRadarChart v-if="profile.latest" :latest="profile.latest" :previous="profile.previous" />
        <div v-else style="text-align:center;padding:40px;color:#94a3b8;">
          该成员尚未开展能力评估，请点击右上角「发起新一轮六维评估」
        </div>
        <div v-if="profile.latest?.summary" style="margin-top:12px;padding:10px 12px;background:#f8fafc;border-radius:8px;font-size:13px;color:#334155;">
          <strong>最新诊断评语：</strong>{{ profile.latest.summary }}
        </div>
      </div>

      <!-- 右：自动薄弱项诊断 + 题库补强题单闭环 -->
      <div style="display:flex;flex-direction:column;gap:18px;">
        <div class="card">
          <div class="card-title">
            <span>薄弱项自动识别清单（&lt; 70 分重点补强 · FR-AB-004）</span>
          </div>
          <div v-if="profile.latest?.weak_points?.length" style="display:flex;flex-direction:column;gap:10px;">
            <div
              v-for="w in profile.latest.weak_points"
              :key="w.dimension_key"
              style="padding:11px 13px;border-radius:10px;border:1px solid #fde68a;background:#fffbeb;"
            >
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:14px;color:#92400e;">{{ w.dimension_label }}（{{ w.score }} 分）</strong>
                <span :class="['badge', w.level === '高优先补强' ? 'badge-red' : w.level === '重点提升' ? 'badge-amber' : 'badge-green']">
                  {{ w.level }}
                </span>
              </div>
              <div style="font-size:12px;color:#78350f;margin-top:5px;">{{ w.suggestion }}</div>
            </div>
          </div>
          <div v-else style="font-size:13px;color:#94a3b8;">暂无诊断记录</div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>智能匹配补强题单（衔接后续训练规划 BR-007）</span>
            <router-link to="/question-bank" class="btn btn-sm">前往题库 →</router-link>
          </div>
          <div v-if="profile.recommended_lists?.length" style="display:flex;flex-direction:column;gap:10px;">
            <div
              v-for="pl in profile.recommended_lists"
              :key="pl.id"
              style="padding:10px 12px;border:1px solid #dbeafe;background:#eff6ff;border-radius:10px;"
            >
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:13px;color:#1e40af;">{{ pl.title }}</strong>
                <span class="badge badge-blue">{{ pl.problem_count }} 题</span>
              </div>
              <div style="font-size:12px;color:#475569;margin:4px 0;">{{ pl.description }}</div>
              <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:4px;">
                <span v-for="p in pl.problems" :key="p.code" class="badge badge-gray">{{ p.code }} {{ p.title }}</span>
              </div>
            </div>
          </div>
          <div v-else style="font-size:13px;color:#94a3b8;">当前薄弱维度暂未关联专项题单，可在题库模块创建</div>
        </div>
      </div>
    </div>

    <!-- 历次评估对比时间轴 (FR-AB-005) -->
    <div v-if="profile" class="card">
      <div class="card-title"><span>历次能力评估记录与训练前后对比 (FR-AB-005)</span></div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>周期 / 评估名称</th>
              <th>语言基础</th>
              <th>基础算法</th>
              <th>模拟逻辑</th>
              <th>边界处理</th>
              <th>知识点组合</th>
              <th>代码调试</th>
              <th>综合均分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in profile.history" :key="h.id">
              <td>
                <strong>{{ h.assessment_name }}</strong>
                <div style="font-size:12px;color:#64748b;">{{ h.cycle }}</div>
              </td>
              <td :style="scoreStyle(h.lang_basic)">{{ h.lang_basic }}</td>
              <td :style="scoreStyle(h.basic_algo)">{{ h.basic_algo }}</td>
              <td :style="scoreStyle(h.simulation_logic)">{{ h.simulation_logic }}</td>
              <td :style="scoreStyle(h.boundary_handling)">{{ h.boundary_handling }}</td>
              <td :style="scoreStyle(h.knowledge_combo)">{{ h.knowledge_combo }}</td>
              <td :style="scoreStyle(h.coding_debug)">{{ h.coding_debug }}</td>
              <td><span class="badge badge-blue">{{ h.overall_score }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 弹窗：发起新一轮六维评估 -->
    <div v-if="showModal" class="modal-mask" @click.self="showModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新增竞赛会员六维能力评估 (FR-AB-001/002)</span></div>
        <div class="form-grid">
          <div class="form-field"><label>评估名称</label><input v-model="form.assessment_name" class="input" /></div>
          <div class="form-field"><label>评估周期</label><input v-model="form.cycle" class="input" /></div>
          <div class="form-field"><label>编程语言基础 (0-100)</label><input v-model.number="form.lang_basic" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field"><label>基础算法 (0-100)</label><input v-model.number="form.basic_algo" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field"><label>模拟与逻辑实现 (0-100)</label><input v-model.number="form.simulation_logic" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field"><label>边界处理 (0-100)</label><input v-model.number="form.boundary_handling" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field"><label>知识点组合应用 (0-100)</label><input v-model.number="form.knowledge_combo" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field"><label>代码实现与调试 (0-100)</label><input v-model.number="form.coding_debug" type="number" min="0" max="100" class="input" /></div>
          <div class="form-field full"><label>综合分析与补强建议</label><textarea v-model="form.summary" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="submitAssessment">生成能力画像并更新薄弱项</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import AbilityRadarChart from '../components/AbilityRadarChart.vue'

const emit = defineEmits(['notify'])
const competitionMembers = ref([])
const selectedMemberId = ref('')
const profile = ref(null)
const showModal = ref(false)

const form = reactive({
  assessment_name: '2026冬季阶段复评',
  cycle: '2026-S3',
  lang_basic: 88,
  basic_algo: 82,
  simulation_logic: 76,
  boundary_handling: 64,
  knowledge_combo: 78,
  coding_debug: 74,
  summary: ''
})

async function init() {
  try {
    const list = await api.getMembers({ direction: 'COMPETITION' })
    competitionMembers.value = list
    if (list.length) {
      // 默认选中尚思彤或第一个成员，展示清晰的薄弱项与双层雷达图
      const preferred = list.find(m => m.name === '尚思彤') || list[0]
      selectedMemberId.value = preferred.id
      await loadProfile()
    }
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function loadProfile() {
  if (!selectedMemberId.value) return
  try {
    profile.value = await api.getMemberAbilityProfile(selectedMemberId.value)
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function openNewModal() {
  if (profile.value?.latest) {
    form.lang_basic = profile.value.latest.lang_basic
    form.basic_algo = profile.value.latest.basic_algo
    form.simulation_logic = profile.value.latest.simulation_logic
    form.boundary_handling = profile.value.latest.boundary_handling
    form.knowledge_combo = profile.value.latest.knowledge_combo
    form.coding_debug = profile.value.latest.coding_debug
  }
  showModal.value = true
}

async function submitAssessment() {
  try {
    await api.createAbilityAssessment({
      member_id: selectedMemberId.value,
      ...form
    })
    showModal.value = false
    emit('notify', { message: '新一轮能力画像已生成，薄弱项清单与推荐题单已同步更新！' })
    await loadProfile()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function scoreStyle(v) {
  return v < 70 ? { color: '#dc2626', fontWeight: 700 } : { color: '#0f172a', fontWeight: 600 }
}

onMounted(init)
</script>
