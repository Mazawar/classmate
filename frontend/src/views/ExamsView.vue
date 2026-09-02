<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📈 成绩管理</h2>
        <p class="page-sub">录入考试成绩，查看排名与科目统计</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classFilter" placeholder="班级" :options="classOptions" clearable @update:value="loadExams" style="width: 140px" />
        <n-button type="primary" @click="openCreateExam">＋ 新建考试</n-button>
      </div>
    </div>

    <!-- 考试列表 -->
    <div v-if="exams.length" class="exam-list">
      <div v-for="e in exams" :key="e.id" class="exam-card pop-in" :class="{ active: currentExam && currentExam.id === e.id }">
        <div class="exam-info" @click="loadSummary(e)">
          <div class="exam-name">{{ e.name }}</div>
          <div class="exam-meta">{{ e.date || '—' }} · {{ e.subject_count }} 科 · {{ e.student_count }} 人</div>
        </div>
        <div class="exam-actions">
          <n-button size="tiny" secondary @click.stop="openScoreEntry(e)">录入成绩</n-button>
          <n-button size="tiny" secondary @click.stop="openEditExam(e)">编辑</n-button>
          <n-button size="tiny" secondary type="error" @click.stop="removeExam(e)">删除</n-button>
        </div>
      </div>
    </div>
    <n-empty v-else description="还没有考试，新建一场吧" style="margin-top: 50px" />

    <!-- 成绩排名与统计 -->
    <template v-if="summary">
      <!-- 科目统计卡片 -->
      <div class="subj-stats">
        <div v-for="s in summary.subjects" :key="s.id" class="subj-stat">
          <div class="subj-name" :style="{ background: s.color }">{{ s.name }}</div>
          <div class="subj-row"><span>平均</span><b>{{ s.avg }}</b></div>
          <div class="subj-row"><span>最高</span><b style="color:#34d399">{{ s.max }}</b></div>
          <div class="subj-row"><span>最低</span><b style="color:#ff6f6f">{{ s.min }}</b></div>
          <div class="subj-row"><span>及格率</span><b style="color:var(--c-primary)">{{ s.pass_rate }}%</b></div>
          <div class="pass-bar"><div class="pass-fill" :style="{ width: s.pass_rate + '%', background: s.color }"></div></div>
        </div>
      </div>

      <!-- 排名表 -->
      <h3 class="section-title">🏆 成绩排名（{{ summary.exam_name }}）</h3>
      <n-data-table
        :columns="rankColumns"
        :data="summary.rows"
        :bordered="false"
        :pagination="false"
        :scroll-x="600"
        size="small"
      />
    </template>

    <!-- 考试 CRUD 弹窗 -->
    <n-modal v-model:show="examModal" preset="card" :title="examEditing ? '编辑考试' : '新建考试'" style="max-width: 420px">
      <n-form label-placement="top">
        <n-form-item label="考试名称 *">
          <n-input v-model:value="examForm.name" placeholder="如：期中考试、第一次月考" />
        </n-form-item>
        <n-form-item label="考试日期">
          <n-date-picker v-model:value="examDateTs" type="date" clearable style="width: 100%" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="examForm.remark" type="textarea" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px">
          <n-button @click="examModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="saveExam">保存</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 成绩录入弹窗 -->
    <n-modal v-model:show="scoreModal" preset="card" :title="`录入成绩：${scoreExam?.name || ''}`" style="max-width: 720px" :style="{ minWidth: '600px' }">
      <div class="score-entry">
        <n-data-table
          :columns="scoreCols"
          :data="scoreRows"
          :bordered="false"
          :pagination="false"
          :scroll-x="600"
          size="small"
        />
      </div>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px">
          <n-button @click="scoreModal = false">关闭</n-button>
          <n-button type="primary" :loading="saving" @click="saveScores">💾 保存成绩</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { h, onMounted, reactive, ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'

const message = useMessage()
const classFilter = ref(null)
const classOptions = ref([])
const exams = ref([])
const currentExam = ref(null)
const summary = ref(null)
const subjects = ref([])
const saving = ref(false)

// 考试 CRUD
const examModal = ref(false)
const examEditing = ref(null)
const examDateTs = ref(null)
const examForm = reactive({ name: '', remark: '' })

// 成绩录入
const scoreModal = ref(false)
const scoreExam = ref(null)
const scoreRows = ref([])

async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  if (res.items.length && !classFilter.value) {
    classFilter.value = res.items[0].id
    loadExams()
  }
}
async function loadSubjects() {
  const res = await http.get('/subjects')
  subjects.value = res.items
}
async function loadExams() {
  summary.value = null
  currentExam.value = null
  if (!classFilter.value) {
    exams.value = []
    return
  }
  const res = await http.get('/exams', { params: { class_id: classFilter.value } })
  exams.value = res.items
}
function onClassChange() {
  loadExams()
}
async function loadSummary(e) {
  currentExam.value = e
  const res = await http.get(`/exams/${e.id}/summary`)
  summary.value = res
}

// ---- 排名表列 ----
const rankColumns = computed(() => [
  { title: '排名', key: 'rank', width: 70, render: (r) => h('b', { style: `color:${r.rank <= 3 ? '#ff8fab' : '#4a4a55'}` }, `#${r.rank}`) },
  { title: '姓名', key: 'name', width: 90, render: (r) => h('b', {}, r.name) },
  { title: '学号', key: 'student_no', width: 100, render: (r) => r.student_no || '—' },
  ...subjects.value.map((s) => ({
    title: s.name,
    key: 'sub' + s.id,
    width: 70,
    render: (r) => {
      const v = r.subjects ? r.subjects[s.id] : undefined
      if (v === undefined || v === null) return h('span', { style: 'color:#ccc' }, '-')
      return h('span', { style: `color:${v < (s.full_score || 100) * 0.6 ? '#ff6f6f' : '#4a4a55'}` }, v)
    },
  })),
  { title: '总分', key: 'total', width: 75, sortable: true, render: (r) => h('b', { style: 'color:var(--c-primary)' }, r.total) },
  { title: '平均', key: 'average', width: 75, render: (r) => r.average },
])

// ---- 成绩录入 ----
const scoreCols = computed(() => [
  { title: '学生', key: 'name', width: 90, render: (r) => h('b', {}, r.name) },
  { title: '学号', key: 'student_no', width: 100 },
  ...subjects.value.map((s) => ({
    title: s.name,
    key: 's' + s.id,
    width: 90,
    render: (row) =>
      h('n-input-number', {
        value: row.s[s.id],
        min: 0,
        max: s.full_score || 100,
        size: 'small',
        placeholder: '-',
        'update:value': (v) => {
          row.s[s.id] = v
        },
        style: 'width:80px',
      }),
  })),
])

async function openScoreEntry(e) {
  scoreExam.value = e
  // 预填学生列表，若已有成绩则回填
  const stuRes = await http.get('/students', { params: { class_id: classFilter.value, per_page: 200 } })
  scoreRows.value = stuRes.items.map((st) => {
    const prev = {}
    if (summary.value && summary.value.exam_id === e.id) {
      const row = summary.value.rows.find((r) => r.student_id === st.id)
      if (row) {
        for (const [k, v] of Object.entries(row.subjects)) prev[k] = v
      }
    }
    return { ...st, s: prev }
  })
  scoreModal.value = true
}
async function saveScores() {
  saving.value = true
  const rows = []
  for (const row of scoreRows.value) {
    if (Object.keys(row.s).length) {
      rows.push({ student_id: row.id, scores: row.s })
    }
  }
  try {
    await http.post('/exams/score', { exam_id: scoreExam.value.id, class_id: classFilter.value, rows })
    message.success(`已保存 ${rows.length} 名学生成绩`)
    scoreModal.value = false
    if (summary.value) loadSummary(currentExam.value)
    loadExams()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

// ---- 考试 CRUD ----
function openCreateExam() {
  examEditing.value = null
  examDateTs.value = null
  Object.assign(examForm, { name: '', remark: '' })
  examModal.value = true
}
function openEditExam(e) {
  examEditing.value = e
  examDateTs.value = e.date ? new Date(e.date + 'T00:00:00').getTime() : null
  Object.assign(examForm, { name: e.name, remark: e.remark || '' })
  examModal.value = true
}
async function saveExam() {
  if (!examForm.name) {
    message.warning('请填写考试名称')
    return
  }
  saving.value = true
  try {
    const payload = { ...examForm, date: examDateTs.value ? new Date(examDateTs.value).toISOString().slice(0, 10) : null }
    if (examEditing.value) {
      await http.put(`/exams/${examEditing.value.id}`, payload)
      message.success('已更新')
    } else {
      await http.post('/exams', { ...payload, class_id: classFilter.value })
      message.success('已新建')
    }
    examModal.value = false
    loadExams()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}
async function removeExam(e) {
  message.warning(`确定删除考试「${e.name}」及所有成绩吗？`, { duration: 0, closable: true }, {
    onAction: async () => {
      try {
        await http.delete(`/exams/${e.id}`)
        message.success('已删除')
        if (currentExam.value?.id === e.id) summary.value = null
        loadExams()
      } catch (err) {
        message.error(err.message)
      }
    },
  })
}

onMounted(() => {
  loadClasses()
  loadSubjects()
  loadExams()
})
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
.exam-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; margin-bottom: 24px; }
.exam-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 6px 18px var(--c-shadow);
  border: 3px solid #fff;
}
.exam-card.active { border-color: var(--c-primary); }
.exam-info { cursor: pointer; }
.exam-name { font-weight: 800; font-size: 18px; color: #4a4a55; }
.exam-meta { color: #b39b86; font-size: 13px; margin-top: 2px; }
.exam-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.subj-stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; margin-bottom: 8px; }
.subj-stat {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 14px;
  box-shadow: 0 4px 12px var(--c-shadow);
  border: 3px solid #fff;
}
.subj-name {
  color: #fff;
  border-radius: 999px;
  padding: 4px 12px;
  display: inline-block;
  font-weight: 800;
  font-size: 14px;
  margin-bottom: 8px;
}
.subj-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 13px; color: #8a7a6b; }
.pass-bar { height: 6px; background: #f0e8dc; border-radius: 6px; margin-top: 6px; overflow: hidden; }
.pass-fill { height: 100%; border-radius: 6px; }
.section-title { margin-top: 24px; margin-bottom: 12px; }
.score-entry { overflow-x: auto; }
</style>
