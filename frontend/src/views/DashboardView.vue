<template>
  <div class="page-wrap">
    <h2 class="page-title">👋 首页概览</h2>
    <p class="page-sub">亲爱的班主任，今天也要元气满满哦！</p>

    <!-- 统计卡片 -->
    <div class="stats">
      <div class="stat-card c-blue pop-in">
        <div class="stat-icon">👨‍🎓</div>
        <div class="stat-num">{{ stats.total_students || 0 }}</div>
        <div class="stat-label">学生总数</div>
      </div>
      <div class="stat-card c-pink pop-in" style="animation-delay: 0.05s">
        <div class="stat-icon">🏫</div>
        <div class="stat-num">{{ stats.total_classes || 0 }}</div>
        <div class="stat-label">班级数量</div>
      </div>
      <div class="stat-card c-mint pop-in" style="animation-delay: 0.1s">
        <div class="stat-icon">👦</div>
        <div class="stat-num">{{ stats.male || 0 }}</div>
        <div class="stat-label">男生</div>
      </div>
      <div class="stat-card c-lavender pop-in" style="animation-delay: 0.15s">
        <div class="stat-icon">👧</div>
        <div class="stat-num">{{ stats.female || 0 }}</div>
        <div class="stat-label">女生</div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <h3 style="margin-top: 30px">🚀 快捷入口</h3>
    <div class="quick-grid">
      <div class="quick-card" @click="$router.push('/students')">
        <div class="quick-emoji">🧑‍🎓</div>
        <div class="quick-name">学生管理</div>
        <div class="quick-desc">增删查改学生档案、家长电话</div>
      </div>
      <div class="quick-card" @click="$router.push('/classes')">
        <div class="quick-emoji">🏫</div>
        <div class="quick-name">班级管理</div>
        <div class="quick-desc">维护班级信息与人数统计</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from '../api/http'

const stats = ref({})

onMounted(async () => {
  try {
    stats.value = await http.get('/students/stats')
  } catch (e) {
    /* 忽略，展示空统计 */
  }
})
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  border-radius: var(--radius-lg);
  padding: 22px;
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
.stat-icon { font-size: 30px; }
.stat-num { font-size: 34px; font-weight: 800; margin: 4px 0; }
.stat-label { font-size: 14px; opacity: 0.95; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 8px;
}
.quick-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 24px;
  cursor: pointer;
  box-shadow: 0 6px 18px var(--c-shadow);
  border: 3px solid #fff;
  transition: transform 0.15s, box-shadow 0.15s;
}
.quick-card:hover { transform: translateY(-4px); box-shadow: 0 10px 28px var(--c-shadow); }
.quick-emoji { font-size: 40px; }
.quick-name { font-weight: 800; font-size: 18px; margin: 6px 0; }
.quick-desc { color: #a89485; font-size: 13px; }

@media (max-width: 640px) {
  .stats { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-num { font-size: 26px; }
  .quick-grid { grid-template-columns: 1fr; }
}
</style>
