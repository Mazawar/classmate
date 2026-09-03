<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">🚨 预警中心</h2>
        <p class="page-sub">自动找出需要重点关注的学生：成绩下滑、考勤异常，也不忘表扬进步之星</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classFilter" :options="classOptions" style="width: 150px" @update:value="load" />
        <n-select v-model:value="rankDrop" :options="rankOptions" style="width: 130px" @update:value="load" />
        <n-select v-model:value="attWindow" :options="windowOptions" style="width: 130px" @update:value="load" />
      </div>
    </div>

    <!-- 概览条 -->
    <div class="sum-bar pop-in">
      <div class="sum-item warn"><b>{{ data.attention_count || 0 }}</b><span>名学生需要关注</span></div>
      <div class="sum-item"><b>{{ (data.attention || []).length }}</b><span>成绩/综合预警</span></div>
      <div class="sum-item"><b>{{ (data.attendance_alerts || []).length }}</b><span>考勤异常</span></div>
      <div class="sum-item good"><b>{{ (data.rising || []).length }}</b><span>进步之星 🌟</span></div>
    </div>

    <!-- 重点关注 -->
    <h3 class="section-title">🎯 重点关注名单</h3>
    <div v-if="data.attention?.length" class="warn-grid">
      <div v-for="(w, i) in data.attention" :key="w.student_id" class="warn-card pop-in" :style="{ animationDelay: i * 0.03 + 's' }" @click="openPortrait(w.student_id)">
        <div class="wc-head">
          <div class="wc-avatar">{{ w.name.slice(0, 1) }}</div>
          <div class="wc-who">
            <div class="wc-name">{{ w.name }}</div>
            <div class="wc-class">{{ w.class_name }} · 现排名 #{{ w.latest_rank }}</div>
          </div>
          <n-tag :type="w.rank_drop >= rankDrop ? 'error' : 'warning'" size="small" round :bordered="false">
            {{ w.rank_drop >= rankDrop ? `↓${w.rank_drop} 名` : '考勤异常' }}
          </n-tag>
        </div>
        <div class="wc-reasons">
          <div v-for="r in w.reasons" :key="r" class="wc-reason">{{ r }}</div>
        </div>
      </div>
    </div>
    <div v-else class="empty-tip">🎉 暂无预警，同学们状态都不错！</div>

    <!-- 进步之星 -->
    <template v-if="data.rising?.length">
      <h3 class="section-title">🌟 进步之星</h3>
      <div class="rise-row">
        <div v-for="r in data.rising" :key="r.student_id" class="rise-card pop-in" @click="openPortrait(r.student_id)">
          <div class="rc-name">{{ r.name }}</div>
          <div class="rc-desc">#{{ r.from_rank }} → #{{ r.to_rank }}</div>
          <div class="rc-up">↑ {{ r.rank_gain }} 名</div>
        </div>
      </div>
    </template>

    <!-- 考勤异常明细 -->
    <template v-if="data.attendance_alerts?.length">
      <h3 class="section-title">📅 近 {{ data.window_days }} 天考勤异常</h3>
      <div class="att-card">
        <n-data-table :columns="attColumns" :data="data.attendance_alerts" :bordered="false" :pagination="false" size="small" />
      </div>
    </template>

    <student-portrait v-model:show="portraitShow" :student-id="portraitId" />
  </div>
</template>

<script setup>
import { h, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'
import StudentPortrait from '../components/StudentPortrait.vue'

const message = useMessage()
const classFilter = ref(0)
const classOptions = ref([{ label: '全部班级', value: 0 }])
const rankDrop = ref(5)
const attWindow = ref(30)
const rankOptions = [
  { label: '下滑≥3名', value: 3 },
  { label: '下滑≥5名', value: 5 },
  { label: '下滑≥10名', value: 10 },
]
const windowOptions = [
  { label: '近 14 天考勤', value: 14 },
  { label: '近 30 天考勤', value: 30 },
  { label: '近 60 天考勤', value: 60 },
]
const data = ref({})
const portraitShow = ref(false)
const portraitId = ref(null)

const attColumns = [
  { title: '姓名', key: 'name', width: 100, render: (r) => h('b', { style: 'cursor:pointer', onClick: () => openPortrait(r.student_id) }, r.name) },
  { title: '班级', key: 'class_name', width: 110 },
  { title: '缺勤', key: 'absent', width: 80, render: (r) => h('b', { style: 'color:#ef4444' }, r.absent + ' 次') },
  { title: '迟到', key: 'late', width: 80, render: (r) => h('b', { style: 'color:#ffb020' }, r.late + ' 次') },
  { title: '请假', key: 'leave', width: 80, render: (r) => r.leave + ' 次' },
  {
    title: '出勤率', key: 'rate', width: 160, render: (r) =>
      h('div', { style: 'display:flex;align-items:center;gap:8px' }, [
        h('div', { style: 'flex:1;height:8px;background:#f0e8dc;border-radius:6px;overflow:hidden' },
          h('div', { style: `width:${r.rate}%;height:100%;background:${r.rate >= 90 ? '#34d399' : r.rate >= 75 ? '#ffb020' : '#ef4444'};border-radius:6px` })),
        h('span', { style: 'font-weight:700;font-size:13px;color:#4a4a55' }, r.rate + '%'),
      ]),
  },
]

function openPortrait(id) {
  portraitId.value = id
  portraitShow.value = true
}

async function load() {
  try {
    data.value = await http.get('/warnings', {
      params: {
        class_id: classFilter.value || undefined,
        window_days: attWindow.value,
        rank_drop: rankDrop.value,
      },
    })
  } catch (e) {
    message.error(e.message)
  }
}

onMounted(async () => {
  try {
    const res = await http.get('/classes')
    classOptions.value = [
      { label: '全部班级', value: 0 },
      ...res.items.map((c) => ({ label: c.name, value: c.id })),
    ]
  } catch (_) { /* 保持全部班级 */ }
  load()
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
.sum-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.sum-item {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 14px;
  text-align: center;
  border: 3px solid #fff;
  box-shadow: 0 6px 18px var(--c-shadow);
  color: #8a7a6b;
  font-size: 13px;
}
.sum-item.warn { background: linear-gradient(135deg, #ffe3e3, #ffd1d1); color: #c0392b; }
.sum-item.good { background: linear-gradient(135deg, #d9f9e6, #c2f2d9); color: #1d8a56; }
.sum-item b { display: block; font-size: 26px; color: inherit; }
.section-title { margin-top: 26px; margin-bottom: 12px; }
.warn-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.warn-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 14px;
  border: 3px solid #fff;
  box-shadow: 0 6px 18px var(--c-shadow);
  cursor: pointer;
  transition: transform 0.15s;
}
.warn-card:hover { transform: translateY(-3px); border-color: #ffc9c9; }
.wc-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.wc-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #ff8fab, #ffb86b);
  color: #fff; display: grid; place-items: center; font-weight: 800; font-size: 18px;
}
.wc-who { flex: 1; min-width: 0; }
.wc-name { font-weight: 800; color: #4a4a55; }
.wc-class { font-size: 12px; color: #b39b86; }
.wc-reason { font-size: 12.5px; color: #8a7a6b; background: #fdf4ec; border-radius: 8px; padding: 4px 8px; margin-top: 4px; }
.empty-tip { background: #fff; border-radius: var(--radius-lg); padding: 24px; text-align: center; color: #8a7a6b; border: 3px solid #fff; box-shadow: 0 6px 18px var(--c-shadow); }
.rise-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
.rise-card {
  background: linear-gradient(135deg, #e8fbf1, #d6f5e5);
  border-radius: var(--radius-lg);
  padding: 14px;
  text-align: center;
  cursor: pointer;
  border: 3px solid #fff;
  box-shadow: 0 6px 18px var(--c-shadow);
  transition: transform 0.15s;
}
.rise-card:hover { transform: translateY(-3px); }
.rc-name { font-weight: 800; color: #1d8a56; }
.rc-desc { font-size: 12px; color: #5aa981; margin: 2px 0; }
.rc-up { font-weight: 800; color: #16a34a; }
.att-card { background: #fff; border-radius: var(--radius-lg); padding: 12px; border: 3px solid #fff; box-shadow: 0 6px 18px var(--c-shadow); }
@media (max-width: 640px) {
  .sum-bar { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
</style>
