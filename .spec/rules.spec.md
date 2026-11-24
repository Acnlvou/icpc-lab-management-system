# SDD 强制开发规则与业务约束规范（AI 协作红线）

> 本文档是所有 AI 代码生成任务与人工 Code Review 的前置硬约束。任何偏离下述规则的产出均不得合入 `develop` 分支。

## 1. 业务规则强约束（对应需求文档 BR-001 ~ BR-010）

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
7. **[BR-007] 数据可追溯性**：所有状态变更、考核记录、任职变更、能力评估均必须保留时间戳与历史记录，严禁物理覆盖历史评估数据。

## 2. 工程与接口实现约束

- **API 前缀**：统一采用 `/api/v1/{module}`。
- **状态码语义**：查询成功 `200`，创建成功 `201`，参数校验失败 `422`，业务规则冲突 `400` / `409`，资源不存在 `404`。
- **数据校验**：后端所有入参和出参必须通过 Pydantic Schema 严格定义，禁止直接返回未序列化 ORM 对象。
- **前后端解耦**：前端禁止硬编码模拟业务数据（规划路线图静态展示除外），全部核心列表、详情、提交、流转操作均实时读写 FastAPI + SQLite。
- **自动化验收**：每个核心接口与业务规则（BR-001 ~ BR-007）都必须在 `backend/tests/test_api.py` 中具备对应的 pytest 自动化测试用例。
