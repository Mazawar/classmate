<template>
  <n-modal
    v-model:show="show"
    :mask-closable="true"
    class="portrait-modal"
    transform-origin="center"
  >
    <div class="portrait-card">
      <div class="portrait-close" @click="show=false">✕</div>
      <div class="portrait-header">
        <div class="avatar-big">{{ (data?.student?.name || '?').slice(0, 1) }}</div>
        <div>
          <div class="p-name">{{ data?.student?.name }}
            <n-tag v-if="data?.cadre" size="small" round :bordered="false" type="warning" style="margin-left:6px">⭐{{ data.cadre }}</n-tag>
          </div>
          <div class="p-sub">{{ data?.student?.class_name }} · {{ genderLabel }} · {{ data?.student?.student_no }}</div>
        </div>
      </div>

      <div v-if="!loading" class="portrait-body">
        <!-- 基本信息卡（固定不滚） -->
        <div class="info-cards">
          <div class="info-card"><span>座位</span><b>{{ data?.seat || '未排' }}</b></div>
          <div class="info-card"><span>家长</span><b>{{ data?.student?.guardian || '—' }}</b></div>
          <div class="info-card"><span>电话</span><b>{{ data?.student?.phone || '—' }}</b></div>
        </div>

        <!-- 下方内容：可滚动 -->
        <div class="portrait-scroll">
        <!-- 近90天考勤 -->
        <h4>✅ 近 90 天出勤</h4>
        <div class="att-summary">
          <div class="att-box" style="background:#34d399"><b>{{ data?.attendance?.present }}</b><span>出勤</span></div>
          <div class="att-box" style="background:#ffb020"><b>{{ data?.attendance?.late }}</b><span>迟到</span></div>
          <div class="att-box" style="background:#ef4444"><b>{{ data?.attendance?.absent }}</b><span>缺勤</span></div>
          <div class="att-box" style="background:#8b5cf6"><b>{{ data?.attendance?.leave }}</b><span>请假</span></div>
        </div>

        <!-- 历次成绩趋势 -->
        <h4 style="margin-top:18px">📈 历次考试总分与班级对比</h4>
        <v-chart v-if="trendOption.series?.[0]?.data?.length" :option="trendOption" height="240px" />
        <n-empty v-else description="暂未录入成绩" style="padding:20px 0" />

        <!-- 最近一次考试详情 -->
        <div v-if="latestExam" class="latest-card">
          <div class="latest-title">{{ latestExam.name }} · 总分 {{ latestExam.my_total }}（班均 {{ latestExam.class_avg }}）
            <n-tag :type="rankColor(latestExam)" size="small" round>第 {{ latestExam.rank }} / {{ latestExam.count }} 名</n-tag>
          </div>
          <n-progress
            type="line"
            :percentage="pct(latestExam)"
            :height="14"
            :color="latestExam.my_total >= latestExam.class_avg ? '#34d399' : '#ff6f6f'"
          />
        </div>
        </div><!-- /portrait-scroll -->
      </div><!-- /portrait-body -->
      <div v-else class="loading-box">加载中…</div>
    </div>
  </n-modal>

  <!-- portrait end -->
</template>

<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount, defineProps, defineEmits } from 'vue'
import http from '../api/http'
import VChart, { CARTOON_COLORS, baseTooltip } from './VChart'

const props = defineProps({ show: Boolean, studentId: Number })
const emit = defineEmits(['update:show'])

// 弹层宽度：桌面 720，窄屏自动贴合 94vw（居中）
const viewportW = ref(typeof window !== 'undefined' ? window.innerWidth : 900)
const isMobile = computed(() => viewportW.value < 640)
const modalWidth = computed(() => (isMobile.value ? '94vw' : '720px'))
function onResize() {
  viewportW.value = window.innerWidth
}
onMounted(() => {
  window.addEventListener('resize', onResize)
  viewportW.value = window.innerWidth
})
onBeforeUnmount(() => window.removeEventListener('resize', onResize))

const data = ref(null)
const loading = ref(false)
const computeVersion = ref(0)

const show = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v),
})

const genderLabel = computed(() => (data.value?.student?.gender === 'M' ? '男' : data.value?.student?.gender === 'F' ? '女' : ''))
const latestExam = computed(() =>
  data.value?.exam_trend && data.value.exam_trend.length
    ? data.value.exam_trend[data.value.exam_trend.length - 1]
    : null
)

watch(
  () => [props.show, props.studentId, computeVersion.value],
  async () => {
    if (props.show && props.studentId) {
      loading.value = true
      try {
        const res = await http.get(`/analytics/student-portrait/${props.studentId}`)
        data.value = res
      } catch (e) {
        data.value = null
      } finally {
        loading.value = false
      }
    }
  },
  { immediate: true }
)

function pct(e) {
  const fullTotal = e.count > 0 ? e.class_avg * 2 : 1000
  return Math.min(100, Math.round((e.my_total / Math.max(fullTotal, 1)) * 100))
}
function rankColor(e) {
  const r = e.rank
  if (r <= 3) return 'warning'
  if (r <= e.count / 2) return 'success'
  return 'error'
}

const trendOption = computed(() => {
  const t = data.value?.exam_trend || []
  return {
    color: [CARTOON_COLORS[0], '#c0aa94'],
    tooltip: baseTooltip({ valueFormatter: (v) => `${v} 分`, axisPointer: { type: 'cross' } }),
    legend: { data: ['我的总分', '班级平均'], bottom: 0, textStyle: { color: '#8a7a6b' } },
    grid: { top: 20, left: 30, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: t.map((e) => e.name), axisLabel: { color: '#8a7a6b' } },
    yAxis: { type: 'value', axisLabel: { color: '#8a7a6b' } },
    series: [
      {
        name: '我的总分',
        type: 'line',
        data: t.map((e) => e.my_total),
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 3 },
        label: { show: true, fontSize: 11, color: '#c9b6a4' },
        areaStyle: { opacity: 0.1 },
      },
      {
        name: '班级平均',
        type: 'line',
        data: t.map((e) => Math.round(e.class_avg)),
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2, type: 'dashed' },
      },
    ],
  }
})
</script>

<style scoped>
.portrait-card {
  background: #fff;
  border-radius: 22px;
  border: 3px solid #fff;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
  box-sizing: border-box;
  /* 固定头 + 仅下方滚动 */
  display: flex;
  flex-direction: column;
  height: auto;
  max-height: min(90vh, 720px);
  overflow: hidden;
}
.portrait-header { display: flex; align-items: center; gap: 12px; padding-right: 26px; flex: 0 0 auto; }
.portrait-body { display: flex; flex-direction: column; min-height: 0; flex: 1 1 auto; }
.portrait-body > .info-cards { flex: 0 0 auto; }
.portrait-scroll {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  padding-top: 2px;
  /* 柔和滚动条 */
  scrollbar-width: thin;
  scrollbar-color: #d9c6b2 transparent;
}
.portrait-scroll::-webkit-scrollbar { width: 6px; }
.portrait-scroll::-webkit-scrollbar-thumb { background: #d9c6b2; border-radius: 8px; }
.portrait-close {
  position: absolute; top: 12px; right: 14px;
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #f3e9dd; color: #8a7a6b; cursor: pointer; font-size: 13px;
  font-weight: 700; transition: all .12s;
}
.portrait-close:hover { background: #ff6f6f; color: #fff; transform: rotate(90deg); }
.avatar-big {
  width: 46px; height: 46px; border-radius: 50%;
  background: linear-gradient(135deg, #ff8fab, #ffb86b);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 800; font-size: 20px;
}
.p-name { font-size: 18px; font-weight: 800; color: #3b3b47; }
.p-sub { color: #b39b86; font-size: 12px; }
.portrait-body { padding: 4px; }
.info-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.info-card { background: #fbf6f1; border-radius: 12px; padding: 10px; text-align: center; }
.info-card span { display: block; color: #b39b86; font-size: 11px; }
.info-card b { color: #4a4a55; font-size: 14px; }
.att-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px; }
.att-box { color: #fff; border-radius: 14px; padding: 12px; text-align: center; border: 2px solid #fff; }
.att-box b { display: block; font-size: 20px; }
.att-box span { font-size: 11px; opacity: 0.9; }
.latest-card { margin-top: 6px; background: #f6f8ff; border-radius: 14px; padding: 14px; }
.latest-title { font-size: 13px; color: #4a4a55; font-weight: 700; margin-bottom: 8px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.loading-box { text-align: center; color: #b39b86; padding: 40px 0; }
</style>
