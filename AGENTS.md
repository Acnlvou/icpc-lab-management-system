# AGENTS.md — ICPC 实验室管理系统 AI 协作开发与审查总则

> 本文件面向所有参与本仓库开发或代码审查的 AI Coding Agent 与协作者。**在编写、修改或审查任何代码前，必须完整遵守本文件全部条款。**

---

## 一、项目概况与开发范式

- **项目名称**：ICPC 实验室管理系统（`icpc-lab-management-system`）
- **开发团队**：Kcat 小组（《UML与软件工程建模》课程项目）
- **开发范式**：**Scrum 敏捷迭代 + SDD（规范驱动开发，Spec-Driven Development）**
- **技术栈**：
  - 后端：`Python 3.9+` + `FastAPI` + `SQLAlchemy 2.0` + `Pydantic v2` + `SQLite 3` + `pytest` + `ruff`
  - 前端：`Vue 3`（`<script setup>` 纯 JavaScript，**无 TypeScript**）+ `Vite` + `Vue Router 4` + 原生 CSS/SVG
- **当前进度**：已完成 50%（`v0.5.0-milestone`：协会管理、多标签题库、六维个人能力评估、统计看板）；当前处于 **Sprint 3（训练与寒暑假集训管理）** 与 **Sprint 4（队伍与校赛/非XCPC/XCPC竞赛管理）** 并行冲刺阶段。

### 唯一事实来源（Single Source of Truth，开工必读）
1. `.spec/rules.spec.md` — 十大业务规则（`BR-001 ~ BR-010`）与通用工程约束（`G-01 ~ G-07`）
2. `.spec/api.spec.yaml` — 全量冻结的 RESTful API 接口契约（含 Sprint 3 & 4 字段级 `snake_case` 请求/响应 Schema）
3. `.spec/project.spec.yaml` — 模块边界与里程碑划分
4. `docs/10-冲刺分工与实验记录总纲.md` — 4 人分工与终期交付清单
5. `docs/11-团队协作开发与AI代码审查方案.md` — 文件所有权与 PR 审查流程
6. `ruff.toml` & `.github/workflows/ci.yml` — 静态检查与自动化 CI 门禁

---

## 二、范围红线（严禁擅自加需求！）

1. **禁止中途私自新增「注册、登录、JWT 鉴权、RBAC 权限拦截」等需求表外功能**：
   - 功能需求表（`FR-*`）未单列注册/登录模块；非功能需求 `9.3 安全性`（身份识别与按职责限制操作范围）已明确排期在 **Sprint 3 & Sprint 4 核心业务 100% 完成并合入 `develop` 之后**，再统一开独立的 `feature/auth-role` 轻量分支实现（演示账号登录 + 角色视角与按钮控制，不做复杂邮箱注册/找回密码）。
   - **Sprint 3 / Sprint 4 期间所有接口保持无鉴权直通**，严禁添加全局鉴权中间件导致既有 20 个接口、`test_api.py` 7 条用例或其他组员模块大面积报错返工。
2. **禁止擅自引入重型依赖**：
   - 前端**禁止**引入 TypeScript、Element Plus、Ant Design Vue、Pinia、ECharts 等重依赖；图标/图表沿用轻量原生 SVG 与 `frontend/src/styles/main.css` 语义样式类。
   - 后端**禁止**引入 Alembic、Redis、Celery 等外部中间件，也**禁止**改动 `backend/app/database.py` 的 SQLite 架构。
3. **禁止越界修改他人负责的模块文件**（见第五节所有权边界）。

---

## 三、十大核心业务规则硬红线（BR-001 ~ BR-010）

| 编号 | 强制要求 | 禁止事项 |
| :--- | :--- | :--- |
| **BR-001** | 竞赛类申请审核通过后必须先进入 `CANDIDATE`（备选会员），通过入会考核方可转正 `FORMAL` | 禁止跳过备选直接转正 |
| **BR-002** | `stage` / `direction` / `status` 三轴正交；协会职务独立存 `org_positions` 表 | 禁止把职务当会员类型 |
| **BR-003** | 周期考核单次不合格→`OBSERVATION`；连续 `>= 2` 次→`DISMISSAL_PENDING`；合格→重置计数并恢复 `ACTIVE` | 禁止手改状态破坏考核驱动逻辑 |
| **BR-004** | 竞赛会员与非竞赛会员采用差异化考核指标（`metrics_json`） | 禁止两类会员混用同一套指标 |
| **BR-005** | 个人能力评估（`ability_assessments`）独立于会员考核，仅面向 `direction == "COMPETITION"` | 禁止为非竞赛会员创建能力评估（应返回 `400`） |
| **BR-006** | 题目-标签 N:M（`problem_tag_rel`），区分 `KNOWLEDGE` / `ABILITY`，难度独立，支持 AND/OR 检索 | 禁止将难度耦合进标签 |
| **BR-007** | **个人训练规划**必须读取最近一次 `ability_assessments` 薄弱项并关联题库题单，留存 `source_assessment_id` 与快照 | 禁止反向修改 `ability_assessments`；禁止为非竞赛会员建个人能力补强计划（`400`） |
| **BR-008** | **暑假集训、多校训练、XCPC 网络预选赛与正赛结果**必须以非空 `team_id` 关联队伍档案；**非 XCPC** 按个人制挂 `member_id` | 禁止成员离队后覆写历史队伍成绩；禁止物理删除队伍 |
| **BR-009** | **校赛采用个人选手制（`member_id`）**；决赛前须参赛确认，放弃（状态统一锁定 `ABANDONED`）或逾期未确认（须标 `auto=True`）时在**同一事务内**按 `prelim_rank` 升序自动递补 `WAITLISTED` 首位为 `PROMOTED` 并写日志 | 重复确认须返回 `400`；禁止使用 `DECLINED`；**严禁**将校赛放弃参赛联动到 `BR-003` 会员管理状态 |
| **BR-010** | 线上校赛异常行为仅留存 `evidence_url` 与描述材料，初始状态固定 `PENDING_REVIEW`；须提供独立人工复核接口写入三值结论：`CONFIRMED_VIOLATION` / `EXONERATED` / `NEED_MORE_EVIDENCE` | **严禁**系统自动判作弊、自动取消成绩（DQ）或自动清退；禁止覆盖原始核查材料 |

---

## 四、工程与代码规范（违反即打回）

### 4.1 后端（Python / FastAPI / SQLite）
- **Python 3.9 语法兼容（强约束）**：
  - 路由参数与 Pydantic Schema 中**禁止**使用 `X | None`（PEP 604）、`match` 语句、`datetime.UTC`；统一使用 `Optional[...]`、`list[...]`、`dict[...]`。
  - **禁止**添加 `from __future__ import annotations`（与 FastAPI 在 Python 3.9 下运行时解析类型注解冲突，已在 `ruff.toml` 忽略 `FA100`）。
- **时间字段规范**：
  - 路由与业务逻辑、种子数据中**禁止**调用 `datetime.utcnow()`（Ruff `DTZ003` 报错），统一使用 `datetime.now(timezone.utc).replace(tzinfo=None)`。
- **FastAPI 路由与契约规范**：
  - 统一前缀 `/api/v1/{module}`；静态路径必须声明在动态路径之前（如 `/teams/recommend` 必须在 `/teams/{team_id}` 之前）。
  - **字段级契约与命名约定**：Sprint 3/4 入参与出参必须严格匹配 `.spec/api.spec.yaml` 的 `components.schemas`（统一 `snake_case`）；校赛放弃状态统一 `ABANDONED`；`POST /training/camps` 在 `camp_type == "SUMMER"` 时 `team_id` 必填非空；后端 ORM 模型类名统一约定为 `TrainingPlan` / `TrainingTask` / `TrainingCamp`（李靖宇）与 `Team` / `SchoolContest` / `XcpcResult` / `NonXcpcResult`（莫姝），方便合入后统一接入 Dashboard KPI。
  - 所有接口出参必须经 Pydantic Schema 或显式 dict 序列化，**严禁**直接 `return db.query(...)` 返回裸 ORM 对象。
  - HTTP 状态码：`200` 查询/流转、`201` 创建、`400` 业务规则冲突、`404` 不存在、`409` 唯一键冲突、`422` 参数校验失败。
- **数据库与 Seed 规范（无 Alembic）**：
  - Sprint 3 / Sprint 4 **只能新增数据表，严禁修改既有 14 张表的列定义**；所有外键必须显式声明 `ondelete`（`CASCADE` / `SET NULL`）；历史记录一律 Append-Only。
  - **`seed.py` 必须按域/按表判空幂等**（例如新增 `seed_training_data(db)` / `seed_contest_data(db)` 各自判空），**严禁**放在顶层 `if db.query(Member).first(): return` 之后导致老数据库升级时新表无法灌入演示数据。
- **自动化测试规范**：
  - 新增测试用例写在独立文件（如 `backend/tests/test_sprint3_training.py`、`test_sprint4_contest.py`、`test_sprint3_4.py`），顶部必须通过 `ICPC_DATABASE_URL` 指向独立临时 SQLite 库（参考 `test_api.py`），**不得修改或破坏 `test_api.py` 既有 7 条用例**。
  - 每个 `BR-007 ~ BR-010` 必须同时包含**正向流转断言 + 禁止事项负向断言**（如非竞赛会员建补强计划返回 `400`、重复确认校赛返回 `400` 等）。

### 4.2 前端（Vue 3 + Vite）
- 使用 `<script setup>` 组合式 API，纯 JavaScript。
- 全部后端请求统一封装在 `frontend/src/api/client.js`，禁止在组件里散落裸 `fetch` 或硬编码假数据。
- 样式复用 `frontend/src/styles/main.css` 已有语义类（`card`、`grid-2`、`toolbar`、`table-wrap`、`badge-*`、`modal-mask`、`form-grid`、`toast`），保持全站视觉风格一致。
- 关键状态流转操作（如校赛放弃触发候补递补、训练计划自动带出薄弱项）必须在操作成功后弹出清晰 `notify` 提示。

---

## 五、小组文件所有权与防冲突边界

| 成员 | GitHub Issue | 功能分支 | 专属新增文件（零冲突） | 仅允许末尾追加挂载的公共文件 |
| :--- | :---: | :--- | :--- | :--- |
| **李靖宇** | `#1` | `feature/training-camp` | `backend/app/routers/training.py`、`backend/tests/test_sprint3_training.py` | `models.py`、`schemas.py`、`main.py`、`seed.py` |
| **莫 姝** | `#2` | `feature/team-contest` | `backend/app/routers/contest.py`、`backend/tests/test_sprint4_contest.py` | `models.py`、`schemas.py`、`main.py`、`seed.py`、`docs/04`、`docs/05` |
| **尚思彤** | `#3` | `feature/frontend-training`（训练+竞赛单分支交付） | `frontend/src/views/TrainingView.vue`<br>`frontend/src/views/ContestView.vue` | `frontend/src/api/client.js`、`router.js`、`App.vue`、`DashboardView.vue`、`docs/06` |
| **覃爽爽** | `#4` | `feature/qa-acceptance` | `backend/tests/test_sprint3_4.py` | `docs/08-迭代任务拆分与测试验收报告.md` |

> **公共文件修改原则**：只允许在文件末尾追加新模块块或注册 1~2 行，**严禁重排、格式化或改写他人既有代码行**。
>
> **版本与跨分支裁决**：前端分支严禁修改 `backend/app/main.py`、`backend/app/routers/dashboard.py`、`backend/tests/test_api.py`；在 `#1` 与 `#2` 合入 `develop` 前，系统进度与版本统一保持 `50%` / `v0.5.0-milestone`，合入后再由组长统一升级至 `100%` / `v1.0.0`。

---

## 六、Git 分支、全中文提交与 PR 门禁

1. **分支铁律**：
   - **严禁直接向 `main` 或 `develop` 提交/推送代码**；严禁 `git push -f` 覆盖他人历史。
   - 每次开任务必须从最新 `develop` 切出 `feature/<模块名>` 分支；发起 Pull Request 时 **base 分支一律选 `develop`**。
2. **全中文提交与 PR 规范（`[G-07]`）**：
   - 所有 Commit 信息、PR 标题及说明**统一使用中文**，格式：`<type>(<scope>): <中文简要说明>`
   - 示例：
     - `feat(training): 新增联动能力薄弱项的个人训练计划接口`
     - `feat(contest): 实现校赛决赛确认与同事务候补递补流程`
     - `test(contest): 补充BR-008至BR-010正负向pytest验收用例`
     - `fix(frontend): 修复训练任务打卡弹窗状态刷新问题`
3. **严禁提交污染文件**：
   - 禁止提交 `*.db` / `*.db-*`、`.venv/`、`node_modules/`、`frontend/dist/`、`__pycache__/`、`.pytest_cache/`、`.ruff_cache/`、`.DS_Store`、`.vscode/`、`.env` 或任何与本项目无关的目录。
4. **提 PR 前本地必跑三道门禁（须与 `.github/workflows/ci.yml` 一致全绿）**：
   ```bash
   ruff check backend                                  # 必须 0 警告
   cd backend && PYTHONPATH=. .venv/bin/pytest -v      # 必须全量通过（含既有7条不回归）
   npm --prefix frontend run build                     # 必须 0 报错构建通过
   ```
5. **PR 模板与分支清理**：仅完整交付功能的 PR 填写 `Closes #<Issue编号>`（纯规范/文档前置 PR 仅引用 `#x` 避免误关 Issue），并列出涉及的 `FR-*` 与 `BR-*`；等 GitHub Actions 绿勾 ✅ 后再通知代码审查官 Review，PR 合并后顺手删除已合并的临时 `feature/*` 分支。

---

## 七、专职代码审查官（Code Reviewer Agent）职责边界

- **严格只读**：只拉取 PR diff、复跑本地检查并输出结构化审查报告（`APPROVE` 或 `REQUEST_CHANGES` + `P0 / P1` 清单 + `BR-001~010` 核对表），**严禁直接修改业务代码、严禁 commit 或 push**。
- **一票否决（P0）清单**：CI 未全绿、违反 `BR-001~010`、字段名偏离 `.spec/api.spec.yaml`（如校赛放弃误用 `DECLINED`）、前端提前升级 `100% / v1.0.0` 或越界修改后端文件、中途私自加登录/鉴权破坏既有接口、Python 3.9 不兼容或误用 `datetime.utcnow()`、`seed.py` 未按域幂等、改坏既有表列或既有 7 条测试、越界修改他人文件、夹带 `.db`/垃圾文件、Commit/PR 未使用中文。
