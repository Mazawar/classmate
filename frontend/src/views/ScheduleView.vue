<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📋 班级课程表</h2>
        <p class="page-sub">维护每周课程安排</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classId" placeholder="选择班级" :options="classOptions" clearable @update:value="load" style="width: 160px" />
        <n-button type="primary" @click="openCreate">＋ 添加课程</n-button>
      </div>
    </div>

    <!-- 课程表网格 -->
    <div v-if="classId" class="schedule-wrap">
      <table class="schedule-table">
        <thead>
          <tr>
            <th class="corner">节次</th>
            <th v-for="(d, i) in weekdayNames" :key="i">{{ d }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in maxPeriod" :key="p">
            <td class="period"><span>{{ p }}</span><small>节</small></td>
            <td v-for="d in 7" :key="d" class="sched-cell" @click="editCell(d, p)">
              <div v-if="cellAt(d, p)" class="sched-subject" :style="{ background: cellAt(d, p).subject_color || '#6c9ef5' }">
                <div class="sub-name">{{ cellAt(d, p).subject_name }}</div>
                <div v-if="cellAt(d, p).teacher" class="sub-teacher">{{ cellAt(d, p).teacher }}</div>
              </div>
              <div v-else class="sched-empty">＋</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <n-empty v-else description="请先选择一个班级" style="margin-top: 60px" />

    <!-- 添加/编辑课程 -->
    <n-modal v-model:show="modalShow" preset="card" :title="editing ? '编辑课程' : '添加课程'" style="max-width: 420px">
      <n-form label-placement="top">
        <n-form-item label="星期 · 节次">
          <n-tag round size="large">{{ weekdayNames[form.weekday - 1] }} · 第 {{ form.period }} 节</n-tag>
        </n-form-item>
        <n-form-item label="科目">
          <n-select v-model:value="form.subject_id" :options="subjectOptions" filterable placeholder="选择科目" />
        </n-form-item>
        <n-form-item label="任课老师">
          <n-input v-model:value="form.teacher" placeholder="老师姓名" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display: flex; justify-content: space-between; gap: 10px">
          <n-button v-if="editing" type="error" secondary @click="removeEditing">删除此课</n-button>
          <div style="display: flex; gap: 10px; margin-left: auto">
            <n-button @click="modalShow = false">取消</n-button>
            <n-button type="primary" :loading="saving" @click="save">保存</n-button>
          </div>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'

const message = useMessage()
const classId = ref(null)
const classOptions = ref([])
const subjectOptions = ref([])
const grid = ref([])
const maxPeriod = ref(0)
const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const weekdayOptions = weekdayNames.map((n, i) => ({ label: n, value: i + 1 }))

const modalShow = ref(false)
const editing = ref(null)
const saving = ref(false)
const form = reactive({ weekday: 1, period: 1, subject_id: null, teacher: '' })

async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  if (res.items.length && !classId.value) {
    classId.value = res.items[0].id
    load()
  }
}
async function loadSubjects() {
  const res = await http.get('/subjects')
  subjectOptions.value = res.items.map((s) => ({ label: s.name, value: s.id }))
}
function cellAt(d, p) {
  const row = grid.value[p - 1]
  return row ? row[d - 1] : null
}
async function load() {
  if (!classId.value) return
  try {
    const res = await http.get('/schedule', { params: { class_id: classId.value } })
    grid.value = res.grid || []
    maxPeriod.value = res.max_period || 0
  } catch (e) {
    message.error(e.message)
  }
}
function openCreate() {
  editing.value = null
  Object.assign(form, { weekday: 1, period: maxPeriod.value + 1, subject_id: null, teacher: '' })
  modalShow.value = true
}
function editCell(d, p) {
  const item = cellAt(d, p)
  editing.value = item
  if (item) {
    Object.assign(form, { weekday: d, period: p, subject_id: item.subject_id, teacher: item.teacher || '' })
  } else {
    Object.assign(form, { weekday: d, period: p, subject_id: null, teacher: '' })
  }
  modalShow.value = true
}
async function save() {
  if (!form.subject_id) {
    message.warning('请选择科目')
    return
  }
  saving.value = true
  try {
    const payload = { subject_id: form.subject_id, teacher: form.teacher }
    if (editing.value && editing.value.id) {
      await http.put(`/schedule/${editing.value.id}`, payload)
      message.success('已更新')
    } else {
      await http.post('/schedule', { class_id: classId.value, weekday: form.weekday, period: form.period, ...payload })
      message.success('已添加')
    }
    modalShow.value = false
    load()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}
async function removeEditing() {
  try {
    await http.delete(`/schedule/${editing.value.id}`)
    message.success('已删除')
    modalShow.value = false
    load()
  } catch (e) {
    message.error(e.message)
  }
}

onMounted(() => {
  loadClasses()
  loadSubjects()
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
.schedule-wrap {
  overflow-x: auto;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: 0 6px 18px var(--c-shadow);
  border: 3px solid #fff;
}
.schedule-table {
  border-collapse: separate;
  border-spacing: 6px;
  width: 100%;
  min-width: 700px;
}
.schedule-table th, .schedule-table td {
  border-radius: 12px;
  text-align: center;
  padding: 6px;
}
.schedule-table thead th {
  background: linear-gradient(135deg, #ffb86b, #ff8fab);
  color: #fff;
  font-weight: 800;
  padding: 10px 4px;
}
.schedule-table .corner { background: #fff3e6 !important; color: #ff9d4d !important; }
.schedule-table .period {
  background: #eef4ff;
  color: var(--c-primary);
  font-weight: 800;
  width: 52px;
  font-size: 16px;
}
.schedule-table .period small { font-size: 10px; color: #a9c0f0; }
.sched-cell { cursor: pointer; min-height: 52px; vertical-align: top; }
.sched-cell:hover { background: #f6f3ff; }
.sched-subject {
  color: #fff;
  border-radius: 10px;
  padding: 6px 4px;
  min-height: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.sub-name { font-weight: 800; font-size: 13px; }
.sub-teacher { font-size: 10px; opacity: 0.85; }
.sched-empty { color: #e6d9cc; font-size: 20px; }
</style>
