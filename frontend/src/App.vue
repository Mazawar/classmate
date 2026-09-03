<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { NConfigProvider, NMessageProvider } from 'naive-ui'

// 全局主题：糖果色覆盖，让 Naive 组件更卡通风
const themeOverrides = {
  common: {
    primaryColor: '#6c9ef5',
    primaryColorHover: '#82aff7',
    primaryColorPressed: '#4a7fd8',
    primaryColorSuppl: '#6c9ef5',
    borderRadius: '16px',
    borderRadiusSmall: '12px',
    textColorBase: '#4a4a55',
    fontSize: '15px',
  },
  Button: {
    borderRadiusMedium: '999px',
  },
  Card: {
    borderRadius: '24px',
  },
  DataTable: {
    borderRadius: '20px',
  },
}
</script>
