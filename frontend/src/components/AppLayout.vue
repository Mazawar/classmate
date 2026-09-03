<template>
  <div class="layout">
    <!-- 侧边导航（桌面） / 底部导航（移动） -->
    <aside class="sidebar">
      <div class="logo" @click="$router.push('/dashboard')">
        <span class="logo-emoji">🎒</span>
        <div>
          <div class="logo-name">ClassMate</div>
          <div class="logo-sub">班主任减负小助手</div>
        </div>
      </div>

      <nav class="menu">
        <template v-for="group in navGroups" :key="group.label">
          <div v-if="group.label" class="menu-group">{{ group.label }}</div>
          <div
            v-for="item in group.items"
            :key="item.path"
            class="menu-item"
            :class="{ active: isActive(item) }"
            @click="$router.push(item.path)"
          >
            <span class="menu-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </div>
        </template>
      </nav>

      <div class="user-box">
        <div class="avatar">{{ avatarChar }}</div>
        <div>
          <div class="nickname">{{ auth.user?.nickname || auth.user?.username || '用户' }}</div>
          <div class="role">👑 管理员</div>
        </div>
        <div class="logout" title="退出" @click="handleLogout">🚪</div>
      </div>
    </aside>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const navGroups = [
  {
    label: '',
    items: [
      { path: '/dashboard', label: '首页概览', icon: '🏠' },
      { path: '/warnings', label: '预警中心', icon: '🚨' },
      { path: '/analytics', label: '数据分析', icon: '📊' },
    ],
  },
  {
    label: '班级管理',
    items: [
      { path: '/classes', label: '班级信息', icon: '🏫' },
      { path: '/schedule', label: '课程表', icon: '📋' },
      { path: '/seats', label: '座位表', icon: '💺' },
      { path: '/cadres', label: '班干部', icon: '👔' },
      { path: '/subjects', label: '科目管理', icon: '📚' },
    ],
  },
  {
    label: '学生数据',
    items: [
      { path: '/students', label: '学生档案', icon: '🧑‍🎓' },
      { path: '/attendance', label: '考勤打卡', icon: '✅' },
      { path: '/exams', label: '成绩管理', icon: '📈' },
      { path: '/contacts', label: '家长通讯录', icon: '📞' },
    ],
  },
]

function isActive(item) {
  return route.path === item.path
}

const avatarChar = computed(() => {
  const name = auth.user?.nickname || auth.user?.username || '?'
  return name.slice(0, 1)
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 */
.sidebar {
  width: 230px;
  background: linear-gradient(180deg, #fffdfa, #fdf1e3);
  border-right: 3px solid #fff;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  padding: 22px 14px;
  position: sticky;
  top: 0;
  height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px 20px;
  cursor: pointer;
}
.logo-emoji {
  font-size: 34px;
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ffe29a, #ffb86b);
  border-radius: 18px;
  box-shadow: 0 5px 0 rgba(255, 158, 77, 0.3);
}
.logo-name {
  font-size: 20px;
  font-weight: 800;
  color: #3b3b47;
}
.logo-sub {
  font-size: 11px;
  color: #b39b86;
}

.menu {
  flex: 1;
  margin-top: 8px;
}
.menu-group {
  font-size: 11px;
  color: #b39b86;
  padding: 12px 16px 4px;
  font-weight: 700;
  letter-spacing: 1px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 16px;
  border-radius: 16px;
  margin-bottom: 4px;
  cursor: pointer;
  font-weight: 600;
  color: #6b5d50;
  transition: all 0.15s;
}
.menu-item:hover { background: rgba(108, 158, 245, 0.1); }
.menu-item.active {
  background: linear-gradient(135deg, #6c9ef5, #4a7fd8);
  color: #fff;
  box-shadow: 0 5px 12px rgba(74, 127, 216, 0.35);
}
.menu-icon { font-size: 20px; }

.user-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border-radius: 18px;
  padding: 10px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #6c9ef5);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
}
.nickname { font-size: 14px; font-weight: 700; }
.role { font-size: 11px; color: #b39b86; }
.logout {
  margin-left: auto;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.6;
}
.logout:hover { opacity: 1; }

.content {
  flex: 1;
  min-width: 0;
  background: var(--c-bg);
}

/* 移动端：侧栏变顶部 + 底部 TabBar */
@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .sidebar {
    width: 100%;
    height: auto;
    position: sticky;
    top: 0;
    z-index: 50;
    flex-direction: row;
    align-items: center;
    padding: 10px 14px;
    border-right: none;
    border-bottom: 3px solid #fff;
  }
  .logo { padding: 0; }
  .logo-sub, .user-box, .menu-group, .menu-item:not(.active) { display: none; }
  .menu {
    display: flex;
    flex: 0;
    margin: 0 0 0 auto;
    gap: 6px;
  }
  .menu-item { padding: 8px 14px; margin: 0; }
  .menu-item.active { display: flex; }
  .content { padding-bottom: 0; }
}
@media (max-width: 640px) {
  .menu-item { font-size: 0; gap: 0; padding: 8px 12px; }
  .menu-icon { font-size: 22px; }
}
</style>
