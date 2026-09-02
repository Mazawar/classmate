<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">📚 科目管理</h2>
        <p class="page-sub">维护学校科目，用于课程表与成绩录入</p>
      </div>
      <n-button type="primary" @click="openCreate">
        <template #icon><span>➕</span></template>
        新增科目
      </n-button>
    </div>

    <!-- 科目卡片网格 -->
    <div v-if="subjects.length" class="subject-grid">
      <div v-for="s in subjects" :key="s.id" class="subject-card pop-in" :style="{ '--color': s.color }">
        <div class="subject-color"></div>
        <div class="subject-emoji">📖</div>
        <div class="subject-name">{{ s.name }}</div>
        <div class="subject-short">{{ s.short || '—' }}</div>
        <div class="subject-full">满分 {{ s.full_score ?? 100 }}</div>
        <div class="subject-actions">
          <n-button size="small" secondary @click="openEdit(s)">编辑</n-button>
          <n-button size="small" secondary type="error" @click="remove(s)">删除</n-button>
        </div>
      </div>
    </div>
    <n-empty v-else description="还没有科目，点右上角新增" style="margin-top: 60px" />

    <!-- 弹窗 -->
    <n-modal v-model:show="modalShow" preset="card" :title="editing ? '编辑科目' : '新增科目'" style="max-width: 420px">
      <n-form label-placement="top">
        <n-form-item label="科目名称 *">
          <n-input v-model:value="form.name" placeholder="如：语文 / 数学" />
        </n-form-item>
        <n-form-item label="简称">
          <n-input v-model:value="form.short" maxlength="4" placeholder="如：语" />
        </n-form-item>
        <n-form-item label="满分">
          <n-input-number v-model:value="form.full_score" :min="10" :max="300" style="width: 100%" />
        </n-form-item>
        <n-form-item label="展示颜色">
          <n-color-picker v-model:value="form.color" :show-alpha="false" style="width: 100%" />
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
const subjects = ref([])
const saving = ref(false)
const modalShow = ref(false)
const editing = ref(null)
const empty = () => ({ name: '', short: '', color: '#6c9ef5', full_score: 100 })
const form = reactive(empty())

async function load() {
  try {
    const res = await http.get('/subjects')
    subjects.value = res.items
  } catch (e) {
    message.error(e.message)
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, empty())
  modalShow.value = true
}
function openEdit(s) {
  editing.value = s
  Object.assign(form, { name: s.name, short: s.short || '', color: s.color || '#6c9ef5', full_score: s.full_score ?? 100 })
  modalShow.value = true
}
async function save() {
  if (!form.name) {
    message.warning('请填写科目名称')
    return
  }
  saving.value = true
  try {
    if (editing.value) await http.put(`/subjects/${editing.value.id}`, form)
    else await http.post('/subjects', form)
    message.success(editing.value ? '已更新' : '已新增')
    modalShow.value = false
    load()
  } catch (e) {
    message.error(e.message)
  } finally {
    saving.value = false
  }
}
function remove(s) {
  message.warning(`确定删除科目「${s.name}」吗？`, { duration: 0, closable: true }, {
    onAction: async () => {
      try {
        await http.delete(`/subjects/${s.id}`)
        message.success('已删除')
        load()
      } catch (e) {
        message.error(e.message)
      }
    },
  })
}

onMounted(load)
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.subject-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 16px;
}
.subject-card {
  position: relative;
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  text-align: center;
  box-shadow: 0 6px 18px var(--c-shadow);
  border: 3px solid #fff;
  overflow: hidden;
  transition: transform 0.15s;
}
.subject-card:hover { transform: translateY(-4px); }
.subject-color {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 6px;
  background: var(--color);
}
.subject-emoji { font-size: 32px; }
.subject-name { font-weight: 800; font-size: 18px; margin-top: 4px; }
.subject-short { color: #b39b86; font-size: 14px; margin: 2px 0 8px; }
.subject-full { color: #8a7a6b; font-size: 13px; margin-bottom: 10px; }
.subject-actions { display: flex; justify-content: center; gap: 8px; }
</style>
