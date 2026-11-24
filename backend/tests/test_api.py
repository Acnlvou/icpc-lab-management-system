import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# 在导入 app 之前指向独立临时 SQLite 测试库，确保测试隔离且可重复运行
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["ICPC_DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    if os.path.exists(_tmp_db.name):
        os.remove(_tmp_db.name)


def test_health_and_dashboard_overview(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["progress"] == "50%"

    ov = client.get("/api/v1/dashboard/overview")
    assert ov.status_code == 200
    data = ov.json()
    assert data["progress"]["overall_percent"] == 50
    assert data["kpi"]["total_members"] >= 8
    assert data["kpi"]["total_problems"] >= 10
    assert len(data["announcements"]) >= 1


def test_application_to_candidate_and_promote_flow(client):
    """验证 FR-AM-001/002/003 与 BR-001/BR-002：申请 -> 审核通过变备选 -> 入会考核转正并确定方向"""
    create_res = client.post(
        "/api/v1/association/applications",
        json={
            "student_no": "202599990001",
            "name": "测试新生",
            "major": "软件工程",
            "grade": "2025级",
            "contact": "13999990001",
            "target_direction": "COMPETITION",
            "experience": "熟悉 C++ 基础与STL",
        },
    )
    assert create_res.status_code == 201
    app_id = create_res.json()["id"]

    # 审核通过 -> 自动进入 CANDIDATE 备选会员阶段 (BR-001)
    review_res = client.post(
        f"/api/v1/association/applications/{app_id}/review",
        json={
            "approved": True,
            "interview_note": "逻辑清晰",
            "review_note": "同意进入备选考核",
            "department": "竞赛部",
        },
    )
    assert review_res.status_code == 200
    member_id = review_res.json()["member_id"]
    assert member_id is not None

    profile = client.get(f"/api/v1/association/members/{member_id}").json()
    assert profile["member"]["stage"] == "CANDIDATE"
    assert profile["member"]["status"] == "ACTIVE"

    # 备选会员尚未转正，不可直接录入正式会员周期考核
    bad_assess = client.post(
        "/api/v1/association/assessments",
        json={"member_id": member_id, "cycle": "2026-Q4", "score": 80, "passed": True, "metrics": {}},
    )
    assert bad_assess.status_code == 400

    # 通过入会考核转正为正式竞赛会员 (BR-002)
    promo = client.post(
        f"/api/v1/association/members/{member_id}/promote",
        json={"direction": "COMPETITION", "department": "竞赛部", "note": "上机考核 AK 3题通过"},
    )
    assert promo.status_code == 200
    assert promo.json()["stage"] == "FORMAL"
    assert promo.json()["direction"] == "COMPETITION"

    # 已转正会员不可重复转正
    dup_promo = client.post(
        f"/api/v1/association/members/{member_id}/promote",
        json={"direction": "COMPETITION", "department": "竞赛部"},
    )
    assert dup_promo.status_code == 400


def test_periodic_assessment_observation_and_dismissal_flow(client):
    """验证 FR-AM-005/007 与 BR-003：单次不合格->观察，连续两次不合格->待清退，合格->恢复正常"""
    m = client.post(
        "/api/v1/association/members",
        json={
            "student_no": "202599990002",
            "name": "状态流转测试员",
            "major": "软件工程",
            "grade": "2024级",
            "department": "竞赛部",
            "stage": "FORMAL",
            "direction": "COMPETITION",
        },
    ).json()
    mid = m["id"]

    # 首次不合格 -> OBSERVATION
    r1 = client.post(
        "/api/v1/association/assessments",
        json={
            "member_id": mid,
            "cycle": "2026-第1次",
            "score": 52,
            "passed": False,
            "metrics": {"training_completion": 40, "attendance": 50},
            "comment": "训练完成不足",
        },
    )
    assert r1.status_code == 201
    assert r1.json()["resulting_status"] == "OBSERVATION"

    # 连续第二次不合格 -> DISMISSAL_PENDING
    r2 = client.post(
        "/api/v1/association/assessments",
        json={
            "member_id": mid,
            "cycle": "2026-第2次",
            "score": 48,
            "passed": False,
            "metrics": {"training_completion": 30, "attendance": 45},
            "comment": "连续两次未达标",
        },
    )
    assert r2.status_code == 201
    assert r2.json()["resulting_status"] == "DISMISSAL_PENDING"

    # 若后续通过申诉复评合格，恢复计数（手动恢复或复评）
    r3 = client.post(
        f"/api/v1/association/members/{mid}/status",
        json={"status": "ACTIVE", "reason": "补考与补题达标，解除清退预警"},
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "ACTIVE"
    assert r3.json()["consecutive_failures"] == 0


def test_member_full_profile_and_org_position_separation(client):
    """验证 FR-AM-008/009/010：任职与奖惩独立维护并汇总到完整档案"""
    members = client.get("/api/v1/association/members").json()
    first_id = members[0]["id"]

    pos = client.post(
        "/api/v1/association/positions",
        json={"member_id": first_id, "department": "算法研发组", "title": "副部长", "term": "2026-2027"},
    )
    assert pos.status_code == 201

    rew = client.post(
        "/api/v1/association/rewards",
        json={"member_id": first_id, "record_type": "REWARD", "title": "模拟赛第一名", "reason": "单场 AK"},
    )
    assert rew.status_code == 201

    profile = client.get(f"/api/v1/association/members/{first_id}").json()
    assert len(profile["positions"]) >= 1
    assert len(profile["rewards"]) >= 1


def test_question_bank_many_to_many_and_combo_search(client):
    """验证 FR-QB-001..004 与 BR-006：多对多标签关联、难度独立维护及 AND/OR 组合检索"""
    t1 = client.post(
        "/api/v1/question-bank/tags",
        json={"name": "网络流", "category": "KNOWLEDGE", "description": "最大流与费用流"},
    ).json()
    t2 = client.post(
        "/api/v1/question-bank/tags",
        json={"name": "卡常优化", "category": "ABILITY", "description": "常数与缓存友好优化"},
    ).json()

    p = client.post(
        "/api/v1/question-bank/problems",
        json={
            "code": "TEST-9001",
            "title": "网络流与常数优化综合题",
            "statement": "求有向图最大流",
            "source": "校内题库",
            "difficulty": "省选",
            "tag_ids": [t1["id"], t2["id"]],
        },
    )
    assert p.status_code == 201
    pid = p.json()["id"]
    assert len(p.json()["tags"]) == 2

    # 交集 (AND) 检索应精准命中 TEST-9001
    res_and = client.get(
        "/api/v1/question-bank/problems",
        params={"tag_ids": f"{t1['id']},{t2['id']}", "match_mode": "all", "difficulty": "省选"},
    ).json()
    assert [x["code"] for x in res_and] == ["TEST-9001"]

    # 添加题解与题单并校验题库统计 (FR-QB-005/006/007)
    sol = client.post(
        f"/api/v1/question-bank/problems/{pid}/solutions",
        json={"title": "Dinic 当前弧优化", "author_name": "测试者", "idea": "分层图+多路增广", "code": "// dinic"},
    )
    assert sol.status_code == 201

    pl = client.post(
        "/api/v1/question-bank/problem-lists",
        json={
            "title": "图论高阶强化题单",
            "theme": "网络流",
            "target_dimension": "knowledge_combo",
            "problem_ids": [pid],
        },
    )
    assert pl.status_code == 201
    assert len(pl.json()["items"]) == 1

    stats = client.get("/api/v1/question-bank/stats").json()
    assert stats["total_problems"] >= 11
    assert stats["total_solutions"] >= 4


def test_ability_assessment_independence_and_weak_points(client):
    """验证 FR-AB-001..005 与 BR-005：能力评估独立于会员考核、仅面向竞赛会员、自动识别薄弱项与推荐题单"""
    members = client.get("/api/v1/association/members").json()
    non_comp = next(m for m in members if m["direction"] == "NON_COMPETITION")
    comp = next(m for m in members if m["student_no"] == "202421091189")

    # 非竞赛会员不可创建个人能力评估 (BR-005)
    bad = client.post(
        "/api/v1/ability/assessments",
        json={
            "member_id": non_comp["id"],
            "assessment_name": "非法评估尝试",
            "cycle": "2026-S2",
            "lang_basic": 80,
            "basic_algo": 70,
            "simulation_logic": 70,
            "boundary_handling": 70,
            "knowledge_combo": 70,
            "coding_debug": 70,
        },
    )
    assert bad.status_code == 400

    # 竞赛会员提交评估，故意令边界处理(55)与模拟逻辑(62)低于70分
    ok = client.post(
        "/api/v1/ability/assessments",
        json={
            "member_id": comp["id"],
            "assessment_name": "2026冬季专项能力复评",
            "cycle": "2026-S3",
            "lang_basic": 90,
            "basic_algo": 85,
            "simulation_logic": 62,
            "boundary_handling": 55,
            "knowledge_combo": 82,
            "coding_debug": 78,
            "summary": "边界与模拟短板明显",
        },
    )
    assert ok.status_code == 201
    weak_keys = [w["dimension_key"] for w in ok.json()["weak_points"]]
    assert "boundary_handling" in weak_keys
    assert "simulation_logic" in weak_keys

    # 验证画像接口自动关联题库补强题单
    prof = client.get(f"/api/v1/ability/members/{comp['id']}/profile").json()
    assert prof["latest"]["assessment_name"] == "2026冬季专项能力复评"
    assert len(prof["history"]) >= 2
    assert len(prof["recommended_lists"]) >= 1


def test_announcement_creation(client):
    res = client.post(
        "/api/v1/dashboard/announcements",
        json={
            "title": "本周末组织阶段性模拟赛",
            "category": "训练安排",
            "audience": "竞赛会员",
            "content": "请按时签到并提交补题记录",
            "publisher": "竞赛部",
        },
    )
    assert res.status_code == 201
    assert res.json()["title"] == "本周末组织阶段性模拟赛"
