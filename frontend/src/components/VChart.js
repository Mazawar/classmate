// 轻量 ECharts 封装组件：自适应尺寸、自动清理、支持通用卡通配色调色板
import { h, onMounted, onBeforeUnmount, watch, ref, defineComponent } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart, RadarChart, ScatterChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent, DatasetComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, LineChart, PieChart, RadarChart, ScatterChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent, DatasetComponent,
  CanvasRenderer,
])

// 卡通感糖果配色
export const CARTOON_COLORS = [
  '#6c9ef5', '#ff8fab', '#ffb86b', '#8b5cf6', '#34d399',
  '#ffd166', '#22d3ee', '#f472b6', '#a3e635', '#fb7185',
]

// 通用图基配置
export function baseTooltip(extra = {}) {
  return {
    trigger: 'axis',
    backgroundColor: 'rgba(255,255,255,0.96)',
    borderColor: '#f0e6da',
    textStyle: { color: '#4a4a55', fontSize: 13 },
    ...extra,
  }
}

export default defineComponent({
  name: 'VChart',
  props: {
    option: { type: Object, required: true },
    height: { type: String, default: '320px' },
    width: { type: String, default: '100%' },
  },
  setup(props) {
    const elRef = ref(null)
    let chart = null
    let ro = null

    function render() {
      if (!chart && elRef.value) {
        chart = echarts.init(elRef.value)
      }
      if (chart) {
        chart.setOption(props.option, true)
      }
    }

    onMounted(() => {
      render()
      if (elRef.value && typeof ResizeObserver !== 'undefined') {
        ro = new ResizeObserver(() => chart && chart.resize())
        ro.observe(elRef.value)
      }
    })

    watch(() => props.option, render, { deep: true })

    onBeforeUnmount(() => {
      if (ro) ro.disconnect()
      if (chart) {
        chart.dispose()
        chart = null
      }
    })

    return () =>
      h('div', { ref: elRef, style: { width: props.width, height: props.height } })
  },
})
