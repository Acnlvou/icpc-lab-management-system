<template>
  <div class="radar-wrap">
    <svg :viewBox="`0 0 ${size} ${size}`" class="radar-svg">
      <!-- 同心六边形网格 -->
      <polygon
        v-for="ring in rings"
        :key="ring"
        :points="polygonPoints(ring)"
        fill="none"
        stroke="#e2e8f0"
        stroke-width="1"
      />
      <!-- 70分薄弱警戒虚线 -->
      <polygon
        :points="polygonPoints(70)"
        fill="none"
        stroke="#f59e0b"
        stroke-dasharray="4 3"
        stroke-width="1.2"
        opacity="0.7"
      />
      <!-- 6条轴线 -->
      <line
        v-for="(dim, idx) in dimensions"
        :key="'axis-' + dim.key"
        :x1="cx"
        :y1="cy"
        :x2="pointAt(idx, 100).x"
        :y2="pointAt(idx, 100).y"
        stroke="#cbd5e1"
        stroke-width="1"
      />
      <!-- 上一期对比多边形 -->
      <polygon
        v-if="previous"
        :points="dataPolygon(previous)"
        fill="rgba(16, 185, 129, 0.12)"
        stroke="#10b981"
        stroke-width="2"
        stroke-dasharray="5 3"
      />
      <!-- 当前期能力多边形 -->
      <polygon
        v-if="latest"
        :points="dataPolygon(latest)"
        fill="rgba(37, 99, 235, 0.2)"
        stroke="#2563eb"
        stroke-width="2.5"
      />
      <!-- 当前期顶点圆点（低于70分标红提醒） -->
      <g v-if="latest">
        <circle
          v-for="(dim, idx) in dimensions"
          :key="'pt-' + dim.key"
          :cx="pointAt(idx, latest[dim.key] || 0).x"
          :cy="pointAt(idx, latest[dim.key] || 0).y"
          r="5"
          :fill="(latest[dim.key] || 0) < 70 ? '#dc2626' : '#2563eb'"
          stroke="#ffffff"
          stroke-width="2"
        />
      </g>
      <!-- 维度文字与分值 -->
      <g v-for="(dim, idx) in dimensions" :key="'lbl-' + dim.key">
        <text
          :x="labelPoint(idx).x"
          :y="labelPoint(idx).y"
          text-anchor="middle"
          dominant-baseline="middle"
          font-size="12"
          font-weight="700"
          :fill="latest && (latest[dim.key] || 0) < 70 ? '#dc2626' : '#1e293b'"
        >
          {{ dim.label }}
        </text>
        <text
          v-if="latest"
          :x="labelPoint(idx).x"
          :y="labelPoint(idx).y + 15"
          text-anchor="middle"
          dominant-baseline="middle"
          font-size="11"
          font-weight="600"
          :fill="(latest[dim.key] || 0) < 70 ? '#dc2626' : '#2563eb'"
        >
          {{ latest[dim.key] }}分
          <tspan v-if="previous" fill="#059669">
            ({{ formatDelta(latest[dim.key] - previous[dim.key]) }})
          </tspan>
        </text>
      </g>
    </svg>

    <div class="radar-legend">
      <span><i class="dot dot-blue"></i> 最新评估（{{ latest?.cycle || '-' }}）</span>
      <span v-if="previous"><i class="dot dot-green"></i> 上期对比（{{ previous.cycle }}）</span>
      <span><i class="dot dot-amber"></i> 70分薄弱阈值线</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  latest: { type: Object, default: null },
  previous: { type: Object, default: null }
})

const size = 380
const cx = size / 2
const cy = size / 2
const radius = 122
const rings = [20, 40, 60, 80, 100]

const dimensions = [
  { key: 'lang_basic', label: '编程语言基础' },
  { key: 'basic_algo', label: '基础算法' },
  { key: 'simulation_logic', label: '模拟与逻辑' },
  { key: 'boundary_handling', label: '边界处理' },
  { key: 'knowledge_combo', label: '知识点组合' },
  { key: 'coding_debug', label: '代码实现调试' }
]

function pointAt(idx, score) {
  const angle = -Math.PI / 2 + (idx * 2 * Math.PI) / dimensions.length
  const r = (Math.max(0, Math.min(100, score)) / 100) * radius
  return {
    x: cx + r * Math.cos(angle),
    y: cy + r * Math.sin(angle)
  }
}

function labelPoint(idx) {
  const angle = -Math.PI / 2 + (idx * 2 * Math.PI) / dimensions.length
  const r = radius + 36
  return {
    x: cx + r * Math.cos(angle),
    y: cy + r * Math.sin(angle)
  }
}

function polygonPoints(val) {
  return dimensions.map((_, idx) => {
    const p = pointAt(idx, val)
    return `${p.x.toFixed(1)},${p.y.toFixed(1)}`
  }).join(' ')
}

function dataPolygon(record) {
  return dimensions.map((dim, idx) => {
    const p = pointAt(idx, record[dim.key] || 0)
    return `${p.x.toFixed(1)},${p.y.toFixed(1)}`
  }).join(' ')
}

function formatDelta(d) {
  return d >= 0 ? `+${d}` : `${d}`
}
</script>

<style scoped>
.radar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.radar-svg {
  width: 100%;
  max-width: 390px;
  height: auto;
}
.radar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  font-size: 12px;
  color: #475569;
  margin-top: 6px;
}
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
  vertical-align: -1px;
}
.dot-blue { background: #2563eb; }
.dot-green { background: #10b981; }
.dot-amber { background: #f59e0b; }
</style>
