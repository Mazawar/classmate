<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">✅ 考勤打卡</h2>
        <p class="page-sub">按日登记全班出勤情况</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classFilter" placeholder="班级" :options="classOptions" clearable @update:value="loadDay" style="width: 140px" />
        <n-date-picker v-model:value="dateTs" type="date" clearable @update:value="loadDay" style="width: 150px" />
      </div>
    </div>

    <!-- 今日统计 -->
    <div class="att-stats">
      <div class="att-stat" style="background: linear-gradient(135deg,#6ee7b7,#34d399)">
        <b>{{ day.present }}</b><span>出勤</span>
      </div>
      <div class="att-stat" style="background: linear-gradient(135deg,#ffd166,#ffb020)">
        <b>{{ day.late }}</b><span>迟到</span>
      </div>
      <div class="att-stat" style="background: linear-gradient(135deg,#ff6f6f,#ef4444)">
        <b>{{ day.absent }}</b><span>缺勤</span>
      </div>
      <div class="att-stat" style="background: linear-gradient(135deg,#a78bfa,#8b5cf6)">
        <b>{{ day.leave }}</b><span>请假</span>
      </div>
    </div>

    <!-- 批量操作条 -->
    <div class="batch-bar">
      <n-button size="small" secondary @click="allPresent">✅ 一键全勤</n-button>
      <span class="batch-divider"></span>
      <span class="batch-label">选中 {{ checkedKeys.length }} 人，标记为：</span>
      <n-button size="small" secondary type="warning" :disabled="!checkedKeys.length" @click="batchMark('late')">迟到</n-button>
      <n-button size="small" secondary type="error" :disabled="!checkedKeys.length" @click="batchMark('absent')">缺勤</n-button>
      <n-button size="small" secondary type="primary" :disabled="!checkedKeys.length" @click="batchMark('leave')">请假</n-button>
      <div style="flex: 1"></div>
      <n-button size="small" type="info" secondary @click="openPicker">🎯 随机点名</n-button>
    </div>

    <!-- 打卡表格 -->
    <div class="att-table cartoon-card pop-in">
      <n-data-table
        :columns="attColumns"
        :data="day.records"
        :row-key="(r) => r.student_id"
        v-model:checked-row-keys="checkedKeys"
        :bordered="false"
        :pagination="false"
        size="small"
      />
      <div class="att-footer">
        <n-button type="primary" :loading="saving" @click="saveDay">💾 保存当日考勤</n-button>
        <span class="att-tip">共 {{ day.total }} 人 · 未标记状态将视为「出勤」</span>
      </div>
    </div>

    <!-- 随机点名 -->
    <n-modal v-model:show="pickerShow" :mask-closable="true" transform-origin="center">
      <div class="picker-card">
        <div class="picker-title">🎯 随机点名</div>
        <div class="picker-stage" :class="{ rolling: picking }">
          <div class="picker-name">{{ picking ? rollName : (pickedName || '准备好了吗？') }}</div>
          <div v-if="!picking && pickedName" class="picker-fire">🎉</div>
        </div>
        <div class="picker-actions">
          <n-button secondary @click="pickerShow = false">关闭</n-button>
          <n-button type="primary" :loading="picking" @click="roll">{{ pickedName ? '再来一次' : '开始点名' }}</n-button>
        </div>
      </div>
    </n-modal>

    <!-- 近 30 天趋势 -->
    <h3 class="section-title">📅 近 30 天考勤趋势</h3>
    <div class="trend-list">
      <div v-for="d in trendDays" :key="d.date" class="trend-row">
        <span class="trend-date">{{ d.date.slice(5) }}</span>
        <div class="trend-bar">
          <div class="bar-late" :style="{ width: barW(d.late) }" :title="`迟到 ${d.late}`"></div>
          <div class="bar-absent" :style="{ width: barW(d.absent) }" :title="`缺勤 ${d.absent}`"></div>
          <div class="bar-leave" :style="{ width: barW(d.leave) }" :title="`请假 ${d.leave}`"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, onBeforeUnmount, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'

const message = useMessage()
const classFilter = ref(null)
const classOptions = ref([])
const dateTs = ref(Date.now())
const day = ref({ total: 0, present: 0, late: 0, absent: 0, leave: 0, records: [] })
const saving = ref(false)
const trendDays = ref([])
const checkedKeys = ref([])
const pickerShow = ref(false)
const picking = ref(false)
const rollName = ref('')
const pickedName = ref('')
let rollTimer = null

const STATUS = {
  present: { label: '出勤', color: '#34d399' },
  late: { label: '迟到', color: '#ffb020' },
  absent: { label: '缺勤', color: '#ef4444' },
  leave: { label: '请假', color: '#8b5cf6' },
}

const attColumns = [
  { type: 'selection' },
  { title: '姓名', key: 'student_name', width: 110, render: (r) => h('b', {}, r.student_name) },
  {
    title: '考勤状态',
    key: 'status',
    render: (r) =>
      h('div', { style: 'display:flex;gap:6px;flex-wrap:wrap' }, Object.entries(STATUS).map(([key, opt]) =>
        h('button', {
          class: 'status-btn' + (r.status === key ? ' on' : ''),
          style: r.status === key ? `background:${opt.color};border-color:${opt.color};color:#fff` : '',
          onClick: () => setStatus(r, key),
        }, opt.label)
      )),
  },
]

function setStatus(r, status) {
  r.status = status
}

// ---- 批量操作 ----
async function allPresent() {
  day.value.records.forEach((r) => (r.status = 'present'))
  await saveDay(true)
}
async function batchMark(status) {
  const set = new Set(checkedKeys.value)
  day.value.records.forEach((r) => {
    if (set.has(r.student_id)) r.status = status
  })
  await saveDay(true)
  checkedKeys.value = []
}

// ---- 随机点名 ----
function openPicker() {
  pickedName.value = ''
  pickerShow.value = true
}
function roll() {
  const names = day.value.records.map((r) => r.student_name)
  if (!names.length) return
  picking.value = true
  const t0 = Date.now()
  rollTimer = setInterval(() => {
    rollName.value = names[Math.floor(Math.random() * names.length)]
    if (Date.now() - t0 > 1500) {
      clearInterval(rollTimer)
      picking.value = false
      pickedName.value = names[Math.floor(Math.random() * names.length)]
    }
  }, 70)
}
function dateStr() {
  return new Date(dateTs.value).toISOString().slice(0, 10)
}
function barW(n) {
  return Math.min(100, n * 12) + '%'
}
async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  if (res.items.length && !classFilter.value) {
    classFilter.value = res.items[0].id
    loadDay()
  }
}
async function loadDay() {
  if (!classFilter.value) return
  try {
    const res = await http.get('/attendance/day', {
      params: { class_id: classFilter.value, date_str: dateStr() },
    })
    day.value = res
  } catch (e) {
    message.error(e.message)
  }
}
async function loadTrend() {
  const res = await http.get('/attendance/summary')
  trendDays.value = res.days || []
}
async function saveDay() {
  saving.value = true
  const records = day.value.records.map((r) => ({ student_id: r.student_id, status: r.status, note: r.note }))
  try {
    await http.put('/attendance', { date: dateStr(), records })
    message.success('考勤已保存')
    loadDay()
    loadTrend()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadClasses()
  loadDay()
  loadTrend()
})
onBeforeUnmount(() => rollTimer && clearInterval(rollTimer))
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}
.att-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
.att-stat {
  color: #fff;
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  border: 3px solid #fff;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.att-stat b { font-size: 28px; }
.att-stat span { opacity: 0.9; font-size: 14px; }
.att-footer { display: flex; align-items: center; gap: 14px; margin-top: 14px; flex-wrap: wrap; }
.att-tip { color: #b39b86; font-size: 13px; }
.section-title { margin-top: 26px; margin-bottom: 10px; }
.trend-list { background: #fff; border-radius: var(--radius-lg); padding: 16px; border: 3px solid #fff; box-shadow: 0 4px 12px var(--c-shadow); }
.trend-row { display: flex; align-items: center; gap: 12px; padding: 5px 0; }
.trend-date { width: 44px; font-size: 12px; color: #8a7a6b; font-weight: 700; }
.trend-bar { flex: 1; height: 16px; background: #eef2f7; border-radius: 8px; display: flex; overflow: hidden; gap: 2px; }
.bar-late { background: #ffb020; height: 100%; border-radius: 4px; min-width: 2px; }
.bar-absent { background: #ef4444; height: 100%; border-radius: 4px; min-width: 2px; }
.bar-leave { background: #8b5cf6; height: 100%; border-radius: 4px; min-width: 2px; }
@media (max-width: 640px) {
  .att-stats { grid-template-columns: repeat(2, 1fr); }
}
.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: #fff;
  border: 3px solid #fff;
  border-radius: 16px;
  padding: 8px 12px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px var(--c-shadow);
}
.batch-divider { width: 1px; height: 18px; background: #eee2d4; margin: 0 4px; }
.batch-label { font-size: 13px; color: #8a7a6b; font-weight: 600; }
.picker-card {
  background: #fff;
  border-radius: 24px;
  border: 3px solid #fff;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
  padding: 22px;
  width: min(90vw, 360px);
  text-align: center;
}
.picker-title { font-weight: 800; font-size: 16px; color: #4a4a55; margin-bottom: 14px; }
.picker-stage {
  min-height: 110px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f2f7ff, #fdf1f6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px;
}
.picker-name { font-size: 30px; font-weight: 800; color: #4a7fd8; }
.picker-stage.rolling .picker-name { color: #b39b86; animation: roll-blink 0.12s infinite alternate; }
@keyframes roll-blink { from { opacity: 0.55; } to { opacity: 1; } }
.picker-fire { font-size: 22px; }
.picker-actions { display: flex; justify-content: center; gap: 10px; margin-top: 16px; }
</style>
