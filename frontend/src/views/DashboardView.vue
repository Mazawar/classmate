<template>
  <div class="page-wrap">
    <h2 class="page-title">👋 首页概览</h2>
    <p class="page-sub">亲爱的班主任，今天也要元气满满哦！{{ greeting }}</p>

    <!-- 综合统计 -->
    <div class="stats">
      <div class="stat-card c-blue pop-in"><div class="stat-icon">👨‍🎓</div><div class="stat-num">{{ stats.total_students || 0 }}</div><div class="stat-label">学生总数</div></div>
      <div class="stat-card c-pink pop-in" style="animation-delay:.04s"><div class="stat-icon">🏫</div><div class="stat-num">{{ stats.total_classes || 0 }}</div><div class="stat-label">班级数量</div></div>
      <div class="stat-card c-mint pop-in" style="animation-delay:.08s"><div class="stat-icon">✅</div><div class="stat-num">{{ stats.attendance_today || 0 }}</div><div class="stat-label">今日考勤</div></div>
      <div class="stat-card c-lavender pop-in" style="animation-delay:.12s"><div class="stat-icon">📈</div><div class="stat-num">{{ stats.total_exams || 0 }}</div><div class="stat-label">考试场次</div></div>
      <div class="stat-card c-orange pop-in" style="animation-delay:.16s"><div class="stat-icon">📚</div><div class="stat-num">{{ stats.total_subjects || 0 }}</div><div class="stat-label">开设科目</div></div>
      <div class="stat-card c-teal pop-in" style="animation-delay:.2s"><div class="stat-icon">👔</div><div class="stat-num">{{ stats.total_cadres || 0 }}</div><div class="stat-label">班干部</div></div>
    </div>

    <!-- 男女比例 -->
    <div class="gender-row">
      <div class="gender-box">
        <div class="gender-title">👦 男生</div>
        <div class="gender-ratio"><span :style="{ width: malePercent }" class="male-fill"></span></div>
        <div class="gender-num">{{ stats.male || 0 }} / {{ malePercent }}</div>
      </div>
      <div class="gender-box">
        <div class="gender-title">👧 女生</div>
        <div class="gender-ratio"><span :style="{ width: femalePercent }" class="female-fill"></span></div>
        <div class="gender-num">{{ stats.female || 0 }} / {{ femalePercent }}</div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <h3 style="margin-top: 28px">🚀 快捷入口</h3>
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

const stats = ref({})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，早点休息～'
  if (h < 12) return '早上好～'
  if (h < 18) return '下午好～'
  return '晚上好～'
})
const malePercent = computed(() => {
  const total = stats.value.male + stats.value.female
  return total ? Math.round((stats.value.male / total) * 100) + '%' : '0%'
})
const femalePercent = computed(() => {
  const total = stats.value.male + stats.value.female
  return total ? Math.round((stats.value.female / total) * 100) + '%' : '0%'
})
const quickLinks = [
  { path: '/students', icon: '🧑‍🎓', name: '学生档案', desc: '管理学生信息、家长电话' },
  { path: '/attendance', icon: '✅', name: '考勤打卡', desc: '每日出勤登记与统计' },
  { path: '/exams', icon: '📈', name: '成绩管理', desc: '录入成绩、查看排名' },
  { path: '/schedule', icon: '📋', name: '课程表', desc: '维护每周课程安排' },
  { path: '/seats', icon: '💺', name: '座位表', desc: '可视化排座' },
  { path: '/cadres', icon: '👔', name: '班干部', desc: '班委职务安排' },
]

onMounted(async () => {
  try {
    stats.value = await http.get('/students/stats')
  } catch (e) {
    /* 忽略 */ {}
  }
})
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.stat-card {
  border-radius: var(--radius-lg);
  padding: 20px;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border: 3px solid #fff;
}
.c-blue { background: linear-gradient(135deg, #6c9ef5, #4a7fd8); }
.c-pink { background: linear-gradient(135deg, #ff8fab, #ff6f91); }
.c-mint { background: linear-gradient(135deg, #6ee7b7, #34d399); }
.c-lavender { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
.c-orange { background: linear-gradient(135deg, #ffb86b, #ff9d4d); }
.c-teal { background: linear-gradient(135deg, #22d3ee, #0ea5e9); }
.stat-icon { font-size: 28px; }
.stat-num { font-size: 30px; font-weight: 800; margin: 4px 0; }
.stat-label { font-size: 13px; opacity: 0.95; }

.gender-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 20px; }
.gender-box { background: #fff; border-radius: var(--radius-lg); padding: 16px; border: 3px solid #fff; box-shadow: 0 4px 12px var(--c-shadow); }
.gender-title { font-weight: 800; margin-bottom: 10px; color: #4a4a55; }
.gender-ratio { height: 14px; background: #f0e8dc; border-radius: 8px; overflow: hidden; }
.male-fill { display: block; height: 100%; background: linear-gradient(90deg,#6c9ef5,#22d3ee); border-radius: 8px; transition: width .5s; }
.female-fill { display: block; height: 100%; background: linear-gradient(90deg,#ff8fab,#ff6f91); border-radius: 8px; transition: width .5s; }
.gender-num { color: #8a7a6b; font-size: 13px; margin-top: 6px; }

.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 8px; }
.quick-card { background: #fff; border-radius: var(--radius-lg); padding: 18px; cursor: pointer; box-shadow: 0 6px 18px var(--c-shadow); border: 3px solid #fff; transition: transform 0.15s, box-shadow 0.15s; }
.quick-card:hover { transform: translateY(-4px); box-shadow: 0 10px 28px var(--c-shadow); }
.quick-emoji { font-size: 32px; }
.quick-name { font-weight: 800; font-size: 16px; margin: 4px 0; }
.quick-desc { color: #a89485; font-size: 12px; }

@media (max-width: 640px) {
  .stats { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-num { font-size: 24px; }
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
