import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    AbilityAssessment,
    Member,
    MemberAssessment,
    MembershipApplication,
    OperationLog,
    OrgPosition,
    RewardPunishment,
)
from app.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationReview,
    MemberAssessmentCreate,
    MemberAssessmentOut,
    MemberCreate,
    MemberOut,
    MemberPromote,
    MemberStatusChange,
    MemberUpdate,
    OrgPositionCreate,
    OrgPositionOut,
    RewardCreate,
    RewardOut,
)

router = APIRouter(prefix="/api/v1/association", tags=["协会管理 (FR-AM)"])

VALID_DIRECTIONS = {"COMPETITION", "NON_COMPETITION"}
VALID_STATUSES = {"ACTIVE", "OBSERVATION", "DISMISSAL_PENDING", "DISMISSED", "WITHDRAWN"}


def _log(db: Session, action: str, target: str, detail: str):
    db.add(
        OperationLog(
            module="协会管理",
            action=action,
            target=target,
            detail=detail,
            operator="协会工作人员",
        )
    )


# ==================== 入会申请与资格审核 (FR-AM-001, FR-AM-002, BR-001) ====================


@router.get("/applications", response_model=list[ApplicationOut])
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    q = db.query(MembershipApplication)
    if status_filter:
        q = q.filter(MembershipApplication.status == status_filter)
    return q.order_by(MembershipApplication.created_at.desc()).all()


@router.post("/applications", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    if payload.target_direction not in VALID_DIRECTIONS:
        raise HTTPException(status_code=400, detail="意向方向仅支持 COMPETITION 或 NON_COMPETITION")
    existing_member = db.query(Member).filter(Member.student_no == payload.student_no).first()
    if existing_member:
        raise HTTPException(status_code=409, detail=f"学号 {payload.student_no} 已在会员档案中")

    app_obj = MembershipApplication(**payload.model_dump())
    db.add(app_obj)
    _log(db, "提交入会申请", f"{payload.name}({payload.student_no})", f"意向方向：{payload.target_direction}")
    db.commit()
    db.refresh(app_obj)
    return app_obj


@router.post("/applications/{app_id}/review", response_model=ApplicationOut)
def review_application(app_id: int, payload: ApplicationReview, db: Session = Depends(get_db)):
    app_obj = db.query(MembershipApplication).filter(MembershipApplication.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="入会申请记录不存在")
    if app_obj.status != "PENDING":
        raise HTTPException(status_code=400, detail="该申请已完成审核，无法重复处理")

    app_obj.interview_note = payload.interview_note
    app_obj.review_note = payload.review_note
    app_obj.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if payload.approved:
        app_obj.status = "APPROVED"
        # BR-001: 审核通过后进入备选会员阶段，通过入会考核后方成为正式会员
        member = db.query(Member).filter(Member.student_no == app_obj.student_no).first()
        if not member:
            member = Member(
                student_no=app_obj.student_no,
                name=app_obj.name,
                major=app_obj.major,
                grade=app_obj.grade,
                contact=app_obj.contact,
                department=payload.department,
                stage="CANDIDATE",
                direction=app_obj.target_direction,
                status="ACTIVE",
                experience=app_obj.experience,
            )
            db.add(member)
            db.flush()
        app_obj.member_id = member.id
        _log(
            db,
            "审核通过转入备选",
            f"{app_obj.name}({app_obj.student_no})",
            f"BR-001: 资格审核与面试通过，进入备选会员阶段。备注：{payload.review_note}",
        )
    else:
        app_obj.status = "REJECTED"
        _log(db, "驳回入会申请", f"{app_obj.name}({app_obj.student_no})", payload.review_note or "未通过资格审核")

    db.commit()
    db.refresh(app_obj)
    return app_obj


# ==================== 会员档案与生命周期流转 (FR-AM-003, FR-AM-004, FR-AM-007, FR-AM-010) ====================


@router.get("/members", response_model=list[MemberOut])
def list_members(
    keyword: Optional[str] = None,
    stage: Optional[str] = None,
    direction: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Member)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(or_(Member.name.ilike(like), Member.student_no.ilike(like), Member.major.ilike(like)))
    if stage:
        q = q.filter(Member.stage == stage)
    if direction:
        q = q.filter(Member.direction == direction)
    if status_filter:
        q = q.filter(Member.status == status_filter)
    if department:
        q = q.filter(Member.department == department)
    return q.order_by(Member.joined_at.desc(), Member.id.desc()).all()


@router.post("/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    if db.query(Member).filter(Member.student_no == payload.student_no).first():
        raise HTTPException(status_code=409, detail=f"学号 {payload.student_no} 已存在")
    member = Member(**payload.model_dump())
    db.add(member)
    _log(db, "新增会员档案", f"{payload.name}({payload.student_no})", f"阶段:{payload.stage} 方向:{payload.direction}")
    db.commit()
    db.refresh(member)
    return member


@router.get("/members/{member_id}")
def get_member_profile(member_id: int, db: Session = Depends(get_db)):
    """FR-AM-010: 汇总会员基本信息、考核、任职、奖惩和能力评估历史"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    assessments = (
        db.query(MemberAssessment)
        .filter(MemberAssessment.member_id == member_id)
        .order_by(MemberAssessment.created_at.desc())
        .all()
    )
    positions = (
        db.query(OrgPosition)
        .filter(OrgPosition.member_id == member_id)
        .order_by(OrgPosition.is_current.desc(), OrgPosition.created_at.desc())
        .all()
    )
    rewards = (
        db.query(RewardPunishment)
        .filter(RewardPunishment.member_id == member_id)
        .order_by(RewardPunishment.created_at.desc())
        .all()
    )
    ability_records = (
        db.query(AbilityAssessment)
        .filter(AbilityAssessment.member_id == member_id)
        .order_by(AbilityAssessment.created_at.desc())
        .all()
    )

    return {
        "member": MemberOut.model_validate(member).model_dump(),
        "assessments": [
            {
                "id": a.id,
                "cycle": a.cycle,
                "direction": a.direction,
                "score": a.score,
                "passed": a.passed,
                "metrics": json.loads(a.metrics_json or "{}"),
                "comment": a.comment,
                "resulting_status": a.resulting_status,
                "created_at": a.created_at,
            }
            for a in assessments
        ],
        "positions": [
            {
                "id": p.id,
                "department": p.department,
                "title": p.title,
                "term": p.term,
                "is_current": p.is_current,
                "created_at": p.created_at,
            }
            for p in positions
        ],
        "rewards": [
            {
                "id": r.id,
                "record_type": r.record_type,
                "title": r.title,
                "reason": r.reason,
                "is_public": r.is_public,
                "created_at": r.created_at,
            }
            for r in rewards
        ],
        "ability_summary": [
            {
                "id": ab.id,
                "assessment_name": ab.assessment_name,
                "cycle": ab.cycle,
                "overall_score": ab.overall_score,
                "weak_points": json.loads(ab.weak_points_json or "[]"),
                "created_at": ab.created_at,
            }
            for ab in ability_records
        ],
    }


@router.put("/members/{member_id}", response_model=MemberOut)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(member, k, v)
    _log(db, "更新会员信息", f"{member.name}({member.student_no})", "更新基础档案字段")
    db.commit()
    db.refresh(member)
    return member


@router.post("/members/{member_id}/promote", response_model=MemberOut)
def promote_candidate(member_id: int, payload: MemberPromote, db: Session = Depends(get_db)):
    """FR-AM-003, BR-001/002: 备选会员通过入会考核转正为正式会员，并确定职责方向"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    if member.stage != "CANDIDATE":
        raise HTTPException(status_code=400, detail="仅备选会员可执行入会考核转正流程")
    if payload.direction not in VALID_DIRECTIONS:
        raise HTTPException(status_code=400, detail="正式会员必须明确方向：COMPETITION 或 NON_COMPETITION")

    member.stage = "FORMAL"
    member.direction = payload.direction
    member.department = payload.department
    member.status = "ACTIVE"
    _log(
        db,
        "备选会员转正",
        f"{member.name}({member.student_no})",
        f"入会考核通过，成为正式会员（方向：{payload.direction}）。{payload.note}",
    )
    db.commit()
    db.refresh(member)
    return member


@router.post("/members/{member_id}/status", response_model=MemberOut)
def change_member_status(member_id: int, payload: MemberStatusChange, db: Session = Depends(get_db)):
    """FR-AM-007: 观察、清退确认或主动退会状态流转"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="非法状态值")

    old_status = member.status
    member.status = payload.status
    if payload.status in {"DISMISSED", "WITHDRAWN"}:
        member.stage = "EXITED"
    elif payload.status == "ACTIVE":
        member.consecutive_failures = 0

    _log(
        db,
        "变更会员状态",
        f"{member.name}({member.student_no})",
        f"{old_status} -> {payload.status}，原因：{payload.reason}",
    )
    db.commit()
    db.refresh(member)
    return member


# ==================== 周期会员考核与自动状态机 (FR-AM-005/006/007, BR-002/003/004) ====================


@router.get("/assessments", response_model=list[MemberAssessmentOut])
def list_member_assessments(
    member_id: Optional[int] = None,
    direction: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(MemberAssessment).join(Member)
    if member_id:
        q = q.filter(MemberAssessment.member_id == member_id)
    if direction:
        q = q.filter(MemberAssessment.direction == direction)
    rows = q.order_by(MemberAssessment.created_at.desc()).all()
    return [
        MemberAssessmentOut(
            id=r.id,
            member_id=r.member_id,
            member_name=r.member.name,
            student_no=r.member.student_no,
            cycle=r.cycle,
            direction=r.direction,
            score=r.score,
            passed=r.passed,
            metrics=json.loads(r.metrics_json or "{}"),
            comment=r.comment,
            resulting_status=r.resulting_status,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/assessments", response_model=MemberAssessmentOut, status_code=status.HTTP_201_CREATED)
def create_member_assessment(payload: MemberAssessmentCreate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    if member.stage != "FORMAL":
        raise HTTPException(status_code=400, detail="周期会员考核仅面向正式会员，备选会员请走入会考核转正流程")

    # BR-003 状态机自动流转
    if payload.passed:
        member.consecutive_failures = 0
        if member.status == "OBSERVATION":
            member.status = "ACTIVE"
        flow_note = "周期考核合格，保持/恢复正常状态"
    else:
        member.consecutive_failures += 1
        if member.consecutive_failures >= 2:
            member.status = "DISMISSAL_PENDING"
            flow_note = f"连续第 {member.consecutive_failures} 次考核不合格，自动触发【待清退】流程 (BR-003)"
        else:
            member.status = "OBSERVATION"
            flow_note = "周期考核不合格，自动流转至【观察状态】 (BR-003)"

    record = MemberAssessment(
        member_id=member.id,
        cycle=payload.cycle,
        direction=member.direction,
        score=payload.score,
        passed=payload.passed,
        metrics_json=json.dumps(payload.metrics, ensure_ascii=False),
        comment=payload.comment,
        resulting_status=member.status,
    )
    db.add(record)
    _log(
        db,
        "录入周期考核",
        f"{member.name}({member.student_no})",
        f"[{payload.cycle}] 得分:{payload.score} 合格:{payload.passed} -> {flow_note}",
    )
    db.commit()
    db.refresh(record)

    return MemberAssessmentOut(
        id=record.id,
        member_id=member.id,
        member_name=member.name,
        student_no=member.student_no,
        cycle=record.cycle,
        direction=record.direction,
        score=record.score,
        passed=record.passed,
        metrics=payload.metrics,
        comment=record.comment,
        resulting_status=record.resulting_status,
        created_at=record.created_at,
    )


# ==================== 组织任职与奖惩评优 (FR-AM-008, FR-AM-009) ====================


@router.get("/positions", response_model=list[OrgPositionOut])
def list_positions(db: Session = Depends(get_db)):
    rows = (
        db.query(OrgPosition)
        .join(Member)
        .order_by(OrgPosition.is_current.desc(), OrgPosition.created_at.desc())
        .all()
    )
    return [
        OrgPositionOut(
            id=p.id,
            member_id=p.member_id,
            member_name=p.member.name,
            department=p.department,
            title=p.title,
            term=p.term,
            is_current=p.is_current,
            created_at=p.created_at,
        )
        for p in rows
    ]


@router.post("/positions", response_model=OrgPositionOut, status_code=status.HTTP_201_CREATED)
def create_position(payload: OrgPositionCreate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    pos = OrgPosition(**payload.model_dump())
    db.add(pos)
    _log(db, "新增任职履历", f"{member.name}", f"{payload.department}-{payload.title} ({payload.term})")
    db.commit()
    db.refresh(pos)
    return OrgPositionOut(
        id=pos.id,
        member_id=pos.member_id,
        member_name=member.name,
        department=pos.department,
        title=pos.title,
        term=pos.term,
        is_current=pos.is_current,
        created_at=pos.created_at,
    )


@router.get("/rewards", response_model=list[RewardOut])
def list_rewards(db: Session = Depends(get_db)):
    rows = db.query(RewardPunishment).join(Member).order_by(RewardPunishment.created_at.desc()).all()
    return [
        RewardOut(
            id=r.id,
            member_id=r.member_id,
            member_name=r.member.name,
            record_type=r.record_type,
            title=r.title,
            reason=r.reason,
            is_public=r.is_public,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/rewards", response_model=RewardOut, status_code=status.HTTP_201_CREATED)
def create_reward(payload: RewardCreate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    rec = RewardPunishment(**payload.model_dump())
    db.add(rec)
    _log(db, "登记奖惩评优", f"{member.name}", f"[{payload.record_type}] {payload.title}")
    db.commit()
    db.refresh(rec)
    return RewardOut(
        id=rec.id,
        member_id=rec.member_id,
        member_name=member.name,
        record_type=rec.record_type,
        title=rec.title,
        reason=rec.reason,
        is_public=rec.is_public,
        created_at=rec.created_at,
    )
