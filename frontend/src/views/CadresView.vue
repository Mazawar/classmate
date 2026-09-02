<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">👔 班干部安排</h2>
        <p class="page-sub">为班级设置班长、各委员等职务</p>
      </div>
      <div style="display: flex; gap: 10px">
        <n-select v-model:value="classFilter" placeholder="选择班级" :options="classOptions" clearable style="width: 160px" @update:value="load" />
        <n-button type="primary" @click="openCreate">
          <template #icon><span>➕</span></template>
          新增职务
        </n-button>
      </div>
    </div>

    <!-- 班干部卡片 -->
    <div v-if="cadres.length" class="cadre-grid">
      <div v-for="c in cadres" :key="c.id" class="cadre-card pop-in">
        <div class="cadre-emblem">⭐</div>
        <div class="cadre-role">{{ c.role }}</div>
        <div class="cadre-name">{{ c.student_name || '未分配' }}</div>
        <div v-if="c.note" class="cadre-note">{{ c.note }}</div>
        <div class="cadre-actions">
          <n-button size="tiny" secondary @click="openEdit(c)">编辑</n-button>
          <n-button size="tiny" secondary type="error" @click="remove(c)">移除</n-button>
        </div>
      </div>
    </div>
    <n-empty v-else description="还没有班干部，新增一个吧" style="margin-top: 60px" />

    <!-- 常用职位快捷选择 -->
    <h3 style="margin-top: 30px">📌 常用职位</h3>
    <div class="role-quick">
      <n-tag v-for="r in roleTemplates" :key="r" round :bordered="false" class="role-chip" @click="quickAdd(r)">
        ＋{{ r }}
      </n-tag>
    </div>

    <!-- 弹窗 -->
    <n-modal v-model:show="modalShow" preset="card" :title="editing ? '编辑职务' : '新增职务'" style="max-width: 420px">
      <n-form label-placement="top">
        <n-form-item label="职务 *">
          <n-input v-model:value="form.role" placeholder="如：班长、学习委员" />
        </n-form-item>
        <n-form-item label="任职学生">
          <n-select v-model:value="form.student_id" placeholder="选择学生" clearable filterable :options="studentOptions" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="form.note" type="textarea" placeholder="职责说明" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px">
          <n-button @click="modalShow = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="save">保存</n-button>
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
const cadres = ref([])
const saving = ref(false)
const modalShow = ref(false)
const editing = ref(null)
const classFilter = ref(null)
const classOptions = ref([])
const studentOptions = ref([])
const roleTemplates = ref([])

const form = reactive({ class_id: null, role: '', student_id: null, note: '' })

async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  if (res.items.length && !classFilter.value) {
    classFilter.value = res.items[0].id
    load()
  }
}
async function loadStudentsForClass() {
  if (!classFilter.value) {
    studentOptions.value = []
    return
  }
  const res = await http.get('/students', { params: { class_id: classFilter.value, per_page: 100 } })
  studentOptions.value = res.items
    .filter((s) => s.class_id === classFilter.value)
    .map((s) => ({ label: `${s.name}（${s.student_no || '—'}）`, value: s.id }))
}
async function load() {
  try {
    const params = {}
    if (classFilter.value) params.class_id = classFilter.value
    const res = await http.get('/cadres', { params })
    cadres.value = res.items
  } catch (e) {
    message.error(e.message)
  }
}
async function loadRoles() {
  try {
    const res = await http.get('/cadres/roles')
    roleTemplates.value = res.roles
  } catch (e) {
    /* ignore */
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { class_id: classFilter.value, role: '', student_id: null, note: '' })
  modalShow.value = true
}
function openEdit(c) {
  editing.value = c
  Object.assign(form, { class_id: c.class_id, role: c.role, student_id: c.student_id, note: c.note || '' })
  modalShow.value = true
}
async function quickAdd(role) {
  if (!classFilter.value) {
    message.warning('请先选择班级')
    return
  }
  Object.assign(form, { class_id: classFilter.value, role, student_id: null, note: '' })
  modalShow.value = true
}
async function save() {
  if (!form.role) {
    message.warning('请填写职务')
    return
  }
  if (!form.class_id) {
    message.warning('请先选择班级')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await http.put(`/cadres/${editing.value.id}`, { role: form.role, student_id: form.student_id, note: form.note })
      message.success('已更新')
    } else {
      await http.post('/cadres', form)
      message.success('已新增')
    }
    modalShow.value = false
    load()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}
function remove(c) {
  message.warning(`确定移除「${c.role}」职务吗？`, { duration: 0, closable: true }, {
    onAction: async () => {
      try {
        await http.delete(`/cadres/${c.id}`)
        message.success('已移除')
        load()
      } catch (e) {
        message.error(e.message)
      }
    },
  })
}

onMounted(() => {
  loadClasses()
  loadRoles()
  load()
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
.cadre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}
.cadre-card {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px;
  text-align: center;
  box-shadow: 0 6px 18px var(--c-shadow);
  border: 3px solid #fff;
  transition: transform 0.15s;
}
.cadre-card:hover { transform: translateY(-4px); }
.cadre-emblem { font-size: 30px; }
.cadre-role { font-weight: 800; font-size: 17px; margin-top: 4px; color: #4a4a55; }
.cadre-name { color: var(--c-primary); font-size: 15px; margin-top: 2px; }
.cadre-note { color: #b39b86; font-size: 12px; margin: 6px 0; }
.cadre-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }
.role-quick { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
.role-chip { cursor: pointer; padding: 6px 14px; font-size: 14px; transition: transform 0.1s; }
.role-chip:hover { transform: scale(1.05); }
</style>
