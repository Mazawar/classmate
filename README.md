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

**总览 & 可视化分析**
| 模块 | 说明 |
|------|------|
| 🏠 首页概览 | 综合统计 + 预警提醒横幅 + 性别构成饼图 + 各班级规模 + 最近考试各科平均柱状图 |
| 🚨 预警中心 | 自动找出需重点关注的学生：成绩排名下滑、近 N 天考勤异常（阈值可调），另有进步之星表扬名单；点学生看完整画像 |
| 📊 数据分析 | ECharts 可视化驾驶舱：班级男女构成、各科平均对比、历次考试主科趋势折线、单科分数分布直方图、总分前十 |
| 🧑‍🎓 学生画像 | 点击学生姓名弹出侧栏画像：基本信息、座位/职务、近90天考勤、历次成绩与班级对比曲线、最近一次排名 |

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
| 🧑‍🎓 学生档案 | 增删改查、搜索、筛选、分页，显示座位/职务，点姓名看个人画像 |
| ✅ 考勤打卡 | 按日出勤/迟到/缺勤/请假登记，勾选批量标记、一键全勤、随机点名器，30 天 CSS 趋势条 |
| 📈 成绩管理 | 考试管理、多科成绩录入（支持从 Excel/表格直接粘贴导入）、总分排名、科目统计（平均/最高/及格率） |
| 📞 家长通讯录 | 联系信息查询 + 一键导出 CSV（Excel 可直接打开） |

## 演示数据

项目内置数据生成脚本，一键填充 3 个班、132 名学生、9 门科目、班干部/座位/课程表，
以及 3 次考试的完整成绩与近 60 天考勤，方便体验所有页面与图表：

```bash
cd backend
.venv/bin/python seed_demo.py     # 重建演示数据（保留 admin 账号）
```

登录演示账号：`admin` / `admin123`

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
- 可视化用 **ECharts 6**，封装可复用组件 `frontend/src/components/VChart.js`（自带卡通配色、自适应）
