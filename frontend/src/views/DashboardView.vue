<template>
  <div class="page-wrap">
    <h2 class="page-title">👋 首页概览</h2>
    <p class="page-sub">亲爱的班主任，今天也要元气满满哦！{{ greeting }} · {{ today }}{{ weekday }}</p>

    <!-- 综合统计 -->
    <div class="stats">
      <div class="stat-card c-blue pop-in"><div class="stat-icon">👨‍🎓</div><div class="stat-num">{{ stats.total_students || 0 }}</div><div class="stat-label">学生总数</div></div>
      <div class="stat-card c-pink pop-in" style="animation-delay:.04s"><div class="stat-icon">🏫</div><div class="stat-num">{{ stats.total_classes || 0 }}</div><div class="stat-label">班级数量</div></div>
      <div class="stat-card c-mint pop-in" style="animation-delay:.08s"><div class="stat-icon">✅</div><div class="stat-num">{{ stats.attendance_today || 0 }}</div><div class="stat-label">今日考勤</div></div>
      <div class="stat-card c-lavender pop-in" style="animation-delay:.12s"><div class="stat-icon">📈</div><div class="stat-num">{{ stats.total_exams || 0 }}</div><div class="stat-label">考试场次</div></div>
    </div>

    <!-- 图表区 -->
    <div class="chart-row">
      <div class="chart-card">
        <h4>👦👧 学生性别构成</h4>
        <v-chart :option="genderPie" height="240px" v-if="genderPie.series?.[0]?.data?.length" />
        <n-empty v-else description="暂无数据" style="padding:40px 0" />
      </div>
      <div class="chart-card">
        <h4>🏫 各班级规模</h4>
        <v-chart :option="classBar" height="240px" v-if="classBar.xAxis?.data?.length" />
        <n-empty v-else description="暂无数据" style="padding:40px 0" />
      </div>
    </div>

    <!-- 最近一次考试各科平均 -->
    <div class="chart-card" style="margin-top:16px">
      <h4>🎯 {{ compareName }} 各科平均分对比 <span class="tip">（满分 100/120）</span></h4>
      <v-chart :option="compareOption" height="260px" v-if="compareItems.length" />
      <n-empty v-else description="暂无可对比考试" style="padding:40px 0" />
    </div>

    <!-- 快捷入口 -->
    <h3 style="margin-top: 24px">🚀 快捷入口</h3>
    <div class="quick-grid">
      <div class="quick-card" v-for="q in quickLinks" :key="q.path" @click="$router.push(q.path)">
        <div class="quick-emoji">{{ q.icon }}</div>
        <div class="quick-name">{{ q.name }}</div>
        <div class="quick-desc">{{ q.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import http from '../api/http'
import VChart, { CARTOON_COLORS, baseTooltip } from '../components/VChart'

const stats = ref({})
const genderData = ref([])
const classData = ref([])
const compareItems = ref([])
const compareName = ref('')

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，早点休息～'
  if (h < 12) return '早上好～'
  if (h < 18) return '下午好～'
  return '晚上好～'
})
const today = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
const weekday = new Date().toLocaleDateString('zh-CN', { weekday: 'long' })

const quickLinks = [
  { path: '/analytics', icon: '📊', name: '数据分析', desc: '成绩/考勤可视化分析' },
  { path: '/students', icon: '🧑‍🎓', name: '学生档案', desc: '管理学生信息、看画像' },
  { path: '/attendance', icon: '✅', name: '考勤打卡', desc: '每日出勤登记' },
  { path: '/exams', icon: '📈', name: '成绩管理', desc: '录入成绩、查看排名' },
  { path: '/schedule', icon: '📋', name: '课程表', desc: '课程安排' },
  { path: '/seats', icon: '💺', name: '座位表', desc: '可视化排座' },
]

const genderPie = computed(() => ({
  tooltip: baseTooltip({ trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' }),
  legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#8a7a6b' } },
  series: [{
    name: '性别',
    type: 'pie',
    radius: ['55%', '78%'],
    center: ['42%', '50%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
    label: { show: false },
    data: genderData.value,
  }],
}))

const classBar = computed(() => ({
  color: CARTOON_COLORS,
  tooltip: baseTooltip({ axisPointer: { type: 'shadow' } }),
  grid: { top: 20, left: 40, right: 20, bottom: 30 },
  xAxis: { type: 'category', data: classData.value.map((c) => c.name), axisLabel: { color: '#8a7a6b' } },
  yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#8a7a6b' } },
  series: [
    { name: '男生', type: 'bar', stack: 'a', data: classData.value.map((c) => c.male), itemStyle: { color: '#6c9ef5', borderRadius: [3, 3, 0, 0] } },
    { name: '女生', type: 'bar', stack: 'a', data: classData.value.map((c) => c.female), itemStyle: { color: '#ff8fab', borderRadius: [6, 6, 0, 0] } },
  ],
}))

const compareOption = computed(() => {
  const names = compareItems.value.map((c) => c.name)
  const avgs = compareItems.value.map((c) => c.avg)
  const colors = compareItems.value.map((c) => c.color || '#6c9ef5')
  return {
    tooltip: baseTooltip({ axisPointer: { type: 'shadow' }, valueFormatter: (v) => `${v} 分` }),
    grid: { top: 20, left: 40, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    series: [{
      name: '平均分',
      type: 'bar',
      data: avgs,
      barMaxWidth: 48,
      label: { show: true, position: 'top', color: '#8a7a6b', fontWeight: 700 },
      itemStyle: { borderRadius: [8, 8, 0, 0], color: (p) => colors[p.dataIndex] || '#6c9ef5' },
    }],
  }
})

async function loadAll() {
  stats.value = await http.get('/students/stats')
  // 性别
  const o = await http.get('/analytics/overview')
  const male = o.classes.reduce((s, c) => s + c.male, 0)
  const female = o.classes.reduce((s, c) => s + c.female, 0)
  genderData.value = [
    { name: '男生', value: male, itemStyle: { color: '#6c9ef5' } },
    { name: '女生', value: female, itemStyle: { color: '#ff8fab' } },
  ]
  classData.value = o.classes

  // 最近一次考试各科平均（默认第一个有考试的班；用 stats，取任意班级）
  const cres = await http.get('/classes')
  const cls = cres.items && cres.items.length ? cres.items[0] : null
  if (cls) {
    const eres = await http.get('/exams', { params: { class_id: cls.id, per_page: 100 } })
    if (eres.items && eres.items.length) {
      const last = eres.items[eres.items.length - 1]
      const cv = await http.get('/analytics/class-avg-compare', { params: { exam_id: last.id } })
      compareItems.value = cv.items
      compareName.value = `${cls.name} · ${cv.exam_name}`
    }
  }
}

onMounted(loadAll)
</script>

<style scoped>
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.stat-card { border-radius: var(--radius-lg); padding: 20px; color: #fff; display: flex; flex-direction: column; align-items: center; box-shadow: 0 8px 24px rgba(0,0,0,0.1); border: 3px solid #fff; }
.c-blue { background: linear-gradient(135deg,#6c9ef5,#4a7fd8); }
.c-pink { background: linear-gradient(135deg,#ff8fab,#ff6f91); }
.c-mint { background: linear-gradient(135deg,#6ee7b7,#34d399); }
.c-lavender { background: linear-gradient(135deg,#a78bfa,#8b5cf6); }
.stat-icon { font-size: 26px; }
.stat-num { font-size: 30px; font-weight: 800; margin: 4px 0; }
.stat-label { font-size: 13px; opacity: .95; }
.tip { color: #b39b86; font-size: 12px; font-weight: 400; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
.chart-card { background: #fff; border-radius: var(--radius-lg); padding: 16px 18px; border: 3px solid #fff; box-shadow: 0 6px 18px var(--c-shadow); }
.chart-card h4 { margin: 0 0 10px; font-size: 15px; color: #4a4a55; }
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 8px; }
.quick-card { background: #fff; border-radius: var(--radius-lg); padding: 16px; cursor: pointer; box-shadow: 0 6px 18px var(--c-shadow); border: 3px solid #fff; transition: transform .15s; text-align: center; }
.quick-card:hover { transform: translateY(-4px); }
.quick-emoji { font-size: 30px; }
.quick-name { font-weight: 800; font-size: 15px; margin: 4px 0; color: #4a4a55; }
.quick-desc { color: #a89485; font-size: 11px; }
@media (max-width: 640px) {
  .stats { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-num { font-size: 25px; }
  .chart-row { grid-template-columns: 1fr; }
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
