# SDD 强制开发规则与业务约束规范（AI 协作与 PR 审查唯一红线）

> 本文档是所有 AI 代码生成任务与 Code Reviewer 审查 PR 的唯一硬约束基准（业务规则编号严格与 `docs/01-需求分析文档.md` 的 `BR-001 ~ BR-010` 一一对应）。任何偏离下述规则的产出均不得合入 `develop` 分支。

## 1. 核心业务规则强约束（BR-001 ~ BR-010）

1. **[BR-001] 备选会员前置规则**：竞赛类申请者通过资格审核后必须先进入 `CANDIDATE`（备选会员）阶段，不可跳过入会考核直接成为 `FORMAL`（正式会员）。
2. **[BR-002] 阶段、方向与职务正交分离**：
   - `stage`（会员阶段）：`CANDIDATE` | `FORMAL` | `EXITED`
   - `direction`（会员方向，仅正式会员有效）：`COMPETITION`（竞赛会员） | `NON_COMPETITION`（非竞赛会员）
   - `status`（管理状态）：`ACTIVE`（正常） | `OBSERVATION`（观察） | `DISMISSAL_PENDING`（待清退） | `DISMISSED`（已清退） | `WITHDRAWN`（主动退会）
   - 协会职务（会长/副会长/部长/副部长/干事）必须在独立的 `org_positions` 表中维护，**严禁**作为会员类型字段。
3. **[BR-003] 考核驱动状态自动流转**：
   - 单次周期考核 `passed == False`：若当前为 `ACTIVE`，自动流转为 `OBSERVATION`（观察状态），并记录 `consecutive_failures = 1`。
   - 连续周期考核不合格（`consecutive_failures >= 2`）：自动流转为 `DISMISSAL_PENDING`（进入清退流程）。
   - 周期考核通过（`passed == True`）：重置 `consecutive_failures = 0`，若原为 `OBSERVATION` 则恢复为 `ACTIVE`。
4. **[BR-004] 考核指标差异化**：竞赛会员考核必须记录训练完成度、考勤、模拟赛与竞赛奖项表现；非竞赛会员考核必须记录工作任务、值班考勤、工作质量与协作贡献。
5. **[BR-005] 能力评估独立于会员考核**：`ability_assessments` 仅面向竞赛会员，独立建表与独立流程，绝不与 `member_assessments` 混用；其核心输出为 6 维能力画像与薄弱项清单（低于 70 分自动标定为薄弱项）。
6. **[BR-006] 题目-知识点多对多及难度解耦**：
   - 题目综合难度 `difficulty`（入门/普及/提高/省选/NOI）与知识点/能力标签 `tags` 分开维护。
   - 通过关联表 `problem_tag_rel` 实现 N:M 多对多关联，支持 `match_mode=all`（交集）与 `match_mode=any`（并集）组合检索。
   - 标签类型区分为 `KNOWLEDGE`（算法知识点）与 `ABILITY`（实现能力标签，如模拟、逻辑实现、边界处理）。
7. **[BR-007] 训练规划以个人能力评估为主要输入（Sprint 3）**：
   - 创建个人训练规划时，必须读取目标竞赛会员最近一次 `ability_assessments` 记录中的薄弱项（`weak_points`）并关联匹配题库题单（`problem_lists.target_dimension`）。
   - 计划表须留存 `source_assessment_id` 与来源快照，保证历史可回溯；**严禁**训练模块反向修改 `ability_assessments`，也**严禁**为非竞赛会员创建个人能力补强计划（返回 `400`）。
8. **[BR-008] 暑假集训与 XCPC 赛事结果关联队伍档案（Sprint 4）**：
   - 暑假集训、多校训练、XCPC 网络预选赛及正赛结果必须通过非空外键 `team_id` 关联到队伍档案（`teams`），成员变动通过追加调整流水记录，**严禁**队员离队后覆盖改写历史队伍赛事成绩。
   - 非 XCPC 赛事（蓝桥杯、天梯赛、码蹄杯、百度之星）采用个人制，挂 `member_id`。
9. **[BR-009] 校赛决赛确认与候补递补规则（Sprint 4）**：
   - 校赛采用**个人选手制**（关联 `member_id` 或报名学号，便于成绩回流会员考核与个人能力评估）。
   - 晋级决赛前必须执行参赛确认；若选手放弃或逾期未确认（须标记 `auto=True`），系统须在同一数据库事务内按初赛排名 `prelim_rank` 升序从候补池 `WAITLISTED` 自动递补首位选手为 `PROMOTED` 并写操作日志。
   - 重复确认返回 `400`；**严禁**将校赛放弃参赛自动联动到 `BR-003` 会员管理状态。
10. **[BR-010] 线上校赛异常行为留存核查材料与人工裁决（Sprint 4）**：
    - 线上初赛异常行为记录仅留存 `evidence_url` 与描述材料，初始状态固定为 `PENDING_REVIEW`，原始材料不可覆盖或删除。
    - **严禁**系统自动判作弊、自动取消成绩（DQ）或自动清退会员；必须通过独立人工复核接口写入复核人、复核时间与三值结论枚举：`CONFIRMED_VIOLATION` | `EXONERATED` | `NEED_MORE_EVIDENCE`。

## 2. 工程与接口通用约束（G-01 ~ G-06）

- **[G-01] 数据可追溯性（Append-Only）**：所有状态变更、考核记录、任职履历、能力评估、队伍调整与操作日志均保留时间戳与历史记录，严禁物理覆盖历史评估/成绩数据。
- **[G-02] 种子数据按域/按表判空幂等**：`backend/app/seed.py` 必须按业务域/表分别判空幂等初始化（例如 `if db.query(TrainingPlan).first() is None:`），**严禁**仅用顶层 `Member` 判空全局早退导致老数据库升级后新表无演示数据。
- **[G-03] 无 Alembic 迁移约束**：本阶段使用 SQLAlchemy `create_all` 只建新表不改旧表列，Sprint 3/4 须全部采用新增表设计，严禁修改既有 14 张表的列定义。
- **[G-04] Python 3.9 + FastAPI + Ruff 规范**：
  - 兼容 Python 3.9：FastAPI 路由参数与 Pydantic 模型禁止使用 `X | None`、`match`、`datetime.UTC`，统一使用 `Optional[...]`、`list[...]`、`dict[...]`；禁止引入 `from __future__ import annotations`。
  - 路由与业务逻辑中禁止调用已废弃的 `datetime.utcnow()`，改用 `datetime.now(timezone.utc).replace(tzinfo=None)`。
  - FastAPI 静态路径必须声明在动态路径参数之前（如 `/teams/recommend` 必须声明在 `/teams/{team_id}` 之前）。
  - 统一前缀 `/api/v1/{module}`；状态码语义：`200` 查询/流转、`201` 创建、`400` 业务冲突、`404` 不存在、`409` 唯一键冲突、`422` 参数校验失败；所有出参必须经过 Pydantic Schema 或显式字典序列化，禁止直接返回未序列化 ORM 对象。
- **[G-05] 模块化自动化验收测试**：每个核心接口与业务规则（`BR-001 ~ BR-010`）均须在 `backend/tests/` 下有对应 pytest 自动化用例（允许按迭代拆分为 `test_api.py`、`test_sprint3_training.py`、`test_sprint4_contest.py`、`test_sprint3_4.py`），测试文件必须通过 `ICPC_DATABASE_URL` 指向独立临时 SQLite 库，且不得破坏既有 7 条用例。
- **[G-06] 前后端解耦与纯净提交**：前端禁止硬编码模拟业务数据，统一经 `frontend/src/api/client.js` 访问后端；严禁向 Git 提交 `*.db`、`.venv/`、`node_modules/`、`frontend/dist/` 或无关目录。
- **[G-07] 全中文提交与 PR 规范**：所有 Git Commit 信息、PR 标题及说明统一使用中文（格式：`<type>(<scope>): <中文说明>`，例如 `feat(training): 新增关联能力薄弱项的个人训练计划接口`），便于团队协作与课程验收归档。
