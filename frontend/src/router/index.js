import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '首页' } },
      { path: 'warnings', name: 'warnings', component: () => import('../views/WarningsView.vue'), meta: { title: '预警中心' } },
      { path: 'analytics', name: 'analytics', component: () => import('../views/AnalyticsView.vue'), meta: { title: '数据分析' } },
      { path: 'students', name: 'students', component: () => import('../views/StudentsView.vue'), meta: { title: '学生档案' } },
      { path: 'classes', name: 'classes', component: () => import('../views/ClassesView.vue'), meta: { title: '班级管理' } },
      { path: 'subjects', name: 'subjects', component: () => import('../views/SubjectsView.vue'), meta: { title: '科目管理' } },
      { path: 'cadres', name: 'cadres', component: () => import('../views/CadresView.vue'), meta: { title: '班干部' } },
      { path: 'seats', name: 'seats', component: () => import('../views/SeatsView.vue'), meta: { title: '座位表' } },
      { path: 'schedule', name: 'schedule', component: () => import('../views/ScheduleView.vue'), meta: { title: '课程表' } },
      { path: 'exams', name: 'exams', component: () => import('../views/ExamsView.vue'), meta: { title: '成绩管理' } },
      { path: 'attendance', name: 'attendance', component: () => import('../views/AttendanceView.vue'), meta: { title: '考勤打卡' } },
      { path: 'contacts', name: 'contacts', component: () => import('../views/ContactsView.vue'), meta: { title: '家长通讯录' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 登录守卫：未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
