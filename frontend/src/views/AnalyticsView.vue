<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📊 数据分析</h2>
        <p class="page-sub">同类型考试才可比：先选类型，再看趋势、对比与单科深钻</p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <n-select v-model:value="classId" placeholder="班级" :options="classOptions" style="width:150px" @update:value="onClassChange" />
        <n-select v-model:value="typeId" placeholder="考试类型" :options="typeOptions" style="width:140px" @update:value="reload" />
      </div>
    </div>

    <!-- 历次考试趋势（限所选类型） -->
    <div class="chart-card wide pop-in">
      <h4>📈 {{ typeLabel }}历次考试主科平均分趋势 <span class="tip">（{{ trendExams.length }} 场）</span></h4>
      <v-chart :option="trendOption" height="300px" v-if="trendExams.length" />
      <n-empty v-else description="该类型暂无考试" style="padding:30px 0" />
    </div>

    <!-- 单科深钻 -->
    <div class="chart-card wide pop-in" style="margin-top:16px">
      <div class="chart-toolbar">
        <h4 style="flex:1">🔬 单科深钻 · {{ subjectName }}</h4>
        <n-select v-model:value="subjectId" :options="subjectOptions" size="small" style="width:120px" @update:value="loadSubjectTrend" />
      </div>
      <v-chart :option="subjectOption" height="300px" v-if="subjectItems.length" />
      <n-empty v-else description="暂无数据" style="padding:30px 0" />
      <div class="dist-meta" v-if="subjectLatest">
        <span>最近:{{ subjectLatest.name }}</span>
        <span>均分 {{ subjectLatest.avg }}</span>
        <span>最高 {{ subjectLatest.max }}</span>
        <span>最低 {{ subjectLatest.min }}</span>
        <span>及格率 {{ subjectLatest.pass_rate }}%</span>
      </div>
    </div>

    <!-- 任意两场对比（不限类型，才能期中 vs 期末） -->
    <div class="chart-card wide pop-in" style="margin-top:16px">
      <div class="chart-toolbar">
        <h4 style="flex:1">⚔️ 两场对比</h4>
        <n-select v-model:value="examAId" :options="allExamOptions" size="small" style="width:170px" @update:value="loadCross" />
        <span class="vs">vs</span>
        <n-select v-model:value="examBId" :options="allExamOptions" size="small" style="width:170px" @update:value="loadCross" />
      </div>
      <v-chart :option="crossOption" height="300px" v-if="crossData" />
      <n-empty v-else description="选择两场考试进行对比" style="padding:30px 0" />
      <div class="delta-list" v-if="deltaRows.length">
        <div v-for="d in deltaRows" :key="d.name" class="delta-row">
          <span class="d-name" :style="{ background: d.color }">{{ d.name }}</span>
          <span class="d-val">{{ d.a ?? '—' }} → {{ d.b ?? '—' }}</span>
          <b :style="{ color: d.delta > 0 ? '#16a34a' : d.delta < 0 ? '#dc2626' : '#8a7a6b' }">
            {{ d.delta === null ? '' : (d.delta > 0 ? '▲' : d.delta < 0 ? '▼' : '—') + Math.abs(d.delta ?? 0) }}
          </b>
        </div>
      </div>
    </div>

    <!-- 分布 + 前十 -->
    <div class="chart-grid" style="margin-top:16px">
      <div class="chart-card">
        <div class="chart-toolbar">
          <h4 style="flex:1">🎯 成绩分布</h4>
          <n-select v-model:value="distExamId" :options="allExamOptions" size="small" style="width:170px" @update:value="loadDist" />
          <n-select v-model:value="distSubjectId" :options="subjectOptions" size="small" style="width:100px" @update:value="loadDist" />
        </div>
        <v-chart :option="distOption" height="280px" v-if="distSeries.length" />
        <n-empty v-else description="暂无数据" style="padding:30px 0" />
        <div class="dist-meta" v-if="distMeta">
          <span>平均 {{ distMeta.avg }}</span>
          <span>及格率 {{ distMeta.pass_rate }}%</span>
          <span>参考 {{ distMeta.count }} 人</span>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-toolbar">
          <h4 style="flex:1">🥇 班级总分前十</h4>
          <n-select v-model:value="topExamId" :options="allExamOptions" size="small" style="width:170px" @update:value="loadTop" />
        </div>
        <v-chart :option="topOption" height="280px" v-if="topSeries.length" />
        <n-empty v-else description="暂无数据" style="padding:30px 0" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'
import VChart, { CARTOON_COLORS, baseTooltip } from '../components/VChart'

const message = useMessage()
const classId = ref(null)
const classOptions = ref([])
const typeId = ref(null)
const typeOptions = ref([])
const TYPE_MAP = {}

const allExamOptions = ref([])   // 全班考试（不限类型），供对比/分布/前十选场次
const subjectOptions = ref([])
const subjectId = ref(null)

const trendExams = ref([])
const trendSeries = ref([])
const subjectItems = ref([])
const subjectName = ref('')
const subjectFull = ref(100)
const crossData = ref(null)
const examAId = ref(null)
const examBId = ref(null)
const distExamId = ref(null)
const distSubjectId = ref(null)
const topExamId = ref(null)
const distSeries = ref([])
const distMeta = ref(null)
const topSeries = ref([])

const typeLabel = computed(() => (typeId.value && TYPE_MAP[typeId.value]) ? TYPE_MAP[typeId.value] : '')
const subjectLatest = computed(() => subjectItems.value.length ? subjectItems.value[subjectItems.value.length - 1] : null)

const deltaRows = computed(() => {
  if (!crossData.value) return []
  const { a, b, delta } = crossData.value
  return crossData.value.subjects.map((s) => ({
    name: s.name,
    color: s.color,
    a: a.subjects[s.name],
    b: b.subjects[s.name],
    delta: delta[s.name],
  }))
})

async function loadClassesAndTypes() {
  const [cres, tres] = await Promise.all([http.get('/classes'), http.get('/exams/types')])
  classOptions.value = cres.items.map((c) => ({ label: c.name, value: c.id }))
  typeOptions.value = tres.items.map((t) => ({ label: t.label, value: t.value }))
  for (const t of tres.items) TYPE_MAP[t.value] = t.label
  if (classOptions.value.length) classId.value = classOptions.value[0].value
}

// 切班级：类型重置为该班场次最多的类型（避免默认混比所有类型）
async function onClassChange() {
  typeId.value = null
  await reload()
}

async function reload() {
  if (!classId.value) return
  // 全班考试（不限类型）：供 两场对比/分布/前十 自由选择场次
  const eres = await http.get('/exams', {
    params: { class_id: classId.value, per_page: 200 },
  })
  const items = [...eres.items].sort((x, y) => ((x.date || '9999') < (y.date || '9999') ? -1 : 1))
  allExamOptions.value = items.map((e) => ({
    label: `${TYPE_MAP[e.exam_type] || '考试'}·${e.name} ${e.date || ''}`,
    value: e.id,
  }))

  // 类型默认值：该班场次最多的类型（类型必选，杜绝默认混比）
  if (!typeId.value) {
    const count = {}
    for (const e of items) count[e.exam_type || 'other'] = (count[e.exam_type || 'other'] || 0) + 1
    const best = Object.entries(count).sort((a, b) => b[1] - a[1])[0]
    typeId.value = best ? best[0] : (typeOptions.value[0] && typeOptions.value[0].value)
  }

  const sres = await http.get('/subjects')
  subjectOptions.value = sres.items.map((s) => ({ label: s.name, value: s.id }))
  if (!subjectId.value && sres.items.length) subjectId.value = sres.items[0].id
  if (!distSubjectId.value && sres.items.length) distSubjectId.value = sres.items[0].id

  // 默认：分布/前十取最近一场；对比取最近两场
  const lastId = items.length ? items[items.length - 1].id : null
  distExamId.value = lastId
  topExamId.value = lastId
  examAId.value = items.length > 1 ? items[items.length - 2].id : null
  examBId.value = lastId

  await Promise.all([loadTrend(), loadSubjectTrend(), loadCross(), loadDist(), loadTop()])
}

async function loadTrend() {
  const r = await http.get('/analytics/exam-trend', {
    params: { class_id: classId.value, exam_type: typeId.value || undefined },
  })
  trendExams.value = r.exams
  trendSeries.value = r.series
}

async function loadSubjectTrend() {
  if (!subjectId.value) return
  const r = await http.get('/analytics/subject-trend', {
    params: { class_id: classId.value, subject_id: subjectId.value, exam_type: typeId.value || undefined },
  })
  subjectName.value = r.subject
  subjectFull.value = r.full
  subjectItems.value = r.items
}

async function loadCross() {
  if (!examAId.value || !examBId.value) {
    crossData.value = null
    return
  }
  try {
    crossData.value = await http.get('/analytics/cross-compare', {
      params: { class_id: classId.value, exam_a: examAId.value, exam_b: examBId.value },
    })
  } catch (e) {
    crossData.value = null
    message.error(e.message)
  }
}

async function loadDist() {
  if (!distExamId.value || !distSubjectId.value) return
  const r = await http.get('/analytics/score-distribution', {
    params: { exam_id: distExamId.value, subject_id: distSubjectId.value },
  })
  distSeries.value = r.distribution
  distMeta.value = { avg: r.avg, pass_rate: r.pass_rate, count: r.count }
}

async function loadTop() {
  if (!topExamId.value) return
  const r = await http.get('/analytics/top-students', {
    params: { class_id: classId.value, exam_id: topExamId.value, limit: 10 },
  })
  topSeries.value = r.items
}

// ---------- 图表配置 ----------
const trendOption = computed(() => ({
  color: CARTOON_COLORS,
  tooltip: baseTooltip({ valueFormatter: (v) => `${v} 分` }),
  legend: { bottom: 0, textStyle: { color: '#8a7a6b' } },
  grid: { top: 20, left: 40, right: 20, bottom: 46 },
  xAxis: { type: 'category', data: trendExams.value.map((e) => e.name), axisLabel: { color: '#8a7a6b' } },
  yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
  series: trendSeries.value.map((s) => ({
    name: s.name, type: 'line', data: s.values, smooth: true, symbolSize: 7,
    lineStyle: { width: 3 },
  })),
}))

const subjectOption = computed(() => {
  const it = subjectItems.value
  return {
    color: ['#ffb020', '#6c9ef5', '#22d3ee', '#ff8fab'],
    tooltip: baseTooltip({ trigger: 'axis' }),
    legend: { bottom: 0, textStyle: { color: '#8a7a6b' } },
    grid: { top: 20, left: 40, right: 44, bottom: 46 },
    xAxis: { type: 'category', data: it.map((i) => i.name), axisLabel: { color: '#8a7a6b' } },
    yAxis: [
      { type: 'value', name: '分', axisLabel: { color: '#8a7a6b' } },
      { type: 'value', name: '及格率%', min: 0, max: 100, axisLabel: { color: '#8a7a6b' }, splitLine: { show: false } },
    ],
    series: [
      { name: '最高', type: 'line', data: it.map((i) => i.max), smooth: true, lineStyle: { type: 'dashed', width: 2 } },
      { name: '平均', type: 'line', data: it.map((i) => i.avg), smooth: true, symbolSize: 8, lineStyle: { width: 4 },
        areaStyle: { opacity: 0.08 } },
      { name: '最低', type: 'line', data: it.map((i) => i.min), smooth: true, lineStyle: { type: 'dashed', width: 2 } },
      { name: '及格率', type: 'line', yAxisIndex: 1, data: it.map((i) => i.pass_rate), smooth: true,
        lineStyle: { width: 2, type: 'dotted' }, symbol: 'none' },
    ],
  }
})

const crossOption = computed(() => {
  const d = crossData.value
  if (!d) return {}
  const names = d.subjects.map((s) => s.name)
  return {
    color: ['#c0aa94', '#6c9ef5'],
    tooltip: baseTooltip({ axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${v} 分` }),
    legend: { bottom: 0, textStyle: { color: '#8a7a6b' } },
    grid: { top: 20, left: 40, right: 20, bottom: 46 },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    series: [
      { name: d.a.name, type: 'bar', data: names.map((n) => d.a.subjects[n]), barMaxWidth: 18, itemStyle: { borderRadius: [6, 6, 0, 0] } },
      { name: d.b.name, type: 'bar', data: names.map((n) => d.b.subjects[n]), barMaxWidth: 18, itemStyle: { borderRadius: [6, 6, 0, 0] } },
    ],
  }
})

const distOption = computed(() => ({
  tooltip: baseTooltip({ axisPointer: { type: 'shadow' } }),
  grid: { top: 15, left: 30, right: 15, bottom: 30 },
  xAxis: { type: 'category', data: distSeries.value.map((d) => d.range), axisLabel: { rotate: 30, color: '#8a7a6b', fontSize: 11 } },
  yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#8a7a6b' } },
  series: [{
    name: '人数', type: 'bar', data: distSeries.value.map((d) => d.count), barMaxWidth: 50,
    itemStyle: {
      borderRadius: [6, 6, 0, 0],
      color: (p) => (p.dataIndex < 2 ? '#ff6f6f' : p.dataIndex >= 4 ? '#34d399' : '#ffd166'),
    },
  }],
}))

const topOption = computed(() => {
  const rev = [...topSeries.value].reverse()
  return {
    tooltip: baseTooltip({ valueFormatter: (v) => `${v} 分` }),
    grid: { top: 12, left: 40, right: 50, bottom: 20 },
    xAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'category', data: rev.map((s) => s.name), axisLabel: { color: '#8a7a6b', fontWeight: 700 } },
    series: [{
      name: '总分', type: 'bar', data: rev.map((s) => s.total), barMaxWidth: 22,
      label: { show: true, position: 'right', color: '#8a7a6b', fontWeight: 700 },
      itemStyle: { borderRadius: [0, 8, 8, 0], color: (p) => (p.dataIndex >= rev.length - 3 ? '#ffb020' : '#6c9ef5') },
    }],
  }
})

onMounted(async () => {
  try {
    await loadClassesAndTypes()
    await reload()
  } catch (e) {
    message.error(e.message)
  }
})
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
  flex-wrap: wrap;
  gap: 10px;
}
.chart-card {
  background: #fff; border-radius: var(--radius-lg); padding: 16px 18px;
  border: 3px solid #fff; box-shadow: 0 6px 18px var(--c-shadow);
}
.chart-card h4 { margin: 0 0 10px; font-size: 15px; color: #4a4a55; }
.chart-card.wide h4 { margin-left: 2px; }
.tip { color: #b39b86; font-size: 12px; font-weight: 400; }
.vs { color: #ff6f6f; font-weight: 800; font-size: 13px; }
.chart-toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap; }
.chart-toolbar h4 { margin: 4px 0 0; font-size: 15px; }
.dist-meta { display: flex; gap: 16px; justify-content: center; color: #8a7a6b; font-size: 13px; margin-top: 4px; flex-wrap: wrap; }
.delta-list {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px; margin-top: 10px;
}
.delta-row {
  display: flex; align-items: center; gap: 8px;
  background: #fbf6f1; border-radius: 10px; padding: 6px 10px; font-size: 13px;
}
.d-name { color: #fff; border-radius: 999px; padding: 2px 9px; font-size: 12px; font-weight: 700; }
.d-val { flex: 1; color: #6b5d50; font-weight: 600; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
}
</style>
