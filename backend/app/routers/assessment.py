import json
from typing import Dict, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    AbilityAssessment,
    Member,
    OperationLog,
    ProblemList,
    ProblemListItem,
)
from app.schemas import AbilityAssessmentCreate, AbilityAssessmentOut, WeakPointOut

router = APIRouter(prefix="/api/v1/ability", tags=["个人能力评估 (FR-AB)"])

DIMENSIONS: List[Tuple[str, str, str]] = [
    ("lang_basic", "编程语言基础", "巩固 C++ STL 容器、指针引用与复杂度估算，减少基础语法失误"),
    ("basic_algo", "基础算法", "强化二分、贪心、前缀和、基础图论与经典 DP 模板题训练"),
    ("simulation_logic", "模拟与逻辑实现", "开展大模拟与状态机专项训练，养成先写状态流转再编码习惯"),
    ("boundary_handling", "边界处理", "重点练习极值、空集、溢出（long long）与对拍造数据排查习惯"),
    ("knowledge_combo", "知识点组合应用", "加强多知识点综合题（如二分+图论、数据结构优化DP）专题拆解"),
    ("coding_debug", "代码实现与调试", "强化限时盲敲与对拍调试训练，压缩定位 Bug 耗时"),
]

WEAK_THRESHOLD = 70


def analyze_weak_points(scores: Dict[str, int]) -> List[dict]:
    weak_list = []
    for key, label, suggestion in DIMENSIONS:
        val = scores[key]
        if val < WEAK_THRESHOLD:
            level = "高优先补强" if val < 60 else "重点提升"
            weak_list.append(
                {
                    "dimension_key": key,
                    "dimension_label": label,
                    "score": val,
                    "level": level,
                    "suggestion": suggestion,
                }
            )
    if not weak_list:
        # 全部达标时选取最低的 1 项作为进阶优化方向
        lowest_key, lowest_label, suggestion = min(DIMENSIONS, key=lambda d: scores[d[0]])
        weak_list.append(
            {
                "dimension_key": lowest_key,
                "dimension_label": lowest_label,
                "score": scores[lowest_key],
                "level": "进阶拔高",
                "suggestion": f"各项基础均衡，建议围绕「{lowest_label}」冲击高难综合题：{suggestion}",
            }
        )
    weak_list.sort(key=lambda x: x["score"])
    return weak_list


def _serialize_assessment(rec: AbilityAssessment) -> AbilityAssessmentOut:
    raw_weak = json.loads(rec.weak_points_json or "[]")
    return AbilityAssessmentOut(
        id=rec.id,
        member_id=rec.member_id,
        member_name=rec.member.name,
        student_no=rec.member.student_no,
        assessment_name=rec.assessment_name,
        cycle=rec.cycle,
        lang_basic=rec.lang_basic,
        basic_algo=rec.basic_algo,
        simulation_logic=rec.simulation_logic,
        boundary_handling=rec.boundary_handling,
        knowledge_combo=rec.knowledge_combo,
        coding_debug=rec.coding_debug,
        overall_score=rec.overall_score,
        weak_points=[WeakPointOut(**w) for w in raw_weak],
        summary=rec.summary,
        created_at=rec.created_at,
    )


@router.get("/assessments", response_model=List[AbilityAssessmentOut])
def list_ability_assessments(member_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(AbilityAssessment).join(Member)
    if member_id:
        q = q.filter(AbilityAssessment.member_id == member_id)
    rows = q.order_by(AbilityAssessment.created_at.desc(), AbilityAssessment.id.desc()).all()
    return [_serialize_assessment(r) for r in rows]


@router.post("/assessments", response_model=AbilityAssessmentOut, status_code=status.HTTP_201_CREATED)
def create_ability_assessment(payload: AbilityAssessmentCreate, db: Session = Depends(get_db)):
    """FR-AB-001..004, BR-005: 个人能力评估独立于会员考核，仅面向竞赛方向成员"""
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")
    if member.direction != "COMPETITION":
        raise HTTPException(
            status_code=400,
            detail="BR-005: 个人能力评估仅面向竞赛方向会员（非竞赛会员请使用协会管理中的非竞赛周期考核）",
        )

    scores = {
        "lang_basic": payload.lang_basic,
        "basic_algo": payload.basic_algo,
        "simulation_logic": payload.simulation_logic,
        "boundary_handling": payload.boundary_handling,
        "knowledge_combo": payload.knowledge_combo,
        "coding_debug": payload.coding_debug,
    }
    overall = round(sum(scores.values()) / len(scores), 1)
    weak_points = analyze_weak_points(scores)

    rec = AbilityAssessment(
        member_id=member.id,
        assessment_name=payload.assessment_name.strip(),
        cycle=payload.cycle.strip(),
        lang_basic=payload.lang_basic,
        basic_algo=payload.basic_algo,
        simulation_logic=payload.simulation_logic,
        boundary_handling=payload.boundary_handling,
        knowledge_combo=payload.knowledge_combo,
        coding_debug=payload.coding_debug,
        overall_score=overall,
        weak_points_json=json.dumps(weak_points, ensure_ascii=False),
        summary=payload.summary,
    )
    db.add(rec)
    weak_names = "、".join([w["dimension_label"] for w in weak_points])
    db.add(
        OperationLog(
            module="个人能力评估",
            action="生成能力画像",
            target=f"{member.name}({member.student_no})",
            detail=f"[{payload.cycle}] 综合分:{overall} 薄弱项:{weak_names}",
        )
    )
    db.commit()
    db.refresh(rec)
    return _serialize_assessment(rec)


@router.get("/members/{member_id}/profile")
def get_member_ability_profile(member_id: int, db: Session = Depends(get_db)):
    """FR-AB-003..005, BR-007: 返回六维能力画像、薄弱项、历次评估对比与智能推荐补强题单"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    history = (
        db.query(AbilityAssessment)
        .filter(AbilityAssessment.member_id == member_id)
        .order_by(AbilityAssessment.created_at.desc(), AbilityAssessment.id.desc())
        .all()
    )
    serialized_history = [_serialize_assessment(r).model_dump() for r in history]

    latest = serialized_history[0] if serialized_history else None
    previous = serialized_history[1] if len(serialized_history) > 1 else None

    recommended_lists = []
    if latest:
        weak_keys = [w["dimension_key"] for w in latest["weak_points"]]
        pl_rows = (
            db.query(ProblemList)
            .options(joinedload(ProblemList.items).joinedload(ProblemListItem.problem))
            .filter(ProblemList.target_dimension.in_(weak_keys))
            .all()
        )
        for pl in pl_rows:
            recommended_lists.append(
                {
                    "id": pl.id,
                    "title": pl.title,
                    "theme": pl.theme,
                    "target_dimension": pl.target_dimension,
                    "description": pl.description,
                    "problem_count": len(pl.items),
                    "problems": [
                        {
                            "code": it.problem.code,
                            "title": it.problem.title,
                            "difficulty": it.problem.difficulty,
                        }
                        for it in pl.items
                        if it.problem is not None
                    ],
                }
            )

    return {
        "member": {
            "id": member.id,
            "student_no": member.student_no,
            "name": member.name,
            "major": member.major,
            "grade": member.grade,
            "department": member.department,
            "stage": member.stage,
            "direction": member.direction,
            "status": member.status,
        },
        "dimensions_meta": [
            {"key": k, "label": lbl, "suggestion": sug} for k, lbl, sug in DIMENSIONS
        ],
        "latest": latest,
        "previous": previous,
        "history": serialized_history,
        "recommended_lists": recommended_lists,
    }
