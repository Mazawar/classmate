<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📞 家长通讯录</h2>
        <p class="page-sub">查看家长联系信息，一键导出 CSV</p>
      </div>
      <div style="display: flex; gap: 10px; flex-wrap: wrap">
        <n-select v-model:value="classFilter" placeholder="全部班级" clearable :options="classOptions" @update:value="load" style="width: 160px" />
        <n-button type="primary" @click="downloadContacts">
          <template #icon><span>⬇️</span></template>
          导出通讯录
        </n-button>
      </div>
    </div>

    <div class="tbl-scroll pop-in">
      <n-data-table
        :columns="columns"
        :data="students"
        :loading="loading"
        :bordered="false"
        :pagination="pagination"
      />
    </div>
  </div>
</template>

<script setup>
import { h, onMounted, ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import http from '../api/http'

const message = useMessage()
const classFilter = ref(null)
const classOptions = ref([])
const students = ref([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const perPage = 20

const columns = [
  { title: '姓名', key: 'name', minWidth: 80, render: (r) => h('b', {}, r.name) },
  { title: '班级', key: 'class_name', minWidth: 90, render: (r) => r.class_name || '—' },
  { title: '家长', key: 'guardian', minWidth: 80, render: (r) => r.guardian || '—' },
  { title: '联系电话', key: 'phone', minWidth: 130, render: (r) => r.phone ? h('a', { href: `tel:${r.phone}`, style: 'color:var(--c-primary)' }, r.phone) : '—' },
  { title: '备用电话', key: 'guardian_phone2', minWidth: 130, render: (r) => r.guardian_phone2 || '—' },
]

const pagination = computed(() => ({
  page: page.value,
  pageSize: perPage,
  itemCount: total.value,
  onChange: (p) => { page.value = p; load() },
}))

async function loadClasses() {
  const res = await http.get('/classes')
  classOptions.value = res.items.map((c) => ({ label: c.name, value: c.id }))
}
async function load() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (classFilter.value) params.class_id = classFilter.value
    const res = await http.get('/students', { params })
    students.value = res.items
    total.value = res.total
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}
async function downloadContacts() {
  try {
    const params = {}
    if (classFilter.value) params.class_id = classFilter.value
    const blob = await http.get('/export/contacts', { params, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = classFilter.value ? `家长通讯录_${classFilter.value}.csv` : '家长通讯录_全部.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    message.success('通讯录已导出')
  } catch (e) {
    message.error(e.message)
  }
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
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
