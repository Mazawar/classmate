<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">🧑‍🎓 学生管理</h2>
        <p class="page-sub">共 {{ total }} 名学生</p>
      </div>
      <n-button type="primary" @click="openCreate">
        <template #icon><span>➕</span></template>
        新增学生
      </n-button>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <n-input v-model:value="query" placeholder="🔍 搜索姓名 / 学号 / 家长" clearable style="max-width: 260px" @keyup.enter="load" />
      <n-select
        v-model:value="classFilter"
        placeholder="全部班级"
        clearable
        :options="classOptions"
        style="max-width: 180px"
        @update:value="load"
      />
      <n-select
        v-model:value="genderFilter"
        placeholder="全部性别"
        clearable
        :options="genderOptions"
        style="max-width: 130px"
        @update:value="load"
      />
      <n-button quaternary type="primary" @click="resetFilter">重置</n-button>
    </div>

    <!-- 表格 -->
    <div class="tbl-scroll pop-in">
      <n-data-table
        :columns="columns"
        :data="students"
        :loading="loading"
        :pagination="pagination"
        :bordered="false"
        remote
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <n-modal v-model:show="modalShow" preset="card" :title="editing ? '编辑学生' : '新增学生'" style="max-width: 500px">
      <n-form label-placement="top">
        <div class="form-grid">
          <n-form-item label="姓名 *">
            <n-input v-model:value="form.name" placeholder="学生姓名" />
          </n-form-item>
          <n-form-item label="学号">
            <n-input v-model:value="form.student_no" placeholder="学号" />
          </n-form-item>
          <n-form-item label="性别">
            <n-radio-group v-model:value="form.gender">
              <n-radio value="M">男</n-radio>
              <n-radio value="F">女</n-radio>
            </n-radio-group>
          </n-form-item>
          <n-form-item label="班级">
            <n-select v-model:value="form.class_id" clearable placeholder="选择班级" :options="classOptions" />
          </n-form-item>
          <n-form-item label="出生日期">
            <n-date-picker v-model:value="birthTs" type="date" clearable style="width: 100%" />
          </n-form-item>
          <n-form-item label="家长姓名">
            <n-input v-model:value="form.guardian" placeholder="家长姓名" />
          </n-form-item>
          <n-form-item label="家长电话">
            <n-input v-model:value="form.phone" placeholder="联系电话" />
          </n-form-item>
          <n-form-item label="备用电话">
            <n-input v-model:value="form.guardian_phone2" placeholder="备用联系电话" />
          </n-form-item>
        </div>
        <n-form-item label="家庭住址">
          <n-input v-model:value="form.address" placeholder="住址" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="form.remark" type="textarea" placeholder="其他说明" />
        </n-form-item>
      </n-form>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px">
          <n-button @click="modalShow = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="save">保存</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 学生画像抽屉 -->
    <student-portrait v-model:show="portraitShow" :student-id="portraitId" />
  </div>
</template>

<script setup>
import { h, onMounted, reactive, ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'
import StudentPortrait from '../components/StudentPortrait.vue'

const message = useMessage()

const students = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const query = ref('')
const classFilter = ref(null)
const genderFilter = ref(null)
const page = ref(1)
const perPage = 10

const genderOptions = [
  { label: '男', value: 'M' },
  { label: '女', value: 'F' },
]
const classOptions = ref([])

const modalShow = ref(false)
const portraitShow = ref(false)
const portraitId = ref(null)
const editing = ref(null)
const birthTs = ref(null)
const emptyForm = () => ({
  name: '', student_no: '', gender: null, class_id: null,
  guardian: '', phone: '', guardian_phone2: '', address: '', remark: '',
})
const form = reactive(emptyForm())

const columns = computed(() => [
  { title: '学号', key: 'student_no', minWidth: 90, render: (r) => r.student_no || '—' },
  { title: '姓名', key: 'name', minWidth: 90, render: (r) => h('a', { class: 'stu-link', onClick: () => openPortrait(r) }, r.name) },
  { title: '性别', key: 'gender', minWidth: 60, render: (r) => (r.gender === 'M' ? '👦 男' : r.gender === 'F' ? '👧 女' : '—') },
  { title: '班级', key: 'class_name', minWidth: 100, render: (r) => r.class_name || '未分班' },
  { title: '座位', key: 'seat', minWidth: 80, render: (r) => r.seat || '—' },
  { title: '职务', key: 'cadre', minWidth: 80, render: (r) => r.cadre ? '⭐ ' + r.cadre : '—' },
  { title: '家长', key: 'guardian', minWidth: 90, ellipsis: true, render: (r) => r.guardian || '—' },
  { title: '联系电话', key: 'phone', minWidth: 130, render: (r) => r.phone || '—' },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (r) =>
      h('div', { style: 'display:flex;gap:8px' }, [
        h('a', { onClick: () => openEdit(r), class: 'link-btn' }, '编辑'),
        h('a', { onClick: () => remove(r), class: 'link-btn danger' }, '删除'),
      ]),
  },
])

const pagination = computed(() => ({
  page: page.value,
  pageSize: perPage,
  itemCount: total.value,
  showSizePicker: false,
  onChange: (p) => {
    page.value = p
    load()
  },
}))

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (query.value) params.q = query.value
    if (classFilter.value) params.class_id = classFilter.value
    if (genderFilter.value) params.gender = genderFilter.value
    const res = await http.get('/students', { params })
    students.value = res.items
    total.value = res.total
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}

async function loadClasses() {
  try {
    const res = await http.get('/classes')
    classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
  } catch (e) {
    /* classOptions 留空 */
  }
}

function openCreate() {
  editing.value = null
  birthTs.value = null
  Object.assign(form, emptyForm())
  modalShow.value = true
}

function openEdit(row) {
  editing.value = row
  Object.assign(form, {
    name: row.name, student_no: row.student_no, gender: row.gender,
    class_id: row.class_id, guardian: row.guardian, phone: row.phone, guardian_phone2: row.guardian_phone2,
    address: row.address, remark: row.remark,
  })
  birthTs.value = row.birth_date ? new Date(row.birth_date + 'T00:00:00').getTime() : null
  modalShow.value = true
}

async function save() {
  if (!form.name) {
    message.warning('请填写姓名')
    return
  }
  saving.value = true
  const payload = { ...form }
  payload.birth_date = birthTs.value ? new Date(birthTs.value).toISOString().slice(0, 10) : null
  try {
    if (editing.value) {
      await http.put(`/students/${editing.value.id}`, payload)
      message.success('已更新')
    } else {
      await http.post('/students', payload)
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

function openPortrait(row) {
  portraitId.value = row.id
  portraitShow.value = true
}

function remove(row) {
  message.warning(`确定删除学生「${row.name}」吗？`, { duration: 0, closable: true }, {
    onAction: async () => {
      try {
        await http.delete(`/students/${row.id}`)
        message.success('已删除')
        load()
      } catch (e) {
        message.error(e.message)
      }
    },
  })
}

function resetFilter() {
  query.value = ''
  classFilter.value = null
  genderFilter.value = null
  page.value = 1
  load()
}

onMounted(() => {
  loadClasses()
  load()
})
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  align-items: center;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}
.link-btn {
  cursor: pointer;
  color: var(--c-primary);
  font-weight: 600;
}
.link-btn.danger { color: #ff6f6f; }
@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
