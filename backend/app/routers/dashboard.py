
from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AbilityAssessment,
    Announcement,
    Member,
    MembershipApplication,
    OperationLog,
    Problem,
    ProblemList,
    Tag,
)
from app.schemas import AnnouncementCreate, AnnouncementOut

# Sprint 3/4 新增表（训练/集训、队伍/竞赛）由 feature/training-camp 与 feature/team-contest 分支合入。
# 此处做防御式导入：后端合入前计数为 0，合入后自动生效，保证 Dashboard 在 v0.5.0 与 v1.0.0 均可启动。
try:
    from app.models import (  # noqa: F401
        NonXcpcResult,
        SchoolContest,
        Team,
        TrainingCamp,
        TrainingPlan,
        TrainingTask,
        XcpcResult,
    )

    _SPRINT34_MODELS_READY = True
except ImportError:  # pragma: no cover - 过渡期兼容
    NonXcpcResult = SchoolContest = Team = TrainingCamp = TrainingPlan = TrainingTask = XcpcResult = None
    _SPRINT34_MODELS_READY = False

router = APIRouter(prefix="/api/v1/dashboard", tags=["系统总览与辅助 (FR-SYS)"])


@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    total_members = db.query(func.count(Member.id)).scalar() or 0
    formal_members = db.query(func.count(Member.id)).filter(Member.stage == "FORMAL").scalar() or 0
    candidate_members = db.query(func.count(Member.id)).filter(Member.stage == "CANDIDATE").scalar() or 0
    competition_members = (
        db.query(func.count(Member.id))
        .filter(Member.stage == "FORMAL", Member.direction == "COMPETITION")
        .scalar()
        or 0
    )
    non_competition_members = (
        db.query(func.count(Member.id))
        .filter(Member.stage == "FORMAL", Member.direction == "NON_COMPETITION")
        .scalar()
        or 0
    )
    observation_members = db.query(func.count(Member.id)).filter(Member.status == "OBSERVATION").scalar() or 0
    dismissal_pending = (
        db.query(func.count(Member.id)).filter(Member.status == "DISMISSAL_PENDING").scalar() or 0
    )
    pending_applications = (
        db.query(func.count(MembershipApplication.id))
        .filter(MembershipApplication.status == "PENDING")
        .scalar()
        or 0
    )

    total_problems = db.query(func.count(Problem.id)).scalar() or 0
    total_tags = db.query(func.count(Tag.id)).scalar() or 0
    total_lists = db.query(func.count(ProblemList.id)).scalar() or 0
    total_ability_assessments = db.query(func.count(AbilityAssessment.id)).scalar() or 0

    if _SPRINT34_MODELS_READY:
        total_training_plans = db.query(func.count(TrainingPlan.id)).scalar() or 0
        total_training_tasks = db.query(func.count(TrainingTask.id)).scalar() or 0
        total_training_camps = db.query(func.count(TrainingCamp.id)).scalar() or 0
        total_teams = db.query(func.count(Team.id)).scalar() or 0
        total_school_contests = db.query(func.count(SchoolContest.id)).scalar() or 0
        total_xcpc = db.query(func.count(XcpcResult.id)).scalar() or 0
        total_non_xcpc = db.query(func.count(NonXcpcResult.id)).scalar() or 0
    else:
        total_training_plans = total_training_tasks = total_training_camps = 0
        total_teams = total_school_contests = total_xcpc = total_non_xcpc = 0

    diff_order = ["入门", "普及", "提高", "省选", "NOI"]
    diff_map = dict(db.query(Problem.difficulty, func.count(Problem.id)).group_by(Problem.difficulty).all())
    difficulty_distribution = [{"difficulty": d, "count": diff_map.get(d, 0)} for d in diff_order]

    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(6).all()
    logs = db.query(OperationLog).order_by(OperationLog.created_at.desc()).limit(8).all()

    return {
        "progress": {
            "overall_percent": 100,
            "milestone": "v1.0.0",
            "modules": [
                {"name": "SDD 规范与架构建基", "sprint": "Sprint 0", "percent": 100, "status": "已完成"},
                {"name": "协会管理模块", "sprint": "Sprint 1", "percent": 100, "status": "已完成"},
                {"name": "题库与知识点标签管理", "sprint": "Sprint 1-2", "percent": 100, "status": "已完成"},
                {"name": "个人能力评估与画像", "sprint": "Sprint 2", "percent": 100, "status": "已完成"},
                {"name": "训练与寒暑假集训管理", "sprint": "Sprint 3", "percent": 100, "status": "已完成"},
                {"name": "队伍与校赛/XCPC竞赛管理", "sprint": "Sprint 4", "percent": 100, "status": "已完成"},
            ],
        },
        "kpi": {
            "total_members": total_members,
            "formal_members": formal_members,
            "candidate_members": candidate_members,
            "competition_members": competition_members,
            "non_competition_members": non_competition_members,
            "observation_members": observation_members,
            "dismissal_pending": dismissal_pending,
            "pending_applications": pending_applications,
            "total_problems": total_problems,
            "total_tags": total_tags,
            "total_lists": total_lists,
            "total_ability_assessments": total_ability_assessments,
            "total_training_plans": total_training_plans,
            "total_training_tasks": total_training_tasks,
            "total_training_camps": total_training_camps,
            "total_teams": total_teams,
            "total_school_contests": total_school_contests,
            "total_xcpc": total_xcpc,
            "total_non_xcpc": total_non_xcpc,
        },
        "difficulty_distribution": difficulty_distribution,
        "announcements": [AnnouncementOut.model_validate(a).model_dump() for a in announcements],
        "recent_logs": [
            {
                "id": lg.id,
                "module": lg.module,
                "action": lg.action,
                "target": lg.target,
                "detail": lg.detail,
                "operator": lg.operator,
                "created_at": lg.created_at,
            }
            for lg in logs
        ],
    }


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()


@router.post("/announcements", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db)):
    ann = Announcement(**payload.model_dump())
    db.add(ann)
    db.add(
        OperationLog(
            module="通知公告",
            action="发布公告",
            target=ann.title,
            detail=f"面向对象:{ann.audience} 分类:{ann.category}",
            operator=ann.publisher,
        )
    )
    db.commit()
    db.refresh(ann)
    return ann
