<template>
  <div>
    <div class="tabs">
      <button :class="['tab-btn', activeTab === 'problems' && 'active']" @click="activeTab = 'problems'">
        题目多标签检索 ({{ problems.length }})
      </button>
      <button :class="['tab-btn', activeTab === 'tags' && 'active']" @click="activeTab = 'tags'">
        知识点与能力标签 ({{ tags.length }})
      </button>
      <button :class="['tab-btn', activeTab === 'lists' && 'active']" @click="activeTab = 'lists'">
        专题题单管理 ({{ problemLists.length }})
      </button>
      <button :class="['tab-btn', activeTab === 'stats' && 'active']" @click="activeTab = 'stats'">
        题库覆盖统计 (FR-QB-007)
      </button>
    </div>

    <!-- Tab 1: 多对多组合检索题库 -->
    <div v-if="activeTab === 'problems'" class="card">
      <div class="toolbar">
        <input v-model="query.keyword" class="input" placeholder="检索题号 / 标题 / 题面关键词..." @keyup.enter="loadProblems" />
        <select v-model="query.difficulty" class="select" @change="loadProblems">
          <option value="">全部难度</option>
          <option v-for="d in difficulties" :key="d" :value="d">{{ d }}</option>
        </select>
        <select v-model="query.source" class="select" @change="loadProblems">
          <option value="">全部来源</option>
          <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="query.match_mode" class="select" @change="loadProblems">
          <option value="all">多标签交集 (AND：同时满足)</option>
          <option value="any">多标签并集 (OR：满足任一)</option>
        </select>
        <button class="btn" @click="resetQuery">重置</button>
        <button class="btn btn-primary" style="margin-left:auto;" @click="showProblemModal = true">+ 录入新题目</button>
      </div>

      <!-- 知识点 & 实现能力标签点选筛选区 (BR-006) -->
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:16px;">
        <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:8px;">
          按知识点 / 实现能力标签组合筛选（已选 {{ selectedTagIds.length }} 个 · 点击切换）：
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:7px;">
          <button
            v-for="tag in tags"
            :key="tag.id"
            :class="[
              'chip',
              selectedTagIds.includes(tag.id)
                ? (tag.category === 'KNOWLEDGE' ? 'selected-knowledge' : 'selected-ability')
                : ''
            ]"
            @click="toggleFilterTag(tag.id)"
          >
            <span>{{ tag.category === 'ABILITY' ? '⚡' : '#' }} {{ tag.name }}</span>
          </button>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>题号 / 题目名称</th>
              <th>综合难度</th>
              <th>来源</th>
              <th>关联知识点与能力标签 (N:M)</th>
              <th>题解</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in problems" :key="p.id">
              <td>
                <strong>{{ p.code }} · {{ p.title }}</strong>
              </td>
              <td><span :class="['badge', diffBadge(p.difficulty)]">{{ p.difficulty }}</span></td>
              <td><span class="badge badge-gray">{{ p.source }}</span></td>
              <td>
                <div style="display:flex;flex-wrap:wrap;gap:5px;">
                  <span
                    v-for="t in p.tags"
                    :key="t.id"
                    :class="['badge', t.category === 'KNOWLEDGE' ? 'badge-blue' : 'badge-purple']"
                  >
                    {{ t.name }}
                  </span>
                </div>
              </td>
              <td>{{ p.solution_count }} 篇</td>
              <td>
                <div style="display:flex;gap:6px;">
                  <button class="btn btn-sm" @click="openDetail(p.id)">题面与题解</button>
                  <button class="btn btn-danger btn-sm" @click="removeProblem(p)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="!problems.length">
              <td colspan="6" style="text-align:center;color:#94a3b8;padding:28px;">当前组合条件下暂无匹配题目</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab 2: 知识点与实现能力标签 -->
    <div v-if="activeTab === 'tags'" class="grid-2">
      <div class="card">
        <div class="card-title"><span>算法知识点（KNOWLEDGE）与实现能力标签（ABILITY）</span></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>标签名称</th>
                <th>类别</th>
                <th>关联题数</th>
                <th>说明</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in tags" :key="t.id">
                <td><strong>{{ t.name }}</strong></td>
                <td>
                  <span :class="['badge', t.category === 'KNOWLEDGE' ? 'badge-blue' : 'badge-purple']">
                    {{ t.category === 'KNOWLEDGE' ? '算法知识点' : '实现能力标签' }}
                  </span>
                </td>
                <td>{{ t.problem_count }}</td>
                <td style="font-size:12px;color:#64748b;">{{ t.description }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title"><span>新增知识点或能力标签 (FR-QB-001)</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>标签名称</label><input v-model="tagForm.name" class="input" placeholder="如：树状数组 / 对拍验证" /></div>
          <div class="form-field full">
            <label>标签分类</label>
            <select v-model="tagForm.category" class="select">
              <option value="KNOWLEDGE">算法知识点 (KNOWLEDGE)</option>
              <option value="ABILITY">实现能力标签 (ABILITY，如模拟/边界处理)</option>
            </select>
          </div>
          <div class="form-field full"><label>说明</label><textarea v-model="tagForm.description" class="textarea"></textarea></div>
        </div>
        <div style="margin-top:14px;">
          <button class="btn btn-primary" @click="submitTag">创建标签</button>
        </div>
      </div>
    </div>

    <!-- Tab 3: 专题题单管理 -->
    <div v-if="activeTab === 'lists'">
      <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
        <button class="btn btn-primary" @click="showListModal = true">+ 新建专题补强题单</button>
      </div>
      <div class="grid-2">
        <div v-for="pl in problemLists" :key="pl.id" class="card">
          <div class="card-title">
            <span>{{ pl.title }}</span>
            <span class="badge badge-blue">{{ pl.theme }}</span>
          </div>
          <p style="font-size:13px;color:#475569;margin-top:0;">{{ pl.description }}</p>
          <div style="font-size:12px;color:#64748b;margin-bottom:10px;">
            适用阶段：{{ pl.target_stage }}
            <span v-if="pl.target_dimension" class="badge badge-purple" style="margin-left:6px;">
              联动薄弱维度：{{ dimName(pl.target_dimension) }}
            </span>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;">
            <div
              v-for="item in pl.items"
              :key="item.problem_id"
              style="display:flex;justify-content:space-between;align-items:center;padding:7px 10px;background:#f8fafc;border-radius:8px;font-size:13px;"
            >
              <span>{{ item.sort_order }}. <strong>{{ item.code }}</strong> {{ item.title }}</span>
              <span :class="['badge', diffBadge(item.difficulty)]">{{ item.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 4: 题库覆盖统计 -->
    <div v-if="activeTab === 'stats' && stats" class="grid-2">
      <div class="card">
        <div class="card-title"><span>知识点与能力标签覆盖题数排行</span></div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div v-for="item in stats.tag_coverage" :key="item.id">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
              <span>
                <strong>{{ item.name }}</strong>
                <span :class="['badge', item.category === 'KNOWLEDGE' ? 'badge-blue' : 'badge-purple']" style="margin-left:6px;">
                  {{ item.category === 'KNOWLEDGE' ? '知识点' : '能力' }}
                </span>
              </span>
              <span>{{ item.count }} 题</span>
            </div>
            <div class="progress-bar-light">
              <div class="progress-fill" :style="{ width: Math.min(100, (item.count / Math.max(1, stats.total_problems)) * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-title"><span>题目来源分布</span></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>题目来源</th><th>收录数量</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in stats.source_distribution" :key="s.source">
                <td><strong>{{ s.source }}</strong></td>
                <td>{{ s.count }} 题</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 弹窗：题目详情与题解管理 (FR-QB-005) -->
    <div v-if="detailProblem" class="modal-mask" @click.self="detailProblem = null">
      <div class="modal-box" style="max-width:760px;">
        <div class="card-title">
          <span>{{ detailProblem.code }} · {{ detailProblem.title }}</span>
          <button class="btn btn-sm" @click="detailProblem = null">关闭</button>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
          <span :class="['badge', diffBadge(detailProblem.difficulty)]">{{ detailProblem.difficulty }}</span>
          <span class="badge badge-gray">{{ detailProblem.source }}</span>
          <span v-for="t in detailProblem.tags" :key="t.id" :class="['badge', t.category === 'KNOWLEDGE' ? 'badge-blue' : 'badge-purple']">{{ t.name }}</span>
          <a v-if="detailProblem.external_url" :href="detailProblem.external_url" target="_blank" style="font-size:12px;margin-left:auto;">原题链接 ↗</a>
        </div>
        <p style="font-size:13px;color:#334155;background:#f8fafc;padding:12px;border-radius:8px;">{{ detailProblem.statement }}</p>
        <div v-if="detailProblem.sample_input" class="grid-2" style="margin-bottom:14px;">
          <div>
            <div style="font-size:12px;font-weight:700;margin-bottom:4px;">样例输入</div>
            <div class="code-block">{{ detailProblem.sample_input }}</div>
          </div>
          <div>
            <div style="font-size:12px;font-weight:700;margin-bottom:4px;">样例输出</div>
            <div class="code-block">{{ detailProblem.sample_output }}</div>
          </div>
        </div>

        <h4 style="margin:12px 0 8px;font-size:14px;">沉淀题解与参考代码 ({{ detailProblem.solutions.length }})</h4>
        <div v-for="sol in detailProblem.solutions" :key="sol.id" style="border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;">
            <strong>{{ sol.title }}</strong>
            <span style="font-size:12px;color:#64748b;">{{ sol.author_name }} · {{ sol.language }}</span>
          </div>
          <p style="font-size:13px;color:#475569;margin:6px 0;">{{ sol.idea }}</p>
          <div v-if="sol.code" class="code-block">{{ sol.code }}</div>
        </div>

        <div style="border-top:1px solid #e2e8f0;padding-top:12px;margin-top:12px;">
          <strong style="font-size:13px;">补充新题解</strong>
          <div class="form-grid" style="margin-top:8px;">
            <div class="form-field"><label>题解标题</label><input v-model="solForm.title" class="input" /></div>
            <div class="form-field"><label>作者</label><input v-model="solForm.author_name" class="input" /></div>
            <div class="form-field full"><label>解题思路</label><textarea v-model="solForm.idea" class="textarea"></textarea></div>
            <div class="form-field full"><label>参考代码片段</label><textarea v-model="solForm.code" class="textarea"></textarea></div>
          </div>
          <button class="btn btn-primary btn-sm" style="margin-top:10px;" @click="submitSolution">保存题解</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：录入新题目 -->
    <div v-if="showProblemModal" class="modal-mask" @click.self="showProblemModal = false">
      <div class="modal-box">
        <div class="card-title"><span>录入新题目并关联多标签 (BR-006)</span></div>
        <div class="form-grid">
          <div class="form-field"><label>题号</label><input v-model="problemForm.code" class="input" placeholder="如：ICPC-1010" /></div>
          <div class="form-field"><label>题目名称</label><input v-model="problemForm.title" class="input" /></div>
          <div class="form-field">
            <label>综合难度（与标签解耦）</label>
            <select v-model="problemForm.difficulty" class="select">
              <option v-for="d in difficulties" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="form-field">
            <label>题目来源</label>
            <select v-model="problemForm.source" class="select">
              <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-field full"><label>外部链接（选填）</label><input v-model="problemForm.external_url" class="input" placeholder="https://..." /></div>
          <div class="form-field full"><label>题面描述</label><textarea v-model="problemForm.statement" class="textarea"></textarea></div>
          <div class="form-field full">
            <label>选择关联知识点与能力标签（可多选）</label>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px;">
              <button
                v-for="tag in tags"
                :key="tag.id"
                type="button"
                :class="['chip', problemForm.tag_ids.includes(tag.id) ? (tag.category === 'KNOWLEDGE' ? 'selected-knowledge' : 'selected-ability') : '']"
                @click="toggleProblemFormTag(tag.id)"
              >
                {{ tag.name }}
              </button>
            </div>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showProblemModal = false">取消</button>
          <button class="btn btn-primary" @click="submitProblem">保存题目</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：新建专题题单 -->
    <div v-if="showListModal" class="modal-mask" @click.self="showListModal = false">
      <div class="modal-box">
        <div class="card-title"><span>新建专题补强题单 (FR-QB-006)</span></div>
        <div class="form-grid">
          <div class="form-field full"><label>题单标题</label><input v-model="listForm.title" class="input" /></div>
          <div class="form-field"><label>训练主题</label><input v-model="listForm.theme" class="input" placeholder="如：动态规划" /></div>
          <div class="form-field">
            <label>对应能力薄弱维度</label>
            <select v-model="listForm.target_dimension" class="select">
              <option value="">通用专题</option>
              <option value="lang_basic">编程语言基础</option>
              <option value="basic_algo">基础算法</option>
              <option value="simulation_logic">模拟与逻辑实现</option>
              <option value="boundary_handling">边界处理</option>
              <option value="knowledge_combo">知识点组合应用</option>
              <option value="coding_debug">代码实现与调试</option>
            </select>
          </div>
          <div class="form-field full"><label>题单说明</label><textarea v-model="listForm.description" class="textarea"></textarea></div>
          <div class="form-field full">
            <label>勾选编排题目</label>
            <div style="max-height:160px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px;padding:8px;">
              <label v-for="p in allProblems" :key="p.id" style="display:flex;align-items:center;gap:8px;padding:4px 0;font-weight:400;">
                <input type="checkbox" :value="p.id" v-model="listForm.problem_ids" />
                <span>{{ p.code }} · {{ p.title }} ({{ p.difficulty }})</span>
              </label>
            </div>
          </div>
        </div>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px;">
          <button class="btn" @click="showListModal = false">取消</button>
          <button class="btn btn-primary" @click="submitProblemList">发布题单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'

const emit = defineEmits(['notify'])
const activeTab = ref('problems')
const difficulties = ['入门', '普及', '提高', '省选', 'NOI']
const sources = ['校内题库', 'Codeforces', 'AtCoder', '洛谷', '牛客']

const tags = ref([])
const problems = ref([])
const allProblems = ref([])
const problemLists = ref([])
const stats = ref(null)
const detailProblem = ref(null)

const query = reactive({ keyword: '', difficulty: '', source: '', match_mode: 'all' })
const selectedTagIds = ref([])

const showProblemModal = ref(false)
const problemForm = reactive({ code: '', title: '', difficulty: '普及', source: '校内题库', external_url: '', statement: '', tag_ids: [] })

const tagForm = reactive({ name: '', category: 'KNOWLEDGE', description: '' })
const solForm = reactive({ title: '', author_name: '题库组', idea: '', code: '', language: 'C++17' })

const showListModal = ref(false)
const listForm = reactive({ title: '', theme: '专题强化', target_stage: '日常训练', target_dimension: 'boundary_handling', description: '', problem_ids: [] })

async function loadProblems() {
  problems.value = await api.getProblems({
    ...query,
    tag_ids: selectedTagIds.value.join(',')
  })
}

async function loadAll() {
  try {
    const [t, p, lists, st] = await Promise.all([
      api.getTags(),
      api.getProblems(),
      api.getProblemLists(),
      api.getQuestionBankStats()
    ])
    tags.value = t
    allProblems.value = p
    problemLists.value = lists
    stats.value = st
    await loadProblems()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

function toggleFilterTag(id) {
  const idx = selectedTagIds.value.indexOf(id)
  if (idx >= 0) selectedTagIds.value.splice(idx, 1)
  else selectedTagIds.value.push(id)
  loadProblems()
}

function resetQuery() {
  query.keyword = ''
  query.difficulty = ''
  query.source = ''
  query.match_mode = 'all'
  selectedTagIds.value = []
  loadProblems()
}

function toggleProblemFormTag(id) {
  const idx = problemForm.tag_ids.indexOf(id)
  if (idx >= 0) problemForm.tag_ids.splice(idx, 1)
  else problemForm.tag_ids.push(id)
}

async function submitProblem() {
  try {
    await api.createProblem({ ...problemForm })
    showProblemModal.value = false
    Object.assign(problemForm, { code: '', title: '', statement: '', external_url: '', tag_ids: [] })
    emit('notify', { message: '题目录入成功，多对多标签关联已生效' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function openDetail(id) {
  detailProblem.value = await api.getProblemDetail(id)
}

async function submitSolution() {
  try {
    await api.addSolution(detailProblem.value.id, { ...solForm })
    solForm.title = ''
    solForm.idea = ''
    solForm.code = ''
    emit('notify', { message: '题解沉淀成功' })
    detailProblem.value = await api.getProblemDetail(detailProblem.value.id)
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function removeProblem(p) {
  try {
    await api.deleteProblem(p.id)
    emit('notify', { message: `已删除题目 ${p.code}` })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitTag() {
  try {
    await api.createTag({ ...tagForm })
    tagForm.name = ''
    tagForm.description = ''
    emit('notify', { message: '标签创建成功' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

async function submitProblemList() {
  try {
    await api.createProblemList({ ...listForm })
    showListModal.value = false
    listForm.title = ''
    listForm.description = ''
    listForm.problem_ids = []
    emit('notify', { message: '专题题单已发布' })
    await loadAll()
  } catch (err) {
    emit('notify', { message: err.message, type: 'err' })
  }
}

const diffBadge = (d) => ({ 入门: 'badge-green', 普及: 'badge-blue', 提高: 'badge-amber', 省选: 'badge-purple', NOI: 'badge-red' }[d] || 'badge-gray')
const dimName = (k) => ({
  lang_basic: '编程语言基础',
  basic_algo: '基础算法',
  simulation_logic: '模拟与逻辑实现',
  boundary_handling: '边界处理',
  knowledge_combo: '知识点组合应用',
  coding_debug: '代码实现与调试'
}[k] || k)

onMounted(loadAll)
</script>
