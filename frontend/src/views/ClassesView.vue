<template>
  <div class="page-wrap">
    <div class="page-head">
      <div>
        <h2 class="page-title">🏫 班级管理</h2>
        <p class="page-sub">共 {{ total }} 个班级</p>
      </div>
      <n-button type="primary" @click="openCreate">
        <template #icon><span>➕</span></template>
        新增班级
      </n-button>
    </div>

    <!-- 班级卡片网格 -->
    <div v-if="classes.length" class="class-grid">
      <div v-for="c in classes" :key="c.id" class="class-card pop-in">
        <div class="class-banner">
          <div class="class-emoji">🏫</div>
          <div class="class-name">{{ c.name }}</div>
          <div v-if="c.grade" class="class-grade">{{ c.grade }}</div>
        </div>
        <div class="class-body">
          <div class="class-metric">
            <div class="cm-num">{{ c.student_count ?? 0 }}</div>
            <div class="cm-label">学生数</div>
          </div>
          <div class="class-remark">{{ c.remark || '暂无备注' }}</div>
          <div class="class-actions">
            <n-button size="small" secondary @click="openEdit(c)">编辑</n-button>
            <n-button size="small" secondary type="error" @click="remove(c)">删除</n-button>
          </div>
        </div>
      </div>
    </div>
    <n-empty v-else description="还没有班级，点右上角新增一个吧" style="margin-top: 60px" />

    <!-- 新增/编辑弹窗 -->
    <n-modal v-model:show="modalShow" preset="card" :title="editing ? '编辑班级' : '新增班级'" style="max-width: 460px">
      <n-form label-placement="top">
        <n-form-item label="班级名称 *">
          <n-input v-model:value="form.name" placeholder="如：初二(3)班" />
        </n-form-item>
        <n-form-item label="年级">
          <n-input v-model:value="form.grade" placeholder="如：初二" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="form.remark" type="textarea" placeholder="班级备注" />
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
const classes = ref([])
const total = ref(0)
const saving = ref(false)
const modalShow = ref(false)
const editing = ref(null)
const form = reactive({ name: '', grade: '', remark: '' })

async function load() {
  try {
    const res = await http.get('/classes')
    classes.value = res.items
    total.value = res.total
  } catch (e) {
    message.error(e.message)
  }
}

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', grade: '', remark: '' })
  modalShow.value = true
}
function openEdit(c) {
  editing.value = c
  Object.assign(form, { name: c.name, grade: c.grade || '', remark: c.remark || '' })
  modalShow.value = true
}

async function save() {
  if (!form.name) {
    message.warning('请填写班级名称')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await http.put(`/classes/${editing.value.id}`, form)
      message.success('已更新')
    } else {
      await http.post('/classes', form)
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
  message.warning(`确定删除班级「${c.name}」吗？`, { duration: 0, closable: true }, {
    onAction: async () => {
      try {
        await http.delete(`/classes/${c.id}`)
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
.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}
.class-card {
  background: #fff;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 24px var(--c-shadow);
  border: 3px solid #fff;
  transition: transform 0.15s;
}
.class-card:hover { transform: translateY(-4px); }
.class-banner {
  background: linear-gradient(135deg, #ffb86b, #ff8fab);
  padding: 26px 22px;
  text-align: center;
  color: #fff;
}
.class-emoji { font-size: 40px; }
.class-name { font-size: 22px; font-weight: 800; margin: 4px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.class-grade { display: inline-block; background: rgba(255,255,255,0.3); border-radius: 999px; padding: 2px 14px; font-size: 13px; }
.class-body { padding: 18px 20px; }
.class-metric { text-align: center; margin-bottom: 12px; }
.cm-num { font-size: 30px; font-weight: 800; color: var(--c-primary); }
.cm-label { color: #b39b86; font-size: 13px; }
.class-remark { color: #8a7a6b; font-size: 14px; min-height: 20px; text-align: center; margin-bottom: 14px; }
.class-actions { display: flex; justify-content: center; gap: 10px; }
</style>
