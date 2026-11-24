<template>
  <div>
    <div class="card" style="margin-bottom:18px;">
      <div class="card-title">
        <span>后续 50% 迭代研发路线图（Sprint 3 ~ Sprint 4）</span>
        <span class="badge badge-blue">遵循 SDD 规范递进交付</span>
      </div>
      <p style="margin:0;font-size:13px;color:#475569;">
        当前项目已完成 50% 核心业务底座（协会管理、多标签题库管理、个人能力评估与统计看板）。下一阶段将直接复用已沉淀的会员档案、能力薄弱项清单与专题题单数据，无缝串联日常训练、寒暑假集训、智能组队及校赛/XCPC 赛事闭环。
      </p>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">
          <span>Sprint 3：训练与集训管理（计划占比 25%）</span>
          <span class="badge badge-amber">规划中</span>
        </div>
        <ul style="padding-left:18px;font-size:13px;color:#334155;line-height:1.8;">
          <li><strong>FR-TRN-001 ~ 002 日常训练计划</strong>：整体学期训练节奏 + 基于「个人能力评估薄弱项」自动生成个人补强训练规划（BR-007）。</li>
          <li><strong>FR-TRN-003 ~ 006 任务下发与闭环复盘</strong>：直接引用题库专题题单发布周任务，记录考勤与补题率，效果评估后回流开启新一轮能力评估。</li>
          <li><strong>FR-WIN-001 ~ 003 寒假集训</strong>：围绕基础补强组织每日专题、模拟赛、考勤与阶段复盘。</li>
          <li><strong>FR-SUM-001 ~ 003 暑假集训</strong>：面向网络赛与正赛的多校联训成绩沉淀、补题与解法分享。</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Sprint 4：队伍与竞赛管理（计划占比 25%）</span>
          <span class="badge badge-amber">规划中</span>
        </div>
        <ul style="padding-left:18px;font-size:13px;color:#334155;line-height:1.8;">
          <li><strong>FR-TEAM-001 ~ 005 组队管理</strong>：结合个人竞赛成绩与六维能力画像进行成员能力互补分析，生成候选队伍并维护调整历史。</li>
          <li><strong>FR-CMP-001 ~ 008 校赛管理</strong>：覆盖线上初赛、异常代码行为人工核查材料留存（BR-010）、晋级决赛确认与候补递补流程（BR-009）。</li>
          <li><strong>FR-NC-001 ~ 002 非 XCPC 赛事</strong>：统一管理蓝桥杯、天梯赛、码蹄杯、百度之星报名与获奖归档。</li>
          <li><strong>FR-XCPC-001 ~ 004 XCPC 赛事管理</strong>：串联暑假集训、网络预选赛队伍综合排序、正赛名额赛站分配与赛后总结（BR-008）。</li>
        </ul>
      </div>
    </div>
  </div>
</template>
