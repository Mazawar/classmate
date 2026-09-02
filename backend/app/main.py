# -*- coding: utf-8 -*-
"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import get_settings
from .database import Base, engine
from .routers import auth, classes, students

settings = get_settings()

# 建表
Base.metadata.create_all(bind=engine)

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


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.version, "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
