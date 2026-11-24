import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    AbilityAssessment,
    Announcement,
    Member,
    MemberAssessment,
    MembershipApplication,
    OperationLog,
    OrgPosition,
    Problem,
    ProblemList,
    ProblemListItem,
    ProblemSolution,
    RewardPunishment,
    Tag,
)
from app.routers.assessment import analyze_weak_points


def seed_database(db: Session) -> None:
    """幂等初始化高校 ICPC 实验室演示数据（仅当数据库为空时写入）"""
    if db.query(Member).first() is not None:
        return

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1. 初始化会员（覆盖备选、正式竞赛、正式非竞赛、观察状态）
    members_data = [
        Member(
            student_no="202421091067",
            name="李靖宇",
            major="软件工程",
            grade="2024级",
            contact="13800001067",
            department="竞赛部",
            stage="FORMAL",
            direction="COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="ICPC 区域赛铜牌，擅长图论与数据结构，CF Rating 1920",
            joined_at=now - timedelta(days=320),
        ),
        Member(
            student_no="202421091189",
            name="尚思彤",
            major="软件工程",
            grade="2024级",
            contact="13800001189",
            department="题库组",
            stage="FORMAL",
            direction="COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="省赛二等奖，蓝桥杯省一，负责校赛命题与算法专题整理",
            joined_at=now - timedelta(days=300),
        ),
        Member(
            student_no="202421091198",
            name="莫姝",
            major="软件工程",
            grade="2024级",
            contact="13800001198",
            department="技术部",
            stage="FORMAL",
            direction="COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="CCPC 女生专场银牌，擅长动态规划与字符串",
            joined_at=now - timedelta(days=290),
        ),
        Member(
            student_no="202421091165",
            name="覃爽爽",
            major="软件工程",
            grade="2024级",
            contact="13800001165",
            department="办公室",
            stage="FORMAL",
            direction="NON_COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="负责实验室日常考勤、赛事报名组织与文档归档",
            joined_at=now - timedelta(days=285),
        ),
        Member(
            student_no="202421091201",
            name="陈浩然",
            major="计算机科学与技术",
            grade="2024级",
            contact="13800001201",
            department="竞赛部",
            stage="FORMAL",
            direction="COMPETITION",
            status="OBSERVATION",
            consecutive_failures=1,
            experience="基础算法较好，但近期周训缺勤较多进入观察状态",
            joined_at=now - timedelta(days=210),
        ),
        Member(
            student_no="202421091215",
            name="林思远",
            major="人工智能",
            grade="2024级",
            contact="13800001215",
            department="宣传部",
            stage="FORMAL",
            direction="NON_COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="负责校赛海报设计、公众号推送与招新宣讲",
            joined_at=now - timedelta(days=190),
        ),
        Member(
            student_no="202521090312",
            name="周子轩",
            major="软件工程",
            grade="2025级",
            contact="13800000312",
            department="竞赛部",
            stage="CANDIDATE",
            direction="COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="NOIP 提高组二等奖，目前处于备选会员入会考核阶段",
            joined_at=now - timedelta(days=18),
        ),
        Member(
            student_no="202521090345",
            name="许清禾",
            major="数据科学与大数据技术",
            grade="2025级",
            contact="13800000345",
            department="办公室",
            stage="CANDIDATE",
            direction="NON_COMPETITION",
            status="ACTIVE",
            consecutive_failures=0,
            experience="有学生会组织经验，备选阶段参与秋季招新协助",
            joined_at=now - timedelta(days=12),
        ),
    ]
    db.add_all(members_data)
    db.flush()

    m_li, m_shang, m_mo, m_qin, m_chen, m_lin, m_zhou, _m_xu = members_data

    # 2. 入会申请（含待审核与已通过转备选记录）
    applications = [
        MembershipApplication(
            student_no="202521090401",
            name="赵明宇",
            major="计算机科学与技术",
            grade="2025级",
            contact="13900000401",
            target_direction="COMPETITION",
            experience="洛谷刷题 180 道，熟悉 C++ 基础语法与 DFS/BFS",
            status="PENDING",
            created_at=now - timedelta(days=2),
        ),
        MembershipApplication(
            student_no="202521090418",
            name="苏念安",
            major="软件工程",
            grade="2025级",
            contact="13900000418",
            target_direction="NON_COMPETITION",
            experience="擅长活动统筹与数据整理，希望参与协会校赛后勤组织",
            status="PENDING",
            created_at=now - timedelta(days=1),
        ),
        MembershipApplication(
            student_no="202521090312",
            name="周子轩",
            major="软件工程",
            grade="2025级",
            contact="13800000312",
            target_direction="COMPETITION",
            experience="NOIP 提高组二等奖",
            status="APPROVED",
            interview_note="算法基础扎实，面试现场思路清晰",
            review_note="资格审核通过，转入备选会员考核阶段",
            member_id=m_zhou.id,
            created_at=now - timedelta(days=22),
            reviewed_at=now - timedelta(days=18),
        ),
    ]
    db.add_all(applications)

    # 3. 组织任职履历（职务独立于会员方向）
    positions = [
        OrgPosition(member_id=m_li.id, department="协会执委会", title="会长", term="2026-2027学年", is_current=True),
        OrgPosition(member_id=m_mo.id, department="竞赛部", title="部长", term="2026-2027学年", is_current=True),
        OrgPosition(member_id=m_shang.id, department="题库组", title="组长", term="2026-2027学年", is_current=True),
        OrgPosition(member_id=m_qin.id, department="办公室", title="副部长", term="2026-2027学年", is_current=True),
        OrgPosition(member_id=m_lin.id, department="宣传部", title="干事", term="2026-2027学年", is_current=True),
        OrgPosition(member_id=m_li.id, department="竞赛部", title="副部长", term="2025-2026学年", is_current=False),
    ]
    db.add_all(positions)

    # 4. 周期会员考核（体现竞赛与非竞赛双轨指标 BR-002/003/004）
    member_assessments = [
        MemberAssessment(
            member_id=m_li.id,
            cycle="2026-2027第一学期期中",
            direction="COMPETITION",
            score=95.0,
            passed=True,
            metrics_json=json.dumps(
                {
                    "training_completion": 96,
                    "attendance": 98,
                    "mock_contest": 92,
                    "contest_awards": "ICPC 区域赛铜牌",
                },
                ensure_ascii=False,
            ),
            comment="训练与竞赛综合表现优异，推荐参评优秀会员",
            resulting_status="ACTIVE",
            created_at=now - timedelta(days=15),
        ),
        MemberAssessment(
            member_id=m_qin.id,
            cycle="2026-2027第一学期期中",
            direction="NON_COMPETITION",
            score=93.5,
            passed=True,
            metrics_json=json.dumps(
                {
                    "task_completion": 95,
                    "duty_attendance": 96,
                    "work_quality": 92,
                    "collaboration": 94,
                },
                ensure_ascii=False,
            ),
            comment="招新与校赛筹备组织严谨高效，文档归档完整",
            resulting_status="ACTIVE",
            created_at=now - timedelta(days=14),
        ),
        MemberAssessment(
            member_id=m_chen.id,
            cycle="2026-2027第一学期期中",
            direction="COMPETITION",
            score=54.0,
            passed=False,
            metrics_json=json.dumps(
                {
                    "training_completion": 45,
                    "attendance": 55,
                    "mock_contest": 62,
                    "contest_awards": "无",
                },
                ensure_ascii=False,
            ),
            comment="周训练补题率偏低，按 BR-003 转入观察状态",
            resulting_status="OBSERVATION",
            created_at=now - timedelta(days=10),
        ),
    ]
    db.add_all(member_assessments)

    # 5. 奖惩与优秀会员评优
    rewards = [
        RewardPunishment(
            member_id=m_li.id,
            record_type="EXCELLENT_MEMBER",
            title="2026学年秋季优秀竞赛会员",
            reason="区域赛获奖并带领新生完成基础算法专题训练",
            is_public=True,
            created_at=now - timedelta(days=8),
        ),
        RewardPunishment(
            member_id=m_qin.id,
            record_type="EXCELLENT_STAFF",
            title="2026学年秋季优秀干事",
            reason="高质量完成实验室日常运维与协会制度整理",
            is_public=True,
            created_at=now - timedelta(days=8),
        ),
        RewardPunishment(
            member_id=m_chen.id,
            record_type="WARNING",
            title="周训练缺勤观察提醒",
            reason="期中周期考核未达标，进入观察期需补齐专题题单",
            is_public=False,
            created_at=now - timedelta(days=9),
        ),
    ]
    db.add_all(rewards)

    # 6. 知识点与实现能力标签 (BR-006)
    tags_data = [
        Tag(name="动态规划", category="KNOWLEDGE", description="线性DP、区间DP、背包与状态压缩DP"),
        Tag(name="图论", category="KNOWLEDGE", description="最短路、生成树、拓扑排序与连通分量"),
        Tag(name="贪心", category="KNOWLEDGE", description="局部最优决策与交换论证策略"),
        Tag(name="二分查找", category="KNOWLEDGE", description="单调性判定与二分答案建模"),
        Tag(name="数据结构", category="KNOWLEDGE", description="线段树、树状数组、并查集与优先队列"),
        Tag(name="数论", category="KNOWLEDGE", description="质数筛、快速幂、同余与组合计数"),
        Tag(name="字符串", category="KNOWLEDGE", description="KMP、哈希、Trie与自动机"),
        Tag(name="搜索剪枝", category="KNOWLEDGE", description="DFS/BFS、双向搜索与启发式剪枝"),
        Tag(name="模拟", category="ABILITY", description="按题意严谨还原规则与流程状态机"),
        Tag(name="逻辑实现", category="ABILITY", description="复杂分支条件拆分与结构化代码表达"),
        Tag(name="边界处理", category="ABILITY", description="特判零值/极值/数据溢出/空集合等边界"),
        Tag(name="代码调试", category="ABILITY", description="对拍验证、静态排查与复杂代码定位能力"),
    ]
    db.add_all(tags_data)
    db.flush()
    t = {tag.name: tag for tag in tags_data}

    # 7. 经典多标签题目 (N:M 关联)
    problems_spec = [
        (
            "ICPC-1001",
            "实验室机位预约调度",
            "给定 N 组机位使用区间，求最多可安排的不冲突训练场次，并输出字典序最小方案。",
            "4\n1 3\n2 4\n3 5\n5 7",
            "3\n1 3 4",
            "校内题库",
            "",
            "入门",
            ["贪心", "边界处理", "模拟"],
        ),
        (
            "CF-1922C",
            "Closest Cities 环形传送门代价",
            "数轴上有 n 座城市，相邻最近城市移动代价为 1，其余为距离差，处理 m 次左右方向查询。",
            "5\n0 8 12 15 20\n2\n1 4\n5 2",
            "3\n12",
            "Codeforces",
            "https://codeforces.com/problemset/problem/1922/C",
            "普及",
            ["模拟", "逻辑实现", "边界处理"],
        ),
        (
            "ICPC-1002",
            "集训队体力分配与最短路",
            "在带权无向图上从起点到终点，允许最多 k 次将某条边权减半，求最小耗时。",
            "4 4 1\n1 2 10\n2 4 10\n1 3 6\n3 4 12",
            "13",
            "校内题库",
            "",
            "提高",
            ["图论", "动态规划", "边界处理"],
        ),
        (
            "AT-ABC342D",
            "Square Pair 平方数配对统计",
            "统计序列中满足 a[i] * a[j] 为完全平方数的下标对数量，特别注意元素为 0 的边界情况。",
            "5\n0 3 2 8 12",
            "6",
            "AtCoder",
            "https://atcoder.jp/contests/abc342/tasks/abc342_d",
            "普及",
            ["数论", "边界处理"],
        ),
        (
            "CF-1873F",
            "Money Trees 双指针与前缀限界",
            "给定果树高度与果子数，求满足相邻整除关系且总和不超过 k 的最长连续子段。",
            "5 12\n3 2 4 1 8\n4 4 2 4 1",
            "3",
            "Codeforces",
            "https://codeforces.com/problemset/problem/1873/F",
            "普及",
            ["二分查找", "逻辑实现", "边界处理"],
        ),
        (
            "ICPC-1003",
            "多校榜单滚榜模拟器",
            "完整模拟 ICPC 封榜后自底向上的滚榜揭晓动画顺序、罚时计算与同分排序。",
            "3 2\nTeamA 1 20 +\nTeamB 2 180 ?",
            "TeamB\nTeamA",
            "校内题库",
            "",
            "提高",
            ["模拟", "逻辑实现", "数据结构", "代码调试"],
        ),
        (
            "LG-P1040",
            "加分二叉树区间形态还原",
            "给定中序遍历节点权值，求最大加分并输出对应前序遍历序列。",
            "5\n5 7 1 2 10",
            "145\n3 1 2 4 5",
            "洛谷",
            "https://www.luogu.com.cn/problem/P1040",
            "提高",
            ["动态规划", "逻辑实现"],
        ),
        (
            "CF-1914F",
            "Programming Competition 树上最大配对",
            "一棵有根树表示上下级关系，两成员互不为祖先即可组队，求最多组成多少支两人队。",
            "6\n1 1 2 2 3",
            "2",
            "Codeforces",
            "https://codeforces.com/problemset/problem/1914/F",
            "提高",
            ["图论", "贪心", "动态规划"],
        ),
        (
            "ICPC-1004",
            "动态区间最长上升子序列维护",
            "支持单点修改与区间查询，结合权值线段树优化动态规划状态转移。",
            "5 2\n1 5 2 4 3\nQ 1 5\nU 3 6",
            "3",
            "校内题库",
            "",
            "省选",
            ["数据结构", "动态规划", "代码调试"],
        ),
        (
            "NK-26891",
            "子串匹配与多模敏感词过滤",
            "在长日志文本中快速定位所有命中的关键词并输出首次出现位置。",
            "3\nicpc\nccpc\nalgo\nicpc_ccpc_lab",
            "0 5",
            "牛客",
            "https://ac.nowcoder.com/",
            "提高",
            ["字符串", "数据结构", "边界处理"],
        ),
    ]

    problems = []
    for code, title, stmt, sin, sout, src, url, diff, tag_names in problems_spec:
        p = Problem(
            code=code,
            title=title,
            statement=stmt,
            sample_input=sin,
            sample_output=sout,
            source=src,
            external_url=url,
            difficulty=diff,
            tags=[t[n] for n in tag_names],
        )
        db.add(p)
        problems.append(p)
    db.flush()

    # 8. 题解沉淀
    solutions = [
        ProblemSolution(
            problem_id=problems[2].id,
            title="分层图 Dijkstra 标准解法",
            author_name="李靖宇",
            idea="将状态拆分为 (u, used_k)，对每条边建同层正常边与跨层半价边，共 k+1 层图跑堆优化 Dijkstra。注意 long long 防止权值累加溢出。",
            code="#include <bits/stdc++.h>\nusing namespace std;\n// 分层图 Dijkstra 核心转移: dist[v][c+1] = min(dist[v][c+1], d + w/2);",
            language="C++17",
        ),
        ProblemSolution(
            problem_id=problems[3].id,
            title="分解无平方因子核 + 零值特判",
            author_name="尚思彤",
            idea="将每个正整数剔除所有平方因子得到唯一核值 core(x)，相同核值两两配对。边界处理关键：值为 0 的元素可与任意元素配对成 0（也是平方数）。",
            code="long long ans = cnt0 * (n - cnt0) + cnt0 * (cnt0 - 1) / 2;",
            language="C++17",
        ),
        ProblemSolution(
            problem_id=problems[5].id,
            title="优先队列维护封榜队伍滚榜状态机",
            author_name="莫姝",
            idea="将每支队伍的过题数、罚时与封榜待揭晓队列封装为结构体，自排名末位逐个弹出最早待揭晓提交并重新插入有序集合。",
            code="struct Team { string name; int solved, penalty; queue<Sub> frozen; };",
            language="C++17",
        ),
    ]
    db.add_all(solutions)

    # 9. 专题题单（关联薄弱能力维度，支持自动推荐闭环）
    pl_configs = [
        (
            "边界处理与零值溢出专项补强题单",
            "边界处理",
            "日常补强",
            "boundary_handling",
            "专门针对边界特判遗漏、数据溢出和极端输入 WA 的高频精选题目。",
            [problems[0], problems[1], problems[3], problems[4]],
        ),
        (
            "大模拟与复杂逻辑状态机实战题单",
            "模拟与逻辑",
            "日常补强",
            "simulation_logic",
            "提升复杂题意建模、条件拆解与代码结构化实现能力。",
            [problems[1], problems[5], problems[6]],
        ),
        (
            "多知识点综合组合突破题单",
            "综合组合",
            "阶段拔高",
            "knowledge_combo",
            "精选图论+DP、数据结构+DP 等区域赛常见多知识点组合题。",
            [problems[2], problems[7], problems[8], problems[9]],
        ),
        (
            "代码实现与对拍调试强化题单",
            "实现调试",
            "集训前置",
            "coding_debug",
            "面向代码量大、容易写挂细节的综合题，建议配合随机数据对拍完成。",
            [problems[5], problems[8]],
        ),
    ]
    for title, theme, stage, dim, desc, plist in pl_configs:
        pl = ProblemList(
            title=title,
            theme=theme,
            target_stage=stage,
            target_dimension=dim,
            description=desc,
        )
        db.add(pl)
        db.flush()
        for idx, p in enumerate(plist, start=1):
            db.add(ProblemListItem(problem_list_id=pl.id, problem_id=p.id, sort_order=idx))

    # 10. 个人能力评估历史（每人多周期，直观展示雷达图对比与薄弱项演变）
    ability_seed = [
        (
            m_li,
            "2026春季摸底能力评估",
            "2026-S1",
            {"lang_basic": 86, "basic_algo": 84, "simulation_logic": 72, "boundary_handling": 66, "knowledge_combo": 78, "coding_debug": 75},
            "基础算法扎实，但大模拟与边界细节偶尔罚时偏高。",
            now - timedelta(days=90),
        ),
        (
            m_li,
            "2026秋季赛前能力评估",
            "2026-S2",
            {"lang_basic": 92, "basic_algo": 90, "simulation_logic": 81, "boundary_handling": 78, "knowledge_combo": 88, "coding_debug": 84},
            "经专项补强后边界处理显著提升，当前各项能力均衡达到区域赛主力水平。",
            now - timedelta(days=7),
        ),
        (
            m_shang,
            "2026春季摸底能力评估",
            "2026-S1",
            {"lang_basic": 80, "basic_algo": 74, "simulation_logic": 64, "boundary_handling": 58, "knowledge_combo": 62, "coding_debug": 68},
            "语言基础较好，边界特判与多知识点融合题稳定性待加强。",
            now - timedelta(days=85),
        ),
        (
            m_shang,
            "2026秋季阶段能力评估",
            "2026-S2",
            {"lang_basic": 88, "basic_algo": 82, "simulation_logic": 74, "boundary_handling": 65, "knowledge_combo": 68, "coding_debug": 76},
            "算法与调试能力进步明显，建议继续跟进「边界处理」与「知识点组合」题单。",
            now - timedelta(days=6),
        ),
        (
            m_mo,
            "2026春季摸底能力评估",
            "2026-S1",
            {"lang_basic": 84, "basic_algo": 80, "simulation_logic": 62, "boundary_handling": 71, "knowledge_combo": 76, "coding_debug": 64},
            "思维速度快、DP熟练，但在复杂大模拟和长代码调试上耗时偏多。",
            now - timedelta(days=80),
        ),
        (
            m_mo,
            "2026秋季阶段能力评估",
            "2026-S2",
            {"lang_basic": 90, "basic_algo": 86, "simulation_logic": 68, "boundary_handling": 80, "knowledge_combo": 85, "coding_debug": 66},
            "DP 与组合应用优势突出，下一阶段重点补强模拟状态机与对拍调试效率。",
            now - timedelta(days=5),
        ),
        (
            m_chen,
            "2026秋季诊断能力评估",
            "2026-S2",
            {"lang_basic": 72, "basic_algo": 64, "simulation_logic": 58, "boundary_handling": 52, "knowledge_combo": 48, "coding_debug": 55},
            "观察期专项摸底：基础算法与边界处理薄弱，需按题单完成补强后申请复评。",
            now - timedelta(days=4),
        ),
    ]

    for member, name, cycle, scores, summary, created_at in ability_seed:
        overall = round(sum(scores.values()) / len(scores), 1)
        weak = analyze_weak_points(scores)
        db.add(
            AbilityAssessment(
                member_id=member.id,
                assessment_name=name,
                cycle=cycle,
                overall_score=overall,
                weak_points_json=json.dumps(weak, ensure_ascii=False),
                summary=summary,
                created_at=created_at,
                **scores,
            )
        )

    # 11. 系统公告
    announcements = [
        Announcement(
            title="关于 2026 秋季期中会员考核与优秀会员公示的通知",
            category="协会事务",
            audience="全体会员",
            content="2026-2027 第一学期期中考核已完成汇总，李靖宇、覃爽爽获评优秀会员/干事；进入观察状态的成员请按要求在两周内完成补强复核。",
            publisher="协会秘书处",
            created_at=now - timedelta(days=3),
        ),
        Announcement(
            title="新版多标签题库与六维个人能力评估系统（v0.5.0）上线试运行",
            category="训练安排",
            audience="竞赛会员",
            content="Kcat 小组已完成协会管理、多标签题库与个人能力评估三大模块上线，请竞赛方向队员登录查看个人能力雷达图与推荐补强题单。",
            publisher="Kcat 开发组",
            created_at=now - timedelta(days=1),
        ),
        Announcement(
            title="2025 级备选会员第一次入会考核安排",
            category="考核通知",
            audience="备选会员",
            content="请已通过资格面试的备选会员于本周六 14:00 到计算机学院机房 402 参加上机入会考核，考核通过后正式定岗定方向。",
            publisher="竞赛部",
            created_at=now - timedelta(hours=10),
        ),
    ]
    db.add_all(announcements)

    # 12. 操作日志
    db.add_all(
        [
            OperationLog(
                module="系统初始化",
                action="加载里程碑基线",
                target="v0.5.0-milestone",
                detail="初始化 8 名会员档案、12 个知识点/能力标签、10 道经典题与 7 份能力评估记录",
                operator="系统引导",
                created_at=now - timedelta(days=1),
            ),
            OperationLog(
                module="协会管理",
                action="录入周期考核",
                target="陈浩然(202421091201)",
                detail="[2026-2027第一学期期中] 得分:54.0 合格:False -> 自动流转至【观察状态】(BR-003)",
                operator="协会工作人员",
                created_at=now - timedelta(hours=18),
            ),
            OperationLog(
                module="个人能力评估",
                action="生成能力画像",
                target="尚思彤(202421091189)",
                detail="[2026-S2] 综合分:75.5 自动匹配推荐补强题单 2 套",
                operator="竞赛部",
                created_at=now - timedelta(hours=5),
            ),
        ]
    )

    db.commit()
