# -*- coding: utf-8 -*-
"""请求/响应数据模型（Pydantic schemas）。"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- 通用 ----------
class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: object = None


class PageResult(BaseModel):
    total: int = 0
    items: list = []


# ---------- 认证 ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=64)
    nickname: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


# ---------- 班级 ----------
class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    grade: Optional[str] = None
    head_teacher_id: Optional[int] = None
    remark: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    head_teacher_id: Optional[int] = None
    remark: Optional[str] = None


class ClassOut(BaseModel):
    id: int
    name: str
    grade: Optional[str] = None
    head_teacher_id: Optional[int] = None
    remark: Optional[str] = None
    created_at: datetime
    student_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ---------- 学生 ----------
class StudentCreate(BaseModel):
    class_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=64)
    student_no: Optional[str] = None
    gender: Optional[str] = Field(default=None, pattern="^(M|F)$")
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    guardian: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class StudentUpdate(BaseModel):
    class_id: Optional[int] = None
    name: Optional[str] = None
    student_no: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    guardian: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    class_id: Optional[int] = None
    name: str
    student_no: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    guardian: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    class_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
