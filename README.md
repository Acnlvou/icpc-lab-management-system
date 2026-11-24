# ICPC 实验室管理系统（ICPC Lab Management System）

> **课程项目**：《UML与软件工程建模》｜ **指导教师**：刘卫平 ｜ **开发小组**：Kcat（2024级软件工程）
> **开发范式**：Scrum 敏捷迭代 + SDD 规范驱动开发（Spec-Driven Development）
> **技术栈**：Vue 3 + Vite + FastAPI + SQLAlchemy 2.0 + SQLite 3
> **当前版本**：`v0.5.0-milestone`（整体开发进度 **50%**）

---

## 一、项目简介

本项目面向高校 ICPC 协会与算法竞赛实验室，针对传统管理中依赖聊天工具、电子表格、训练数据分散与能力画像缺失的痛点，构建从 **会员全生命周期管理 → 多标签知识点题库 → 六维个人能力评估 → 日常训练与寒暑假集训 → 组队与校赛/XCPC竞赛管理** 的一体化平台。

本项目严格贯彻 **SDD（规范驱动开发）** 与 **Scrum 敏捷迭代**：先完成需求分析、核心业务规则（`BR-001 ~ BR-010`）、数据库 ER 模型与 API 契约沉淀，再由人机协同按功能分支逐模块实现，并通过自动化接口测试（`pytest`）进行回归验收。

---

## 二、当前开发进度与核心功能（50% 里程碑）

| 模块 | 迭代阶段 | 当前状态 | 覆盖需求编号 | 核心实现亮点 |
| :--- | :---: | :---: | :--- | :--- |
| **SDD 规范与总体架构** | Sprint 0 | ✅ 已完成 | `BR-001 ~ BR-010` | `.spec/` 契约清单 + 9 份完整软件工程与答辩文档 |
| **协会管理中心** | Sprint 1 | ✅ 已完成 | `FR-AM-001 ~ 010` | 申请审核→备选会员→入会考核转正；竞赛/非竞赛双轨考核；单次不合格→观察状态、连续不合格→待清退自动状态机；组织职务与会员方向解耦 |
| **算法题库管理** | Sprint 1-2 | ✅ 已完成 | `FR-QB-001 ~ 007` | 区分「算法知识点」与「实现能力标签」；难度与知识点独立维护；`problem_tag_rel` 多对多关联；支持 **AND 交集 / OR 并集**组合检索、题解与专题题单 |
| **个人能力评估** | Sprint 2 | ✅ 已完成 | `FR-AB-001 ~ 005` | 独立于会员考核、仅面向竞赛会员；六维能力原生 **SVG 双周期对比雷达图**；自动识别 `< 70` 分薄弱项并联动匹配题库补强题单 |
| **系统总览与辅助** | Sprint 2 | ✅ 已完成 | `FR-SYS-001 ~ 003` | 核心 KPI 看板、50% 迭代进度可视化、通知公告发布与全链路审计日志 |
| **训练与集训管理** | Sprint 3 | 🚧 规划中 | `FR-TRN/WIN/SUM-*` | 日常训练计划、任务考勤、寒假基础补强集训、暑假多校集训 |
| **队伍与竞赛管理** | Sprint 4 | 🚧 规划中 | `FR-TEAM/CMP/NC/XCPC-*` | 能力互补辅助组队、校赛线上初赛与候补确认、非 XCPC 与 XCPC 正赛档案 |

---

## 三、技术架构

```text
[浏览器 Vue 3 + Vite (5173)]
        │  HTTP / JSON (/api/v1/*, Vite Dev Proxy)
        ▼
[FastAPI 应用层 (8000) + Pydantic v2 契约校验 + 自动 Swagger UI]
        │  SQLAlchemy 2.0 ORM
        ▼
[SQLite 3 单文件关系型数据库 (backend/icpc_lab.db，13 张核心表，含 N:M 关联表)]
```

---

## 四、团队分工（Kcat 小组）

| 角色 | 姓名 | 学号 | 需求与文档阶段 | 系统研发阶段 |
| :---: | :---: | :---: | :--- | :--- |
| 组长 | 李靖宇 | 202421091067 | 需求分析、文档编写 | 需求与架构设计、SDD 规范制定、后端核心框架 |
| 组员 | 尚思彤 | 202421091189 | 流程图绘制 | 前端开发（Vue 3 业务视图、状态流转交互、SVG 雷达图） |
| 组员 | 莫 姝 | 202421091198 | 文档封面制作 | 后端业务模块开发（题库多对多模型、能力评估与看板接口） |
| 组员 | 覃爽爽 | 202421091165 | 文档格式整理 | 功能测试、`pytest` 自动化验收用例、Git 分支与文档维护 |

---

## 五、环境要求与快速启动（VS Code 指南）

### 5.1 环境要求
- **Python**：`3.9+`
- **Node.js**：`18+`（附带 `npm`）
- **Git**：`2.30+`

### 5.2 在 VS Code 中一键启动（macOS / Linux 推荐）

1. 使用 VS Code 打开项目根目录 `ICPC/`。
2. 按快捷键 `` Ctrl + ` ``（或点击顶部菜单 **终端 → 新建终端**）。
3. 执行一键启动脚本（首次运行会自动安装缺失依赖，已安装则直接秒启）：
   ```bash
   ./scripts/start-dev.sh
   ```
4. 浏览器打开以下地址即可体验：
   - **前端管理界面**：http://127.0.0.1:5173
   - **后端 Swagger 交互式 API 文档**：http://127.0.0.1:8000/docs
   - **后端 ReDoc 文档**：http://127.0.0.1:8000/redoc
5. 在终端按 `Ctrl + C` 即可同时停止前后端服务。

### 5.3 在 VS Code 中分终端手动启动（macOS / Linux / Windows 通用）

适合需要同时查看前后端控制台日志、或演示前后端分离架构时使用：

**终端 1：启动 FastAPI 后端（端口 `8000`）**

*macOS / Linux：*
```bash
cd backend
# 若尚未创建虚拟环境，先执行以下两行（推荐加清华源加速）：
# python3 -m venv .venv
# .venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Windows (PowerShell)：*
```powershell
cd backend
# 首次运行需建虚拟环境：
# python -m venv .venv
# .\.venv\Scripts\pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**终端 2：启动 Vue 3 前端（端口 `5173`）**

点击 VS Code 终端右上角 **`+`** 新建第二个终端：
```bash
cd frontend
# 若尚未安装依赖，先执行：npm install
npm run dev
```

---

## 六、测试验证、Git 展示与演示数据重置

### 6.1 运行后端自动化验收测试（验证 `BR-001 ~ BR-007`）
```bash
cd backend
PYTHONPATH=. .venv/bin/pytest -v
```
> 预期结果：`7 passed`，自动使用独立临时 SQLite 测试库，不会污染演示数据。

### 6.2 前端生产构建检查
```bash
npm --prefix frontend run build
```

### 6.3 查看 Git 多分支开发演进图（`main / develop / feature/*`）
```bash
git log --graph --oneline --decorate --all
```

### 6.4 重置干净的初始演示数据
系统首次启动时会自动通过 `backend/app/seed.py` 写入 8 名不同阶段/状态会员、12 个算法与能力标签、10 道多标签题目、题解、4 套专题题单及 7 份多周期能力评估记录。若演示演练后希望一键还原初始状态：
```bash
rm -f backend/icpc_lab.db
```
然后重新启动后端即可自动重建并灌入全新初始数据。

---

## 七、规范与工程文档索引

- **SDD 规范契约（`.spec/`）**
  - [.spec/project.spec.yaml](.spec/project.spec.yaml) — 项目范围、迭代计划与技术规范
  - [.spec/rules.spec.md](.spec/rules.spec.md) — AI 辅助开发业务红线（`BR-001 ~ BR-010`）
  - [.spec/api.spec.yaml](.spec/api.spec.yaml) — RESTful API 接口契约
- **全套软件工程与汇报文档（`docs/`）**
  1. [docs/01-需求分析文档.md](docs/01-需求分析文档.md)
  2. [docs/02-SDD规范驱动开发与AI协作流程.md](docs/02-SDD规范驱动开发与AI协作流程.md)
  3. [docs/03-系统架构与详细设计文档.md](docs/03-系统架构与详细设计文档.md)
  4. [docs/04-数据库设计规范.md](docs/04-数据库设计规范.md)
  5. [docs/05-API接口规范.md](docs/05-API接口规范.md)
  6. [docs/06-前端页面与交互设计规范.md](docs/06-前端页面与交互设计规范.md)
  7. [docs/07-Git分支管理与团队协作规范.md](docs/07-Git分支管理与团队协作规范.md)
  8. [docs/08-迭代任务拆分与测试验收报告.md](docs/08-迭代任务拆分与测试验收报告.md)
  9. [docs/09-演讲配套演示脚本与PPT要点.md](docs/09-演讲配套演示脚本与PPT要点.md)

---

## 八、目录结构

```text
ICPC/
├── .spec/                       # SDD 规范清单（AI 与团队共享的唯一契约源）
├── docs/                        # 完整软件工程与答辩配套文档（01 ~ 09）
├── backend/                     # FastAPI + SQLAlchemy + SQLite 后端
│   ├── app/
│   │   ├── main.py              # 应用入口、CORS、Swagger 与生命周期初始化
│   │   ├── database.py          # SQLite 连接与外键约束配置
│   │   ├── models.py            # 13 张业务表 ORM 定义（含多对多中间表）
│   │   ├── schemas.py           # Pydantic v2 请求/响应契约校验
│   │   ├── seed.py              # 演示数据幂等初始化脚本
│   │   └── routers/             # dashboard / association / question_bank / assessment
│   ├── tests/test_api.py        # pytest 自动化接口与业务规则测试集
│   └── requirements.txt
├── frontend/                    # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── api/client.js        # 统一 REST API 客户端
│   │   ├── components/          # 原生 SVG 六维能力雷达图组件
│   │   └── views/               # 总览、协会管理、题库管理、个人能力评估、路线图
│   ├── vite.config.js           # /api 反向代理至 FastAPI (8000)
│   └── package.json
└── scripts/
    └── start-dev.sh             # 一键启动前后端开发环境脚本
```

---

## 九、常见问题排查（FAQ）

1. **前端页面打不开数据 / 接口报网络错误**：确认后端 `uvicorn` 已在 `127.0.0.1:8000` 正常运行，可先打开 http://127.0.0.1:8000/api/health 验证返回 `{"status":"ok",...}`。
2. **端口被占用**：若 `8000` 或 `5173` 被占用，可先关闭旧终端进程（`Ctrl + C`），或在启动命令中通过 `--port` 指定新端口。
3. **`pip install` 下载超时**：请使用上方文档中的清华镜像源参数 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。
