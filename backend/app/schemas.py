from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==================== 协会管理 Schemas ====================

class ApplicationCreate(BaseModel):
    student_no: str = Field(..., min_length=3, max_length=32)
    name: str = Field(..., min_length=1, max_length=64)
    major: str = Field(default="软件工程", max_length=64)
    grade: str = Field(default="2024级", max_length=32)
    contact: str = Field(default="", max_length=64)
    target_direction: str = Field(default="COMPETITION")
    experience: str = Field(default="")


class ApplicationReview(BaseModel):
    approved: bool
    interview_note: str = Field(default="")
    review_note: str = Field(default="")
    department: str = Field(default="竞赛部")


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_no: str
    name: str
    major: str
    grade: str
    contact: str
    target_direction: str
    experience: str
    status: str
    interview_note: str
    review_note: str
    member_id: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None


class MemberCreate(BaseModel):
    student_no: str = Field(..., min_length=3, max_length=32)
    name: str = Field(..., min_length=1, max_length=64)
    major: str = Field(default="软件工程", max_length=64)
    grade: str = Field(default="2024级", max_length=32)
    contact: str = Field(default="", max_length=64)
    department: str = Field(default="竞赛部", max_length=64)
    stage: str = Field(default="CANDIDATE")
    direction: str = Field(default="UNDECIDED")
    experience: str = Field(default="")


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    contact: Optional[str] = None
    department: Optional[str] = None
    direction: Optional[str] = None
    experience: Optional[str] = None


class MemberPromote(BaseModel):
    direction: str = Field(..., description="COMPETITION 或 NON_COMPETITION")
    department: str = Field(default="竞赛部")
    note: str = Field(default="通过入会考核，正式转正")


class MemberStatusChange(BaseModel):
    status: str = Field(..., description="ACTIVE | OBSERVATION | DISMISSAL_PENDING | DISMISSED | WITHDRAWN")
    reason: str = Field(..., min_length=1)


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_no: str
    name: str
    major: str
    grade: str
    contact: str
    department: str
    stage: str
    direction: str
    status: str
    consecutive_failures: int
    experience: str
    joined_at: datetime


class MemberAssessmentCreate(BaseModel):
    member_id: int
    cycle: str = Field(..., min_length=1, max_length=64)
    score: float = Field(..., ge=0, le=100)
    passed: bool
    metrics: Dict[str, Any] = Field(default_factory=dict)
    comment: str = Field(default="")


class MemberAssessmentOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    student_no: str
    cycle: str
    direction: str
    score: float
    passed: bool
    metrics: Dict[str, Any]
    comment: str
    resulting_status: str
    created_at: datetime


class OrgPositionCreate(BaseModel):
    member_id: int
    department: str
    title: str
    term: str
    is_current: bool = True


class OrgPositionOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    department: str
    title: str
    term: str
    is_current: bool
    created_at: datetime


class RewardCreate(BaseModel):
    member_id: int
    record_type: str
    title: str
    reason: str = ""
    is_public: bool = True


class RewardOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    record_type: str
    title: str
    reason: str
    is_public: bool
    created_at: datetime


# ==================== 题库管理 Schemas ====================

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    category: str = Field(default="KNOWLEDGE")  # KNOWLEDGE | ABILITY
    description: str = Field(default="")


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    description: str
    problem_count: int = 0


class ProblemSolutionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    author_name: str = Field(default="题库组", max_length=64)
    idea: str = Field(..., min_length=1)
    code: str = Field(default="")
    language: str = Field(default="C++17", max_length=32)


class ProblemSolutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    problem_id: int
    title: str
    author_name: str
    idea: str
    code: str
    language: str
    created_at: datetime


class ProblemCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=160)
    statement: str = Field(default="")
    sample_input: str = Field(default="")
    sample_output: str = Field(default="")
    source: str = Field(default="校内题库", max_length=64)
    external_url: str = Field(default="", max_length=255)
    difficulty: str = Field(default="普及")
    status: str = Field(default="ACTIVE")
    tag_ids: List[int] = Field(default_factory=list)


class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    statement: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    source: Optional[str] = None
    external_url: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class ProblemBriefOut(BaseModel):
    id: int
    code: str
    title: str
    source: str
    external_url: str
    difficulty: str
    status: str
    tags: List[TagOut]
    solution_count: int
    created_at: datetime


class ProblemDetailOut(ProblemBriefOut):
    statement: str
    sample_input: str
    sample_output: str
    solutions: List[ProblemSolutionOut]


class ProblemListCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    theme: str = Field(default="专题强化")
    target_stage: str = Field(default="日常训练")
    target_dimension: str = Field(default="")
    description: str = Field(default="")
    problem_ids: List[int] = Field(default_factory=list)


class ProblemListItemOut(BaseModel):
    sort_order: int
    problem_id: int
    code: str
    title: str
    difficulty: str
    source: str


class ProblemListOut(BaseModel):
    id: int
    title: str
    theme: str
    target_stage: str
    target_dimension: str
    description: str
    created_at: datetime
    items: List[ProblemListItemOut]


# ==================== 个人能力评估 Schemas ====================

class AbilityAssessmentCreate(BaseModel):
    member_id: int
    assessment_name: str = Field(..., min_length=1, max_length=128)
    cycle: str = Field(..., min_length=1, max_length=64)
    lang_basic: int = Field(..., ge=0, le=100)
    basic_algo: int = Field(..., ge=0, le=100)
    simulation_logic: int = Field(..., ge=0, le=100)
    boundary_handling: int = Field(..., ge=0, le=100)
    knowledge_combo: int = Field(..., ge=0, le=100)
    coding_debug: int = Field(..., ge=0, le=100)
    summary: str = Field(default="")


class WeakPointOut(BaseModel):
    dimension_key: str
    dimension_label: str
    score: int
    level: str
    suggestion: str


class AbilityAssessmentOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    student_no: str
    assessment_name: str
    cycle: str
    lang_basic: int
    basic_algo: int
    simulation_logic: int
    boundary_handling: int
    knowledge_combo: int
    coding_debug: int
    overall_score: float
    weak_points: List[WeakPointOut]
    summary: str
    created_at: datetime


# ==================== 系统辅助 Schemas ====================

class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    category: str = Field(default="协会事务")
    audience: str = Field(default="全体会员")
    content: str = Field(..., min_length=1)
    publisher: str = Field(default="协会秘书处")


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    audience: str
    content: str
    publisher: str
    created_at: datetime
