# ICPC 实验室管理系统（ICPC Lab Management System）

> 课程项目：《UML与软件工程建模》｜ 指导教师：刘卫平 ｜ 小组：Kcat（2024级软件工程）
> 开发范式：**Scrum 敏捷迭代 + SDD 规范驱动开发（Spec-Driven Development）**
> 技术栈：**Vue 3 + Vite + FastAPI + SQLAlchemy + SQLite**

---

## 一、项目简介与当前进度（50% 里程碑）

本项目面向高校 ICPC 协会与算法竞赛实验室，覆盖从**会员招募与生命周期管理 → 知识点题库与个人能力评估 → 日常训练与寒暑假集训 → 组队与校赛/XCPC竞赛管理**的完整业务闭环。

截至当前阶段（`v0.5.0-milestone`），项目整体开发进度约 **50%**，已完成全部 SDD 工程规范体系、前后端分离基础框架及三大核心业务模块：

| 模块 | 规划迭代 | 当前状态 | 对应需求编号 |
| :--- | :---: | :---: | :--- |
| SDD 规范体系与总体架构 | Sprint 0 | ✅ 已完成 | 全部基础架构与 BR-001 ~ BR-010 |
| **协会管理模块** | Sprint 1 | ✅ 已完成 | `FR-AM-001` ~ `FR-AM-010` |
| **题库与知识点标签模块** | Sprint 1-2 | ✅ 已完成 | `FR-QB-001` ~ `FR-QB-007` |
| **个人能力评估与画像模块** | Sprint 2 | ✅ 已完成 | `FR-AB-001` ~ `FR-AB-005` |
| **首页数据看板与辅助统计** | Sprint 2 | ✅ 已完成 | `FR-SYS-001` ~ `FR-SYS-003` |
| 训练与寒暑假集训管理 | Sprint 3 | 🚧 规划中 | `FR-TRN-*` / `FR-WIN-*` / `FR-SUM-*` |
| 组队与校赛/XCPC竞赛管理 | Sprint 4 | 🚧 规划中 | `FR-TEAM-*` / `FR-CMP-*` / `FR-NC-*` / `FR-XCPC-*` |

---

## 二、小组成员与分工（Kcat 小组）

| 角色 | 姓名 | 学号 | 文档阶段分工 | 系统开发阶段分工 |
| :---: | :---: | :---: | :--- | :--- |
| 组长 | 李靖宇 | 202421091067 | 需求分析、文档编写 | 需求与架构设计、SDD规范制定、后端核心框架 |
| 组员 | 尚思彤 | 202421091189 | 流程图绘制 | 前端开发（Vue 3 页面、状态流转与雷达图可视化） |
| 组员 | 莫 姝 | 202421091198 | 文档封面制作 | 后端业务模块开发（题库多对多模型、能力评估接口） |
| 组员 | 覃爽爽 | 202421091165 | 文档格式整理 | 功能测试、验收用例编写、Git分支与文档维护 |

---

## 三、完整规范与工程文档目录

本项目严格贯彻 **SDD（规范驱动开发）**，所有代码实现均以 `.spec/` 与 `docs/` 中的规范为唯一事实来源（Single Source of Truth）：

- **机器可读 SDD 规范 (`.spec/`)**
  - [.spec/project.spec.yaml](.spec/project.spec.yaml) — 项目范围、技术约束、模块边界与迭代里程碑规范
  - [.spec/rules.spec.md](.spec/rules.spec.md) — AI 辅助开发强制约束（代码规范、状态机规则、BR-001~BR-010 校验红线）
  - [.spec/api.spec.yaml](.spec/api.spec.yaml) — 后端 RESTful API 契约规范（OpenAPI 3.0 精简契约）
- **软件工程全套文档 (`docs/`)**
  1. [docs/01-需求分析文档.md](docs/01-需求分析文档.md) — 完整需求规格说明（功能需求、数据需求、非功能需求、核心规则与 Mermaid 流程图）
  2. [docs/02-SDD规范驱动开发与AI协作流程.md](docs/02-SDD规范驱动开发与AI协作流程.md) — Scrum + SDD 方法论、AI 六步开发流程、Prompt 规范与人工审查清单
  3. [docs/03-系统架构与详细设计文档.md](docs/03-系统架构与详细设计文档.md) — Vue 3 + FastAPI + SQLite 分层架构、业务状态机与模块交互设计
  4. [docs/04-数据库设计规范.md](docs/04-数据库设计规范.md) — SQLite 逻辑/物理模型、ER 图、多对多关联表及数据完整性约束
  5. [docs/05-API接口规范.md](docs/05-API接口规范.md) — 接口设计准则、统一错误码与三大模块完整接口清单
  6. [docs/06-前端页面与交互设计规范.md](docs/06-前端页面与交互设计规范.md) — 界面布局、交互流程与可视化组件设计规范
  7. [docs/07-Git分支管理与团队协作规范.md](docs/07-Git分支管理与团队协作规范.md) — `main / develop / feature/*` 分支模型、Commit 规范与 AI 代码回退机制
  8. [docs/08-迭代任务拆分与测试验收报告.md](docs/08-迭代任务拆分与测试验收报告.md) — 需求追踪矩阵、Sprint 任务板与后端 pytest 自动化验收报告
  9. [docs/09-演讲配套演示脚本与PPT要点.md](docs/09-演讲配套演示脚本与PPT要点.md) — 演讲稿 6 大章节逐段配套现场演示指引、PPT 结构与答辩 Q&A

---

## 四、目录结构

```text
ICPC/
├── .spec/                       # SDD 规范清单（AI 与团队共享的唯一契约源）
├── docs/                        # 完整软件工程与答辩文档（01 ~ 09）
├── backend/                     # FastAPI + SQLAlchemy + SQLite 后端服务
│   ├── app/
│   │   ├── main.py              # 应用入口、CORS、Swagger配置与自动初始化种子数据
│   │   ├── database.py          # SQLite 连接与会话管理
│   │   ├── models.py            # ORM 数据模型（含题目-知识点多对多关联表）
│   │   ├── schemas.py           # Pydantic 请求/响应契约校验
│   │   ├── seed.py              # 真实高校 ICPC 实验室演示数据初始化
│   │   └── routers/             # 分模块路由：dashboard / association / question_bank / assessment
│   ├── tests/                   # pytest 自动化接口与业务规则测试
│   └── requirements.txt
├── frontend/                    # Vue 3 + Vite 前端应用
│   ├── src/
│   │   ├── api/                 # 统一后端 API 客户端
│   │   ├── components/          # 通用组件（含 SVG 六维能力雷达图等）
│   │   └── views/               # 仪表盘、协会管理、题库管理、个人能力评估、路线图
│   └── package.json
└── scripts/
    └── start-dev.sh             # 一键启动前后端开发环境脚本
```

---

## 五、快速启动

### 方式一：一键脚本启动
```bash
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

### 方式二：分别启动前后端

**1. 启动 FastAPI 后端（默认端口 `8000`）**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- 后端交互式 API 文档（Swagger UI）：`http://127.0.0.1:8000/docs`
- 后端 ReDoc 文档：`http://127.0.0.1:8000/redoc`

**2. 启动 Vue 3 前端（默认端口 `5173`）**
```bash
cd frontend
pnpm install
pnpm dev
```
- 前端访问地址：`http://127.0.0.1:5173`

**3. 运行后端自动化验收测试**
```bash
cd backend
.venv/bin/pytest -v
```
