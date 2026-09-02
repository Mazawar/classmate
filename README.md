# ClassMate · 班主任减负系统

前后端分离的学生管理系统，卡通风格，支持移动端。围绕班主任日常工作设计，覆盖班级管理与学生管理两大维度。

- **前端**：Vue 3 + Vite + Pinia + Vue Router + Naive UI（卡通主题），响应式适配移动端
- **后端**：FastAPI + SQLAlchemy + SQLite，JWT 认证（python-jose + passlib/bcrypt）
- **数据库**：SQLite（单文件，开箱即用）

## 目录结构

```
classmate/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口（含轻量自动建表/迁移）
│   │   ├── config.py         # 配置（.env 可覆盖）
│   │   ├── database.py       # SQLAlchemy 引擎/会话
│   │   ├── models.py         # 10 张表数据模型
│   │   ├── schemas.py        # Pydantic 校验
│   │   ├── security.py       # 密码哈希 + JWT
│   │   └── routers/          # 各业务路由
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/http.js       # axios 实例（统一鉴权）
    │   ├── stores/auth.js    # Pinia 登录态
    │   ├── router/           # 11 个页面路由
    │   ├── components/       # AppLayout（分组侧栏 + 移动端折叠）
    │   ├── views/            # 各功能页面
    │   └── styles/cartoon.css # 卡通风格
    ├── index.html
    └── vite.config.js        # 开发代理 + 分包
```

## 功能模块

**班级维度**
| 模块 | 说明 |
|------|------|
| 🏫 班级管理 | 班级增删改查、学生数统计 |
| 📋 课程表 | 按周×节次的网格排课，支持科目颜色、任课老师 |
| 💺 座位表 | 可视化排座，点击座位为学生分配位置 |
| 👔 班干部 | 班长/各委员职务安排，带常用职位快捷模板 |
| 📚 科目管理 | 维护科目、简称、满分、展示色 |

**学生维度**
| 模块 | 说明 |
|------|------|
| 🧑‍🎓 学生档案 | 增删改查、搜索、筛选、分页，显示座位/职务 |
| ✅ 考勤打卡 | 按日出勤/迟到/缺勤/请假登记，30 天趋势 |
| 📈 成绩管理 | 考试管理、多科成绩录入、排名、科目统计（平均/最高/及格率） |
| 📞 家长通讯录 | 联系信息查询 + 一键导出 CSV（Excel 可直接打开） |

**总览**
| 模块 | 说明 |
|------|------|
| 🏠 首页概览 | 综合统计卡片、男女比例、快捷入口 |

## 数据模型（10 张表）

`users` → `classes` → `subjects` / `students`，业务表含 `class_cadres`（班干部）、`seats`（座位）、`schedule`（课程表）、`exams` + `scores`（考试与成绩）、`attendance`（考勤）。

系统启动 `Base.metadata.create_all` 自动建表；对已存在表新增列采用轻量 `ALTER TABLE` 迁移（见 `main.py._ensure_column`），无需手工迁移。

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

> 生产部署：前端 `/api` 静态托管并反向代理到后端即可。

## 技术要点

- 后端 `bcrypt` 需固定 `==4.0.1`（新版与 passlib 冲突）
- 前端 Naive UI 组件需在 `main.js` 全局注册（PascalCase / kebab-case 都要）
- Pydantic v2：字段名为 `date` 时用 `_dt.date` 类型避免与类型名冲突
- 通讯录/学生导出走 axios blob 携带 JWT 下载，避免 token 丢失
