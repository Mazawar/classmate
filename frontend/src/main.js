import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  NConfigProvider,
  NMessageProvider,
  NButton,
  NInput,
  NForm,
  NFormItem,
  NTabs,
  NTabPane,
  NDataTable,
  NSelect,
  NModal,
  NRadio,
  NRadioGroup,
  NDatePicker,
  NIcon,
  NEmpty,
  NInputNumber,
  NColorPicker,
  NTag,
  NGradientText,
  NPopover,
  NBadge,
  NButtonGroup,
  NCheckbox,
  NCheckboxGroup,
  NDrawer,
  NDrawerContent,
  NProgress,
} from 'naive-ui'
import App from './App.vue'
import router from './router'
import './styles/cartoon.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// 全局注册 Naive UI 组件。
// 注册时同时登记 PascalCase、kebab-case 和组件自带 name，
// 这样模板里 <n-button> / <NButton> 都能正确解析。
function toKebab(str) {
  // "Button" -> "button", "FormItem" -> "form-item", then prefix "n-"
  return (
    'n-' +
    str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
  )
}

const comps = [
  NConfigProvider, NMessageProvider, NButton, NInput, NForm, NFormItem,
  NTabs, NTabPane, NDataTable, NSelect, NModal,
  NRadio, NRadioGroup, NDatePicker, NIcon, NEmpty,
  NInputNumber, NColorPicker, NTag, NGradientText, NPopover, NBadge,
  NButtonGroup, NCheckbox, NCheckboxGroup,
  NDrawer, NDrawerContent, NProgress,
]

comps.forEach((c) => {
  const key = c.name // 如 "Button"、"Input"
  const kebab = toKebab(key) // 如 "n-button"、"n-input"
  const pascal = key[0].toUpperCase() + key.slice(1) // 如 "NButton"
  app.component(key, c)
  app.component(kebab, c)
  app.component(pascal, c)
})

app.mount('#app')
