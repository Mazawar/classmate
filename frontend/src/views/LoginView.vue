<template>
  <div class="login-page">
    <div class="login-card cartoon-card pop-in">
      <div class="mascot">🦉</div>
      <h1 class="login-title">ClassMate</h1>
      <p class="login-sub">班主任减负小助手 · 学生管理系统</p>

      <n-tabs type="segment" animated v-model:value="tab">
        <n-tab-pane name="login" tab="登录">
          <n-form @submit.prevent="doLogin" size="large">
            <n-form-item label="用户名">
              <n-input v-model:value="form.username" placeholder="请输入用户名" autocomplete="username" />
            </n-form-item>
            <n-form-item label="密码">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="请输入密码"
                autocomplete="current-password"
                @keyup.enter="doLogin"
              />
            </n-form-item>
            <n-button attr-type="submit" type="primary" block :loading="loading" class="submit-btn">
              开始减负 🚀
            </n-button>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="register" tab="注册（首个用户为管理员）">
          <n-form @submit.prevent="doRegister" size="large">
            <n-form-item label="用户名">
              <n-input v-model:value="reg.username" placeholder="至少3个字符" />
            </n-form-item>
            <n-form-item label="昵称">
              <n-input v-model:value="reg.nickname" placeholder="可选" />
            </n-form-item>
            <n-form-item label="密码">
              <n-input v-model:value="reg.password" type="password" show-password-on="click" placeholder="至少6个字符" />
            </n-form-item>
            <n-button attr-type="submit" type="primary" block :loading="loading" class="submit-btn">
              创建账号 🎉
            </n-button>
          </n-form>
        </n-tab-pane>
      </n-tabs>
    </div>
    <div class="footer">Made with ❤️ by ClassMate</div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const reg = reactive({ username: '', nickname: '', password: '' })

async function doLogin() {
  if (!form.username || !form.password) {
    message.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    message.success('登录成功，欢迎回来！')
    router.push('/dashboard')
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  if (!reg.username || !reg.password) {
    message.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.register(reg)
    message.success('注册成功，已自动登录！')
    router.push('/dashboard')
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #eaf3ff, #fff4e6, #ffe9f1);
  padding: 20px;
}
.login-card {
  width: 400px;
  max-width: 100%;
  padding: 32px 30px;
}
.mascot {
  font-size: 64px;
  text-align: center;
  margin-bottom: 6px;
  animation: wobble 3s ease-in-out infinite;
}
@keyframes wobble {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}
.login-title {
  text-align: center;
  font-size: 30px;
  margin: 0;
}
.login-sub {
  text-align: center;
  color: #b39b86;
  margin: 6px 0 22px;
  font-size: 14px;
}
.submit-btn {
  margin-top: 8px;
  font-weight: 700;
}
.footer {
  margin-top: 24px;
  color: #c9b6a4;
  font-size: 13px;
}
</style>
