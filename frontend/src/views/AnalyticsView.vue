<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📊 数据分析</h2>
        <p class="page-sub">用图表直观掌握教学与班级情况</p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <n-select v-model:value="classId" placeholder="全部班级/选择班级" :options="classOptions" clearable @update:value="onClassChange" style="width:180px" />
      </div>
    </div>

    <!-- 概览图表 -->
    <div class="chart-grid">
      <div class="chart-card">
        <h4>🏫 各班级男女构成</h4>
        <v-chart :option="genderOption" height="280px" />
      </div>
      <div class="chart-card">
        <h4>🏅 {{ examTrendName }} 各科平均对比</h4>
        <v-chart :option="avgCompareOption" height="280px" />
      </div>
    </div>

    <!-- 历次考试趋势 -->
    <div class="chart-card wide">
      <h4>📈 历次考试主科平均分趋势</h4>
      <v-chart :option="examTrendOption" height="320px" />
    </div>

    <!-- 单科分布 + 前十 -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-toolbar">
          <h4 style="flex:1">🎯 成绩分布</h4>
          <n-select v-model:value="distExamId" :options="examOptions" size="small" style="width:130px" @update:value="onDistChange" />
          <n-select v-model:value="distSubjectId" :options="subjectOptions" size="small" style="width:100px" @update:value="onDistChange" />
        </div>
        <v-chart :option="distOption" height="280px" />
        <div class="dist-meta" v-if="distMeta">
          <span>平均 {{ distMeta.avg }}</span>
          <span>及格率 {{ distMeta.pass_rate }}%</span>
          <span>参考 {{ distMeta.count }} 人</span>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-toolbar">
          <h4 style="flex:1">🥇 班级总分前十</h4>
          <n-select v-model:value="topExamId" :options="examOptions" size="small" style="width:130px" @update:value="loadTop" />
        </div>
        <v-chart :option="topOption" height="280px" />
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
const overview = ref([])

const examOptions = ref([])
const subjectOptions = ref([])
const distExamId = ref(null)
const distSubjectId = ref(null)
const topExamId = ref(null)
const distMeta = ref(null)

const allExamsForClass = ref([])

const genderSeries = ref([])
const avgCompareSeries = ref([])
const examTrendSeries = ref([])
const trendExams = ref([])
const distSeries = ref([])
const topSeries = ref([])

async function loadClassesAndExams() {
  const cres = await http.get('/classes')
  classOptions.value = cres.items.map((c) => ({ label: c.name, value: c.id }))
}

async function ensureExamsForClass() {
  if (!classId.value) {
    allExamsForClass.value = []
    return
  }
  const eres = await http.get('/exams', { params: { class_id: classId.value, per_page: 100 } })
  allExamsForClass.value = eres.items
  examOptions.value = eres.items.map((e) => ({ label: e.name, value: e.id }))
  const sres = await http.get('/subjects')
  subjectOptions.value = sres.items.map((s) => ({ label: s.name, value: s.id }))
  if (!distExamId.value && eres.items.length) distExamId.value = eres.items[0].id
  if (!topExamId.value && eres.items.length) topExamId.value = eres.items[0].id
  if (!distSubjectId.value && sres.items.length) distSubjectId.value = sres.items[0].id
  return eres
}

async function allLoad() {
  await ensureExamsForClass()
  const o = await http.get('/analytics/overview')
  overview.value = o.classes
  genderSeries.value = o.classes

  if (classId.value) {
    const trend = await http.get('/analytics/exam-trend', { params: { class_id: classId.value } })
    trendExams.value = trend.exams
    examTrendSeries.value = trend.series
    const last = allExamsForClass.value.length ? allExamsForClass.value[allExamsForClass.value.length - 1].id : null
    if (last) await loadCompare(last)
  }
  await loadDist()
  await loadTop()
}

async function onClassChange() {
  await allLoad()
}

async function loadCompare(examId) {
  const r = await http.get('/analytics/class-avg-compare', { params: { exam_id: examId } })
  avgCompareSeries.value = r.items
  examTrendName.value = r.exam_name
}

async function onDistChange() {
  await loadDist()
}

async function loadDist() {
  if (!distExamId.value || !distSubjectId.value) return
  const r = await http.get('/analytics/score-distribution', { params: { exam_id: distExamId.value, subject_id: distSubjectId.value } })
  distSeries.value = r.distribution
  distMeta.value = { avg: r.avg, pass_rate: r.pass_rate, count: r.count }
}

async function loadTop() {
  if (!topExamId.value) return
  const r = await http.get('/analytics/top-students', { params: { class_id: classId.value, exam_id: topExamId.value, limit: 10 } })
  topSeries.value = r.items
}

const examTrendName = ref('最近一次')

const genderOption = computed(() => ({
  color: CARTOON_COLORS,
  tooltip: baseTooltip({ axisPointer: { type: 'shadow' } }),
  legend: { data: ['男生', '女生'], bottom: 0, textStyle: { color: '#8a7a6b' } },
  grid: { top: 20, left: 30, right: 20, bottom: 50 },
  xAxis: { type: 'category', data: genderSeries.value.map((c) => c.name), axisLabel: { color: '#8a7a6b' } },
  yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#8a7a6b' } },
  series: [
    { name: '男生', type: 'bar', data: genderSeries.value.map((c) => c.male), barWidth: 18, itemStyle: { borderRadius: [6,6,0,0], color: '#6c9ef5' } },
    { name: '女生', type: 'bar', data: genderSeries.value.map((c) => c.female), barWidth: 18, itemStyle: { borderRadius: [6,6,0,0], color: '#ff8fab' } },
  ],
}))

const avgCompareOption = computed(() => {
  const names = avgCompareSeries.value.map((x) => x.name)
  const avgs = avgCompareSeries.value.map((x) => x.avg)
  return {
    color: CARTOON_COLORS,
    tooltip: baseTooltip({ axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${v} 分` }),
    grid: { top: 20, left: 30, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    series: [{
      name: '平均分',
      type: 'bar',
      data: avgs,
      barMaxWidth: 40,
      label: { show: true, position: 'top', color: '#8a7a6b', fontWeight: 700 },
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: (p) => avgCompareSeries.value[p.dataIndex]?.color || '#6c9ef5',
      },
    }],
  }
})

const examTrendOption = computed(() => ({
  color: [CARTOON_COLORS[0], CARTOON_COLORS[2], CARTOON_COLORS[3], CARTOON_COLORS[4]],
  tooltip: baseTooltip({ valueFormatter: (v) => `${v} 分` }),
  legend: { bottom: 0, textStyle: { color: '#8a7a6b' } },
  grid: { top: 30, left: 40, right: 20, bottom: 40 },
  xAxis: { type: 'category', data: trendExams.value.map((e) => e.name), axisLabel: { color: '#8a7a6b' } },
  yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
  series: examTrendSeries.value.map((s) => ({
    name: s.name,
    type: 'line',
    data: s.values,
    smooth: true,
    connectNulls: true,
    symbolSize: 8,
    lineStyle: { width: 3 },
    label: { show: true, fontSize: 12, color: '#c0aa94' },
  })),
}))

const distOption = computed(() => {
  const names = distSeries.value.map((d) => d.range)
  const vals = distSeries.value.map((d) => d.count)
  return {
    tooltip: baseTooltip({ axisPointer: { type: 'shadow' } }),
    grid: { top: 15, left: 30, right: 15, bottom: 30 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, color: '#8a7a6b', fontSize: 11 } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#8a7a6b' } },
    series: [{
      name: '人数',
      type: 'bar',
      data: vals,
      barMaxWidth: 50,
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: (p) => {
          const i = p.dataIndex
          return i < 2 ? '#ff6f6f' : i >= 4 ? '#34d399' : '#ffd166'
        },
      },
    }],
  }
})

const topOption = computed(() => {
  const revItems = [...topSeries.value].reverse() || []
  return {
    tooltip: baseTooltip({ axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${v} 分` }),
    grid: { top: 12, left: 40, right: 50, bottom: 20 },
    xAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'category', data: revItems.map((s, _i) => s.name), axisLabel: { color: '#8a7a6b', fontWeight: 700 }, inverse: true },
    series: [{
      name: '总分',
      type: 'bar',
      data: revItems.map((s) => s.total),
      barMaxWidth: 22,
      label: { show: true, position: 'right', color: '#8a7a6b', fontWeight: 700 },
      itemStyle: { borderRadius: [0, 8, 8, 0], color: (p) => (p.dataIndex >= (revItems.length - 3) ? '#ffb020' : '#6c9ef5') },
    }],
  }
})

onMounted(async () => {
  await loadClassesAndExams()
  if (classOptions.value.length) {
    classId.value = classOptions.value[0].value
    await allLoad()
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
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-card {
  background: #fff; border-radius: var(--radius-lg); padding: 16px 18px;
  border: 3px solid #fff; box-shadow: 0 6px 18px var(--c-shadow);
}
.chart-card h4 { margin: 0 0 10px; font-size: 15px; color: #4a4a55; }
.chart-card.wide { margin-bottom: 16px; }
.chart-card.wide h4 { margin-left: 6px; }
.dist-meta { display: flex; gap: 16px; justify-content: center; color: #8a7a6b; font-size: 13px; margin-top: 4px; }
.chart-toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; align-items: flex-start; }
.chart-toolbar h4 { margin: 4px 0 0; font-size: 15px; }
@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
}
</style>
