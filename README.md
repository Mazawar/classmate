# ClassMate · 班主任减负系统

前后端分离的学生管理系统骨架。卡通风格，支持移动端。

- **前端**：Vue 3 + Vite + Pinia + Vue Router + Naive UI（卡通主题），响应式适配移动端
- **后端**：FastAPI + SQLAlchemy + SQLite，JWT 认证（python-jose + passlib/bcrypt）
- **数据库**：SQLite（单文件，开箱即用）

## 目录结构

```
classmate/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置（.env 可覆盖）
│   │   ├── database.py       # SQLAlchemy 引擎/会话
│   │   ├── models.py         # 数据模型（User/ClassModel/Student/Attendance）
│   │   ├── schemas.py        # Pydantic 校验
│   │   ├── security.py       # 密码哈希 + JWT
│   │   └── routers/          # auth / students / classes
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/http.js       # axios 实例（统一鉴权）
    │   ├── stores/auth.js    # Pinia 登录态
    │   ├── router/           # 路由 + 登录守卫
    │   ├── components/AppLayout.vue  # 侧边栏（移动端折叠）
    │   ├── views/            # Login / Dashboard / Students / Classes
    │   └── styles/cartoon.css # 卡通风格
    ├── index.html
    └── vite.config.js        # 开发代理 + 分包
```

## 已实现功能

- 账号注册/登录，首个注册用户自动成为管理员，JWT 鉴权
- 学生档案：增删改查、搜索（姓名/学号/家长）、按班级/性别筛选、分页
- 班级管理：增删改查、学生数统计
- 首页概览：学生/教室/男女统计卡片 + 快捷入口

## 后续可扩展（骨架预留）

- 考勤记录（数据模型已建 Attendance，CRUD 未写）
- 通知/留言、成绩管理、家长通讯录导出
- 更多统计图表

## 快速启动

### 后端

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 可选，自定义 secret_key
uvicorn app.main:app --reload --port 8000
```

启动后自动建表，接口文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173，开发代理 /api -> 8000
```

或构建生产包：

```bash
npm run build        # 输出到 frontend/dist
npm run preview      # 预览
```

> 生产部署时，前端把 `/api` 静态托管在 Nginx 等环境，并反向代理到后端即可。

## 技术要点

- 后端依赖的 `bcrypt` 需固定 `==4.0.1`（新版与 passlib 冲突，详见 requirements.txt）
- 前端 Naive UI 组件需在 `main.js` 全局注册（PascalCase / kebab-case 都要），否则模板里 `<n-button>` 等无法解析成真实组件
