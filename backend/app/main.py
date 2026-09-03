# -*- coding: utf-8 -*-
"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from . import models
from .config import get_settings
from .database import Base, engine
from .routers import (
    analytics,
    attendance,
    auth,
    cadres,
    classes,
    exams,
    export,
    schedule,
    seats,
    students,
    subjects,
    warnings,
)

settings = get_settings()

# 建表（新表会自动创建；已有表不自动加列）
Base.metadata.create_all(bind=engine)


def _ensure_indexes():
    """高频查询的复合索引（幂等，已存在则跳过）。"""
    stmts = [
        # 成绩排名统计：按考试+班级取全部分数再按学生聚合
        "CREATE INDEX IF NOT EXISTS idx_scores_exam_class_student ON scores(exam_id, class_id, student_id)",
        # 学生画像：按学生取历次成绩
        "CREATE INDEX IF NOT EXISTS idx_scores_student_exam ON scores(student_id, exam_id)",
        # 考勤趋势：按日期窗口聚合
        "CREATE INDEX IF NOT EXISTS idx_attendance_date_status ON attendance(date, status)",
        # 预警中心：按班级取历次考试
        "CREATE INDEX IF NOT EXISTS idx_exams_class_date ON exams(class_id, date)",
    ]
    with engine.begin() as conn:
        for s in stmts:
            conn.exec_driver_sql(s)


_ensure_indexes()


def _ensure_column(table: str, column_def: str):
    """轻量迁移：若表中缺少指定列则 ALTER TABLE 添加。"""
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns(table)}
    col_name = column_def.split(" ")[0].split("(")[0].strip()
    if col_name not in cols:
        with engine.begin() as conn:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column_def}")


_ensure_column("students", "guardian_phone2 VARCHAR(32)")
_ensure_column("exams", "exam_type VARCHAR(24) DEFAULT 'other'")


def _backfill_exam_types():
    """存量考试按名字启发式归类 exam_type（一次性，已有类型的不动）。"""
    rules = [
        ("midterm", ("期中",)),
        ("final", ("期末",)),
        ("weekly", ("周考", "周测", "周练")),
        ("monthly", ("月考", "月测")),
        ("unit", ("单元", "章节")),
        ("mock", ("模拟", "模考")),
        ("subject", ("单科", "专项")),
        ("unified", ("统考", "统一考试", "联考")),
    ]
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("exams")}
    if "exam_type" not in cols:
        return
    with engine.begin() as conn:
        rows = conn.exec_driver_sql(
            "SELECT id, name FROM exams WHERE exam_type IS NULL OR exam_type = 'other'"
        ).fetchall()
        for eid, name in rows:
            name = (name or "").lower()
            for tval, keys in rules:
                if any(k in name for k in keys):
                    conn.exec_driver_sql(
                        "UPDATE exams SET exam_type = ? WHERE id = ?",
                        (tval, eid),
                    )
                    break


_backfill_exam_types()


app = FastAPI(title="ClassMate 学生管理系统", version=settings.version)

# CORS：开发阶段前端 Vite 服务器跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(analytics.router)
app.include_router(subjects.router)
app.include_router(cadres.router)
app.include_router(seats.router)
app.include_router(schedule.router)
app.include_router(exams.router)
app.include_router(attendance.router)
app.include_router(export.router)
app.include_router(warnings.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.version, "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
