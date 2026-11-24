from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import assessment, association, dashboard, question_bank
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="ICPC 实验室管理系统 API",
    description=(
        "Kcat 小组《UML与软件工程建模》课程项目后端服务。\n\n"
        "采用 **Scrum + SDD（规范驱动开发）** 构建，当前里程碑 `v0.5.0-milestone`（进度 50%）已完整实现：\n"
        "- **协会管理（FR-AM-001 ~ 010）**：入会审核、备选转正、双轨周期考核与 BR-003 状态自动流转\n"
        "- **题库管理（FR-QB-001 ~ 007）**：知识点/能力标签多对多关联、AND/OR 组合检索、题单与题解\n"
        "- **个人能力评估（FR-AB-001 ~ 005）**：六维能力画像、薄弱项自动识别与补强题单联动"
    ),
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(association.router)
app.include_router(question_bank.router)
app.include_router(assessment.router)


@app.get("/api/health", tags=["系统健康检查"])
def health_check():
    return {
        "status": "ok",
        "project": "ICPC实验室管理系统",
        "team": "Kcat",
        "version": "0.5.0-milestone",
        "progress": "50%",
    }
