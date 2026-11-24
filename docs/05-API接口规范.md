# RESTful API 接口规范文档

> 基础路径：`http://127.0.0.1:8000/api/v1`
> 交互式在线文档：启动后端后访问 `http://127.0.0.1:8000/docs`（FastAPI 自动生成 Swagger UI）

---

## 一、通用接口设计规范

1. **协议与格式**：HTTP/1.1 + JSON（`Content-Type: application/json; charset=utf-8`）。
2. **命名风格**：URL 路径使用小写连字符（如 `/question-bank/problem-lists`），JSON 字段统一使用下划线 `snake_case`。
3. **HTTP 状态码规范**：
   - `200 OK`：查询、更新、状态流转成功。
   - `201 Created`：创建资源成功。
   - `400 Bad Request`：违反业务规则（如非备选会员尝试转正、非竞赛会员尝试能力评估）。
   - `404 Not Found`：目标资源不存在。
   - `409 Conflict`：唯一键冲突（如学号/题号/标签名重复）。
   - `422 Unprocessable Entity`：Pydantic 入参类型或范围校验失败。
4. **错误响应格式**：统一返回 FastAPI 标准 `{"detail": "具体错误说明"}`。

---

## 二、协会管理接口（`/api/v1/association`）

| 方法 | 路径 | 需求编号 | 说明 |
| :--- | :--- | :--- | :--- |
| `GET` | `/applications` | FR-AM-001 | 查询入会申请列表（支持按 `status` 筛选） |
| `POST` | `/applications` | FR-AM-001 | 提交新的入会申请 |
| `POST` | `/applications/{id}/review` | FR-AM-002 | 审核申请；通过时自动创建 `CANDIDATE` 备选会员（BR-001） |
| `GET` | `/members` | FR-AM-004 | 多条件检索会员（`keyword` / `stage` / `direction` / `status` / `department`） |
| `POST` | `/members` | FR-AM-004 | 直接新增会员档案 |
| `GET` | `/members/{id}` | FR-AM-010 | 获取会员完整个人档案（基本信息+考核+任职+奖惩+能力评估+状态日志） |
| `PUT` | `/members/{id}` | FR-AM-004 | 更新会员基础信息与部门 |
| `POST` | `/members/{id}/promote` | FR-AM-003 | 备选会员入会考核通过，转正为 `FORMAL` 并指定竞赛/非竞赛方向（BR-002） |
| `POST` | `/members/{id}/status` | FR-AM-007 | 手动变更会员管理状态（观察/确认清退/主动退会/恢复正常）并写操作日志 |
| `GET` | `/assessments` | FR-AM-005/006 | 查询周期会员考核记录（支持按会员、方向筛选） |
| `POST` | `/assessments` | FR-AM-005..007 | 录入周期考核，自动执行 BR-003 状态流转（单次不合格→观察，连续不合格→待清退） |
| `GET` | `/rewards` | FR-AM-008 | 查询优秀会员公示与奖惩记录 |
| `POST` | `/rewards` | FR-AM-008 | 新增奖惩或评优记录 |
| `GET` | `/positions` | FR-AM-009 | 查询部门组织与任职履历 |
| `POST` | `/positions` | FR-AM-009 | 新增部门任职记录 |

---

## 三、题库管理接口（`/api/v1/question-bank`）

| 方法 | 路径 | 需求编号 | 说明 |
| :--- | :--- | :--- | :--- |
| `GET` | `/tags` | FR-QB-001 | 查询全部知识点与实现能力标签（支持 `category` 过滤） |
| `POST` | `/tags` | FR-QB-001 | 新增算法知识点或实现能力标签 |
| `GET` | `/problems` | FR-QB-003 | 组合检索题目：`keyword`、`difficulty`、`source`、`tag_ids`（逗号分隔）、`match_mode`（`all`/`any`） |
| `POST` | `/problems` | FR-QB-002/004 | 新增题目并绑定多个标签 ID（BR-006） |
| `GET` | `/problems/{id}` | FR-QB-002/005 | 查看题目完整题面、样例、标签与全部题解 |
| `PUT` | `/problems/{id}` | FR-QB-002/004 | 编辑题目信息及重绑知识点标签 |
| `DELETE` | `/problems/{id}` | FR-QB-002 | 删除题目（同时级联清理多对多关联与题解） |
| `POST` | `/problems/{id}/solutions` | FR-QB-005 | 新增题解（思路、参考代码、语言、作者） |
| `GET` | `/problem-lists` | FR-QB-006 | 查询专题题单列表（含包含题目有序明细） |
| `POST` | `/problem-lists` | FR-QB-006 | 新建题单并按顺序绑定题目列表 |
| `GET` | `/stats` | FR-QB-007 | 获取题库统计（总量、难度分布、来源分布、各知识点/能力标签覆盖题数） |

---

## 四、个人能力评估接口（`/api/v1/ability`）

| 方法 | 路径 | 需求编号 | 说明 |
| :--- | :--- | :--- | :--- |
| `GET` | `/assessments` | FR-AB-001/005 | 查询个人能力评估记录（支持按 `member_id` 筛选） |
| `POST` | `/assessments` | FR-AB-001..004 | 提交竞赛会员六维能力评估，自动计算均分与薄弱项清单（BR-005） |
| `GET` | `/members/{member_id}/profile` | FR-AB-003..005 | 获取指定竞赛会员能力画像、最新/历史评估对比数据、薄弱项及智能推荐题单 |

---

## 五、系统辅助看板接口（`/api/v1/dashboard`）

| 方法 | 路径 | 需求编号 | 说明 |
| :--- | :--- | :--- | :--- |
| `GET` | `/overview` | FR-SYS-001/002 | 获取仪表盘核心 KPI、会员状态分布、题库概览、50%里程碑进度、公告列表与近期操作日志 |
| `POST` | `/announcements` | FR-SYS-002 | 发布新的协会/训练/赛事通知公告 |
