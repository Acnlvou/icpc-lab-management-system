<template>
  <div>
    <div class="card" style="margin-bottom:18px;">
      <div class="card-title">
        <span>项目里程碑与交付总览（v1.0.0 正式版）</span>
        <span class="badge badge-green">进度 100% · 五大模块已交付</span>
      </div>
      <p style="margin:0;font-size:13px;color:#475569;">
        Kcat 小组遵循 Scrum + SDD（规范驱动开发）完成 ICPC 实验室管理系统全量交付：协会管理 → 题库管理 → 个人能力评估 → 训练与集训 → 队伍与竞赛，核心业务规则 BR-001 ~ BR-010 全部落地。
      </p>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="card-title"><span>Sprint 1 · 协会管理</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">入会审核 → 备选转正、双轨周期考核与 BR-003 状态自动流转、任职履历与奖惩评优。</p>
        <router-link to="/association" class="btn btn-sm" style="margin-top:12px;">进入协会管理中心 →</router-link>
      </div>
      <div class="card">
        <div class="card-title"><span>Sprint 1-2 · 题库管理</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">知识点/能力标签多对多、AND/OR 组合检索、题解抽屉与专题题单编排（BR-006）。</p>
        <router-link to="/question-bank" class="btn btn-sm" style="margin-top:12px;">进入算法题库 →</router-link>
      </div>
      <div class="card">
        <div class="card-title"><span>Sprint 2 · 能力评估</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">六维能力雷达图、薄弱项自动诊断与补强题单联动闭环（BR-005）。</p>
        <router-link to="/ability" class="btn btn-sm" style="margin-top:12px;">进入个人能力评估 →</router-link>
      </div>
      <div class="card">
        <div class="card-title"><span>Sprint 3 · 训练与集训</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">个人补强计划（BR-007）、周任务打卡考勤、寒暑假集训与多校联训看板。</p>
        <router-link to="/training" class="btn btn-sm" style="margin-top:12px;">进入训练与集训 →</router-link>
      </div>
      <div class="card">
        <div class="card-title"><span>Sprint 4 · 队伍与竞赛</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">能力互补组队、校赛晋级候补递补（BR-009）、异常行为人工复核（BR-010）、XCPC/非XCPC 成绩归档。</p>
        <router-link to="/contest" class="btn btn-sm" style="margin-top:12px;">进入队伍与竞赛 →</router-link>
      </div>
      <div class="card">
        <div class="card-title"><span>Sprint 0 · SDD 规范建基</span><span class="badge badge-green">已完成</span></div>
        <p style="font-size:13px;color:#475569;margin:0;">需求分析、系统架构、数据库设计、API 契约与 .spec 规范冻结，贯穿全流程 AI 协作。</p>
        <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer" class="btn btn-sm" style="margin-top:12px;">Swagger API 文档 ↗</a>
      </div>
    </div>
  </div>
</template>
