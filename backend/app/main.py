# -*- coding: utf-8 -*-
"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from . import models
from .config import get_settings
from .database import Base, engine
from .routers import (
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
)

settings = get_settings()

# 建表（新表会自动创建；已有表不自动加列）
Base.metadata.create_all(bind=engine)


def _ensure_column(table: str, column_def: str):
    """轻量迁移：若表中缺少指定列则 ALTER TABLE 添加。"""
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns(table)}
    col_name = column_def.split(" ")[0].split("(")[0].strip()
    if col_name not in cols:
        with engine.begin() as conn:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column_def}")


_ensure_column("students", "guardian_phone2 VARCHAR(32)")


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
app.include_router(subjects.router)
app.include_router(cadres.router)
app.include_router(seats.router)
app.include_router(schedule.router)
app.include_router(exams.router)
app.include_router(attendance.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.version, "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
