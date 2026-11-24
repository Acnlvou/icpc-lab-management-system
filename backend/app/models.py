from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base

# 题目-知识点/能力标签 多对多中间表 (BR-006)
problem_tag_rel = Table(
    "problem_tag_rel",
    Base.metadata,
    Column("problem_id", Integer, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    major = Column(String(64), nullable=False, default="软件工程")
    grade = Column(String(32), nullable=False, default="2024级")
    contact = Column(String(64), nullable=False, default="")
    department = Column(String(64), nullable=False, default="竞赛部")
    # 会员资格阶段: CANDIDATE | FORMAL | EXITED (BR-001/002)
    stage = Column(String(32), nullable=False, default="CANDIDATE")
    # 会员职责方向: COMPETITION | NON_COMPETITION | UNDECIDED (BR-002)
    direction = Column(String(32), nullable=False, default="UNDECIDED")
    # 管理状态: ACTIVE | OBSERVATION | DISMISSAL_PENDING | DISMISSED | WITHDRAWN (BR-003)
    status = Column(String(32), nullable=False, default="ACTIVE")
    consecutive_failures = Column(Integer, nullable=False, default=0)
    experience = Column(Text, nullable=False, default="")
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assessments = relationship(
        "MemberAssessment", back_populates="member", cascade="all, delete-orphan"
    )
    positions = relationship(
        "OrgPosition", back_populates="member", cascade="all, delete-orphan"
    )
    rewards = relationship(
        "RewardPunishment", back_populates="member", cascade="all, delete-orphan"
    )
    ability_assessments = relationship(
        "AbilityAssessment", back_populates="member", cascade="all, delete-orphan"
    )


class MembershipApplication(Base):
    __tablename__ = "membership_applications"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String(32), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    major = Column(String(64), nullable=False, default="软件工程")
    grade = Column(String(32), nullable=False, default="2024级")
    contact = Column(String(64), nullable=False, default="")
    target_direction = Column(String(32), nullable=False, default="COMPETITION")
    experience = Column(Text, nullable=False, default="")
    # PENDING | APPROVED | REJECTED
    status = Column(String(32), nullable=False, default="PENDING")
    interview_note = Column(Text, nullable=False, default="")
    review_note = Column(Text, nullable=False, default="")
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)


class MemberAssessment(Base):
    __tablename__ = "member_assessments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    cycle = Column(String(64), nullable=False)
    direction = Column(String(32), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False, default=True)
    metrics_json = Column(Text, nullable=False, default="{}")
    comment = Column(Text, nullable=False, default="")
    resulting_status = Column(String(32), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("Member", back_populates="assessments")


class OrgPosition(Base):
    __tablename__ = "org_positions"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    department = Column(String(64), nullable=False)
    title = Column(String(64), nullable=False)  # 会长/副会长/部长/副部长/干事
    term = Column(String(64), nullable=False)
    is_current = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("Member", back_populates="positions")


class RewardPunishment(Base):
    __tablename__ = "rewards_punishments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    # EXCELLENT_MEMBER | EXCELLENT_STAFF | REWARD | WARNING | CRITICISM | SUSPENSION
    record_type = Column(String(32), nullable=False)
    title = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False, default="")
    is_public = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("Member", back_populates="rewards")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    # KNOWLEDGE (算法知识点) | ABILITY (实现能力标签，如模拟/边界处理)
    category = Column(String(32), nullable=False, default="KNOWLEDGE")
    description = Column(Text, nullable=False, default="")

    problems = relationship("Problem", secondary=problem_tag_rel, back_populates="tags")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(160), nullable=False)
    statement = Column(Text, nullable=False, default="")
    sample_input = Column(Text, nullable=False, default="")
    sample_output = Column(Text, nullable=False, default="")
    source = Column(String(64), nullable=False, default="校内题库")
    external_url = Column(String(255), nullable=False, default="")
    # 入门 | 普及 | 提高 | 省选 | NOI (与知识点分离维护 BR-006)
    difficulty = Column(String(32), nullable=False, default="普及")
    status = Column(String(32), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tags = relationship("Tag", secondary=problem_tag_rel, back_populates="problems")
    solutions = relationship(
        "ProblemSolution", back_populates="problem", cascade="all, delete-orphan"
    )
    list_items = relationship(
        "ProblemListItem", back_populates="problem", cascade="all, delete-orphan"
    )


class ProblemSolution(Base):
    __tablename__ = "problem_solutions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    author_name = Column(String(64), nullable=False, default="题库组")
    idea = Column(Text, nullable=False)
    code = Column(Text, nullable=False, default="")
    language = Column(String(32), nullable=False, default="C++17")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    problem = relationship("Problem", back_populates="solutions")


class ProblemList(Base):
    __tablename__ = "problem_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    theme = Column(String(64), nullable=False, default="专题强化")
    target_stage = Column(String(64), nullable=False, default="日常训练")
    # 关联能力评估薄弱维度：lang_basic / basic_algo / simulation_logic / boundary_handling / knowledge_combo / coding_debug
    target_dimension = Column(String(64), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship(
        "ProblemListItem",
        back_populates="problem_list",
        cascade="all, delete-orphan",
        order_by="ProblemListItem.sort_order",
    )


class ProblemListItem(Base):
    __tablename__ = "problem_list_items"

    id = Column(Integer, primary_key=True, index=True)
    problem_list_id = Column(Integer, ForeignKey("problem_lists.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)

    problem_list = relationship("ProblemList", back_populates="items")
    problem = relationship("Problem", back_populates="list_items")


class AbilityAssessment(Base):
    """个人能力评估（独立于会员考核，面向竞赛会员 BR-005）"""

    __tablename__ = "ability_assessments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_name = Column(String(128), nullable=False)
    cycle = Column(String(64), nullable=False)
    lang_basic = Column(Integer, nullable=False)
    basic_algo = Column(Integer, nullable=False)
    simulation_logic = Column(Integer, nullable=False)
    boundary_handling = Column(Integer, nullable=False)
    knowledge_combo = Column(Integer, nullable=False)
    coding_debug = Column(Integer, nullable=False)
    overall_score = Column(Float, nullable=False)
    weak_points_json = Column(Text, nullable=False, default="[]")
    summary = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    member = relationship("Member", back_populates="ability_assessments")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    category = Column(String(32), nullable=False, default="协会事务")
    audience = Column(String(64), nullable=False, default="全体会员")
    content = Column(Text, nullable=False)
    publisher = Column(String(64), nullable=False, default="协会秘书处")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    target = Column(String(128), nullable=False)
    detail = Column(Text, nullable=False, default="")
    operator = Column(String(64), nullable=False, default="协会工作人员")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
