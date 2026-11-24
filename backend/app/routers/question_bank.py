from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    OperationLog,
    Problem,
    ProblemList,
    ProblemListItem,
    ProblemSolution,
    Tag,
    problem_tag_rel,
)
from app.schemas import (
    ProblemBriefOut,
    ProblemCreate,
    ProblemDetailOut,
    ProblemListCreate,
    ProblemListItemOut,
    ProblemListOut,
    ProblemSolutionCreate,
    ProblemSolutionOut,
    ProblemUpdate,
    TagCreate,
    TagOut,
)

router = APIRouter(prefix="/api/v1/question-bank", tags=["题库管理 (FR-QB)"])

VALID_DIFFICULTIES = {"入门", "普及", "提高", "省选", "NOI"}
VALID_TAG_CATEGORIES = {"KNOWLEDGE", "ABILITY"}


def _serialize_tag(tag: Tag, count: int = 0) -> TagOut:
    return TagOut(
        id=tag.id,
        name=tag.name,
        category=tag.category,
        description=tag.description,
        problem_count=count,
    )


def _serialize_problem_brief(p: Problem) -> ProblemBriefOut:
    return ProblemBriefOut(
        id=p.id,
        code=p.code,
        title=p.title,
        source=p.source,
        external_url=p.external_url,
        difficulty=p.difficulty,
        status=p.status,
        tags=[_serialize_tag(t) for t in p.tags],
        solution_count=len(p.solutions),
        created_at=p.created_at,
    )


# ==================== 知识点与能力标签管理 (FR-QB-001, BR-006) ====================


@router.get("/tags", response_model=List[TagOut])
def list_tags(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Tag)
    if category:
        q = q.filter(Tag.category == category)
    tags = q.order_by(Tag.category.asc(), Tag.id.asc()).all()

    counts = dict(
        db.query(problem_tag_rel.c.tag_id, func.count(problem_tag_rel.c.problem_id))
        .group_by(problem_tag_rel.c.tag_id)
        .all()
    )
    return [_serialize_tag(t, counts.get(t.id, 0)) for t in tags]


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    if payload.category not in VALID_TAG_CATEGORIES:
        raise HTTPException(status_code=400, detail="标签分类仅支持 KNOWLEDGE（算法知识点）或 ABILITY（实现能力标签）")
    if db.query(Tag).filter(Tag.name == payload.name.strip()).first():
        raise HTTPException(status_code=409, detail=f"标签「{payload.name}」已存在")

    tag = Tag(name=payload.name.strip(), category=payload.category, description=payload.description)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return _serialize_tag(tag, 0)


# ==================== 题目管理与多标签组合检索 (FR-QB-002/003/004, BR-006) ====================


@router.get("/problems", response_model=List[ProblemBriefOut])
def list_problems(
    keyword: Optional[str] = None,
    difficulty: Optional[str] = None,
    source: Optional[str] = None,
    tag_ids: Optional[str] = Query(None, description="逗号分隔的标签ID列表，如 1,3,5"),
    match_mode: str = Query("all", description="多标签组合方式: all(交集) | any(并集)"),
    db: Session = Depends(get_db),
):
    q = db.query(Problem).options(joinedload(Problem.tags), joinedload(Problem.solutions))

    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(or_(Problem.title.ilike(like), Problem.code.ilike(like), Problem.statement.ilike(like)))
    if difficulty:
        q = q.filter(Problem.difficulty == difficulty)
    if source:
        q = q.filter(Problem.source == source)

    if tag_ids:
        try:
            parsed_ids = [int(x.strip()) for x in tag_ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="tag_ids 参数必须为逗号分隔的整数")
        if parsed_ids:
            if match_mode == "any":
                q = q.filter(Problem.tags.any(Tag.id.in_(parsed_ids)))
            else:
                # 交集查询：题目必须同时关联所选的全部知识点/能力标签
                subq = (
                    db.query(problem_tag_rel.c.problem_id)
                    .filter(problem_tag_rel.c.tag_id.in_(parsed_ids))
                    .group_by(problem_tag_rel.c.problem_id)
                    .having(func.count(func.distinct(problem_tag_rel.c.tag_id)) == len(set(parsed_ids)))
                )
                q = q.filter(Problem.id.in_(subq))

    problems = q.order_by(Problem.created_at.desc(), Problem.id.desc()).all()
    return [_serialize_problem_brief(p) for p in problems]


@router.post("/problems", response_model=ProblemDetailOut, status_code=status.HTTP_201_CREATED)
def create_problem(payload: ProblemCreate, db: Session = Depends(get_db)):
    if payload.difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(status_code=400, detail=f"难度等级仅支持：{', '.join(VALID_DIFFICULTIES)}")
    if db.query(Problem).filter(Problem.code == payload.code.strip()).first():
        raise HTTPException(status_code=409, detail=f"题目编号 {payload.code} 已存在")

    tags = []
    if payload.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()
        if len(tags) != len(set(payload.tag_ids)):
            raise HTTPException(status_code=400, detail="包含不存在的知识点/标签 ID")

    problem = Problem(
        code=payload.code.strip(),
        title=payload.title.strip(),
        statement=payload.statement,
        sample_input=payload.sample_input,
        sample_output=payload.sample_output,
        source=payload.source,
        external_url=payload.external_url,
        difficulty=payload.difficulty,
        status=payload.status,
        tags=tags,
    )
    db.add(problem)
    db.add(
        OperationLog(
            module="题库管理",
            action="新增题目",
            target=f"{problem.code} {problem.title}",
            detail=f"难度:{problem.difficulty} 标签数:{len(tags)}",
        )
    )
    db.commit()
    db.refresh(problem)
    return get_problem_detail(problem.id, db)


@router.get("/problems/{problem_id}", response_model=ProblemDetailOut)
def get_problem_detail(problem_id: int, db: Session = Depends(get_db)):
    p = (
        db.query(Problem)
        .options(joinedload(Problem.tags), joinedload(Problem.solutions))
        .filter(Problem.id == problem_id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="题目不存在")
    return ProblemDetailOut(
        id=p.id,
        code=p.code,
        title=p.title,
        statement=p.statement,
        sample_input=p.sample_input,
        sample_output=p.sample_output,
        source=p.source,
        external_url=p.external_url,
        difficulty=p.difficulty,
        status=p.status,
        tags=[_serialize_tag(t) for t in p.tags],
        solution_count=len(p.solutions),
        solutions=[ProblemSolutionOut.model_validate(s) for s in p.solutions],
        created_at=p.created_at,
    )


@router.put("/problems/{problem_id}", response_model=ProblemDetailOut)
def update_problem(problem_id: int, payload: ProblemUpdate, db: Session = Depends(get_db)):
    p = db.query(Problem).filter(Problem.id == problem_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="题目不存在")

    data = payload.model_dump(exclude_unset=True)
    tag_ids = data.pop("tag_ids", None)
    if "difficulty" in data and data["difficulty"] not in VALID_DIFFICULTIES:
        raise HTTPException(status_code=400, detail="非法难度等级")
    for k, v in data.items():
        setattr(p, k, v)
    if tag_ids is not None:
        p.tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()

    db.commit()
    return get_problem_detail(problem_id, db)


@router.delete("/problems/{problem_id}", status_code=status.HTTP_200_OK)
def delete_problem(problem_id: int, db: Session = Depends(get_db)):
    p = db.query(Problem).filter(Problem.id == problem_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="题目不存在")
    code_title = f"{p.code} {p.title}"
    db.delete(p)
    db.add(OperationLog(module="题库管理", action="删除题目", target=code_title, detail="已清理关联标签与题解"))
    db.commit()
    return {"deleted": True, "id": problem_id}


# ==================== 题解管理 (FR-QB-005) ====================


@router.post("/problems/{problem_id}/solutions", response_model=ProblemSolutionOut, status_code=status.HTTP_201_CREATED)
def add_solution(problem_id: int, payload: ProblemSolutionCreate, db: Session = Depends(get_db)):
    p = db.query(Problem).filter(Problem.id == problem_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="题目不存在")
    sol = ProblemSolution(problem_id=problem_id, **payload.model_dump())
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return ProblemSolutionOut.model_validate(sol)


# ==================== 题单管理 (FR-QB-006) ====================


@router.get("/problem-lists", response_model=List[ProblemListOut])
def list_problem_lists(db: Session = Depends(get_db)):
    lists = (
        db.query(ProblemList)
        .options(joinedload(ProblemList.items).joinedload(ProblemListItem.problem))
        .order_by(ProblemList.created_at.desc())
        .all()
    )
    return [
        ProblemListOut(
            id=pl.id,
            title=pl.title,
            theme=pl.theme,
            target_stage=pl.target_stage,
            target_dimension=pl.target_dimension,
            description=pl.description,
            created_at=pl.created_at,
            items=[
                ProblemListItemOut(
                    sort_order=item.sort_order,
                    problem_id=item.problem.id,
                    code=item.problem.code,
                    title=item.problem.title,
                    difficulty=item.problem.difficulty,
                    source=item.problem.source,
                )
                for item in pl.items
                if item.problem is not None
            ],
        )
        for pl in lists
    ]


@router.post("/problem-lists", response_model=ProblemListOut, status_code=status.HTTP_201_CREATED)
def create_problem_list(payload: ProblemListCreate, db: Session = Depends(get_db)):
    pl = ProblemList(
        title=payload.title.strip(),
        theme=payload.theme,
        target_stage=payload.target_stage,
        target_dimension=payload.target_dimension,
        description=payload.description,
    )
    db.add(pl)
    db.flush()

    for idx, pid in enumerate(payload.problem_ids, start=1):
        if db.query(Problem).filter(Problem.id == pid).first():
            db.add(ProblemListItem(problem_list_id=pl.id, problem_id=pid, sort_order=idx))

    db.add(
        OperationLog(
            module="题库管理",
            action="创建专题题单",
            target=pl.title,
            detail=f"主题:{pl.theme} 包含题目数:{len(payload.problem_ids)}",
        )
    )
    db.commit()

    return next(item for item in list_problem_lists(db) if item.id == pl.id)


# ==================== 题库覆盖与统计 (FR-QB-007) ====================


@router.get("/stats")
def question_bank_stats(db: Session = Depends(get_db)):
    total_problems = db.query(func.count(Problem.id)).scalar() or 0
    total_tags = db.query(func.count(Tag.id)).scalar() or 0
    total_lists = db.query(func.count(ProblemList.id)).scalar() or 0
    total_solutions = db.query(func.count(ProblemSolution.id)).scalar() or 0

    difficulty_order = ["入门", "普及", "提高", "省选", "NOI"]
    diff_rows = dict(
        db.query(Problem.difficulty, func.count(Problem.id)).group_by(Problem.difficulty).all()
    )
    difficulty_distribution = [
        {"difficulty": d, "count": diff_rows.get(d, 0)} for d in difficulty_order
    ]

    source_rows = db.query(Problem.source, func.count(Problem.id)).group_by(Problem.source).all()
    source_distribution = [{"source": s, "count": c} for s, c in source_rows]

    tag_counts = dict(
        db.query(problem_tag_rel.c.tag_id, func.count(problem_tag_rel.c.problem_id))
        .group_by(problem_tag_rel.c.tag_id)
        .all()
    )
    tags = db.query(Tag).order_by(Tag.category.asc(), Tag.id.asc()).all()
    tag_coverage = [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "count": tag_counts.get(t.id, 0),
        }
        for t in tags
    ]
    tag_coverage.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_problems": total_problems,
        "total_tags": total_tags,
        "total_lists": total_lists,
        "total_solutions": total_solutions,
        "difficulty_distribution": difficulty_distribution,
        "source_distribution": source_distribution,
        "tag_coverage": tag_coverage,
    }
