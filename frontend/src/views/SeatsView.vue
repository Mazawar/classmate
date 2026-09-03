<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">💺 座位表</h2>
        <p class="page-sub">可视化排座，点击座位为学生安排位置</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classId" placeholder="选择班级" :options="classOptions" clearable @update:value="loadSeats" style="width: 160px" />
        <n-button secondary @click="addRow">＋ 加一排</n-button>
        <n-input-number v-model:value="cols" :min="2" :max="12" style="width: 110px" placeholder="每排人数" />
        <n-button type="primary" :loading="saving" @click="save">💾 保存座位</n-button>
      </div>
    </div>

    <div class="seats-container">
      <div class="seats-inner">
        <!-- 讲台 -->
        <div class="podium">📺 讲台</div>

        <!-- 座位网格 -->
        <table class="seats-table carton">
          <tr v-for="(row, ri) in rows" :key="ri">
            <td class="row-label">第{{ ri + 1 }}排</td>
            <td v-for="col in cols" :key="col" class="seat-cell">
              <div
                class="seat"
                :class="{ occupied: seatAt(ri + 1, col).student_id }"
                @click="assignSeat(ri + 1, col)"
              >
                <template v-if="seatAt(ri + 1, col).student_id">
                  <span class="seat-name">{{ seatName(seatAt(ri + 1, col).student_id) }}</span>
                  <span class="seat-row">{{ seatAt(ri + 1, col).student_name }}</span>
                </template>
                <template v-else>
                  <span class="seat-empty">空</span>
                </template>
              </div>
            </td>
          </tr>
        </table>
      </div>
    </div>

    <!-- 学生选择弹窗 -->
    <n-modal v-model:show="assignShow" preset="card" :title="`第 ${assignTarget.row} 排 第 ${assignTarget.col} 列`" style="max-width: 360px">
      <n-select
        v-model:value="assignStudentId"
        placeholder="选择学生（可搜索）"
        filterable
        clearable
        :options="studentOptions"
      />
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px">
          <n-button @click="assignShow = false">取消</n-button>
          <n-button type="primary" @click="confirmAssign">确定安排</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'

const message = useMessage()
const classId = ref(null)
const classOptions = ref([])
const studentOptions = ref([])
const saving = ref(false)
const cols = ref(6)
const rows = ref([]) // 每行存 { row, cells: [{col, student_id, student_name}] }

const assignShow = ref(false)
const assignTarget = reactive({ row: 0, col: 0 })
const assignStudentId = ref(null)
const allStudents = ref([])

async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  if (res.items.length && !classId.value) {
    classId.value = res.items[0].id
    loadSeats()
  }
}
async function loadStudents() {
  if (!classId.value) return
  const res = await http.get('/students', { params: { class_id: classId.value, per_page: 200 } })
  allStudents.value = res.items
  studentOptions.value = res.items.map((s) => ({
    label: `${s.name}${s.seat ? ' · ' + s.seat : ''}${s.cadre ? ' ⭐' : ''}`,
    value: s.id,
  }))
}
function seatAt(row, col) {
  const r = rows.value.find((x) => x.row === row)
  if (!r) return {}
  return r.cells.find((c) => c.col === col) || {}
}
function seatName(id) {
  const s = allStudents.value.find((x) => x.id === id)
  return s ? s.name.slice(0, 2) : '?'
}
async function loadSeats() {
  loadStudents()
  if (!classId.value) {
    rows.value = []
    return
  }
  try {
    const res = await http.get('/seats', { params: { class_id: classId.value } })
    const seatMap = new Map()
    let maxRow = 0
    for (const s of res.items) {
      seatMap.set(`${s.row}-${s.col}`, s)
      maxRow = Math.max(maxRow, s.row)
    }
    rows.value = []
    for (let r = 1; r <= maxRow; r++) {
      const cells = []
      for (let c = 1; c <= cols.value; c++) {
        const s = seatMap.get(`${r}-${c}`)
        cells.push({ col: c, student_id: s ? s.student_id : null, student_name: s ? s.student_name : null })
      }
      rows.value.push({ row: r, cells })
    }
    if (maxRow === 0) rows.value = []
  } catch (e) {
    message.error(e.message)
  }
}
function addRow() {
  rows.value.push({
    row: rows.value.length + 1,
    cells: Array.from({ length: cols.value }, (_, i) => ({ col: i + 1, student_id: null, student_name: null })),
  })
}
function assignSeat(row, col) {
  assignTarget.row = row
  assignTarget.col = col
  const cur = seatAt(row, col)
  assignStudentId.value = cur.student_id || null
  assignShow.value = true
}
function confirmAssign() {
  const r = rows.value.find((x) => x.row === assignTarget.row)
  if (!r) return
  const cell = r.cells.find((c) => c.col === assignTarget.col)
  const stu = allStudents.value.find((x) => x.id === assignStudentId.value)
  cell.student_id = assignStudentId.value
  cell.student_name = stu ? stu.name : null
  assignShow.value = false
}
async function save() {
  if (!classId.value) {
    message.warning('请先选择班级')
    return
  }
  saving.value = true
  const seats = []
  for (const r of rows.value) {
    for (const cell of r.cells) {
      if (cell.student_id) {
        seats.push({ row: r.row, col: cell.col, student_id: cell.student_id })
      }
    }
  }
  try {
    await http.put('/seats', { class_id: classId.value, seats })
    message.success(`已保存 ${seats.length} 个座位`)
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}

onMounted(loadClasses)
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
.seats-container {
  background: linear-gradient(160deg, #fdf6ee, #f3ecff);
  border-radius: var(--radius-lg);
  padding: 24px;
  overflow-x: auto;
}
/* 讲台与网格同宽：横向滚动时讲台始终对齐座位中线，而不是对齐屏幕 */
.seats-inner {
  min-width: max-content;
  margin: 0 auto;
}
.podium {
  text-align: center;
  background: linear-gradient(135deg, #ffb86b, #ff8fab);
  color: #fff;
  font-weight: 800;
  padding: 10px;
  border-radius: 16px;
  margin-bottom: 24px;
  letter-spacing: 2px;
}
.seats-table {
  border-collapse: separate;
  border-spacing: 8px;
  margin: 0 auto;
  background: transparent !important;
}
.seats-table .row-label {
  color: #b39b86;
  font-size: 12px;
  text-align: center;
  width: 48px;
  font-weight: 700;
}
.seat-cell { padding: 4px; }
.seat {
  width: 72px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  cursor: pointer;
  border: 3px solid #fff;
  transition: transform 0.12s;
  background: #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.06);
}
.seat:hover { transform: scale(1.05); }
.seat.occupied {
  background: linear-gradient(135deg, #6c9ef5, #a78bfa);
  color: #fff;
}
.seat-empty { color: #d5c7b8; font-size: 12px; }
.seat-name { font-weight: 800; font-size: 15px; }
.seat-row { font-size: 10px; opacity: 0.8; }
</style>
