# -*- coding: utf-8 -*-
"""请求/响应数据模型（Pydantic schemas）。"""
import datetime as _dt
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
    guardian_phone2: Optional[str] = None
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
    guardian_phone2: Optional[str] = None
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
    guardian_phone2: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    class_name: Optional[str] = None
    seat: Optional[str] = None     # "第x排 第y列"
    cadre: Optional[str] = None    # 班干部职位

    model_config = ConfigDict(from_attributes=True)


# ---------- 科目 ----------
class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    short: Optional[str] = None
    color: Optional[str] = None
    full_score: Optional[int] = 100


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    short: Optional[str] = None
    color: Optional[str] = None
    full_score: Optional[int] = None


class SubjectOut(BaseModel):
    id: int
    name: str
    short: Optional[str] = None
    color: Optional[str] = None
    full_score: Optional[int] = 100

    model_config = ConfigDict(from_attributes=True)


# ---------- 班干部 ----------
class CadreCreate(BaseModel):
    class_id: int
    role: str = Field(min_length=1, max_length=64)
    student_id: Optional[int] = None
    note: Optional[str] = None


class CadreUpdate(BaseModel):
    role: Optional[str] = None
    student_id: Optional[int] = None
    note: Optional[str] = None


class CadreOut(BaseModel):
    id: int
    class_id: int
    role: str
    student_id: Optional[int] = None
    note: Optional[str] = None
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- 座位 ----------
class SeatItem(BaseModel):
    row: int
    col: int
    student_id: Optional[int] = None


class SeatSave(BaseModel):
    class_id: int
    seats: list[SeatItem] = Field(default_factory=list)


class SeatOut(BaseModel):
    row: int
    col: int
    student_id: Optional[int] = None
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- 课程表 ----------
class ScheduleCreate(BaseModel):
    class_id: int
    weekday: int = Field(ge=1, le=7)
    period: int = Field(ge=1)
    subject_id: Optional[int] = None
    teacher: Optional[str] = None


class ScheduleUpdate(BaseModel):
    subject_id: Optional[int] = None
    teacher: Optional[str] = None


class ScheduleOut(BaseModel):
    id: int
    class_id: int
    weekday: int
    period: int
    subject_id: Optional[int] = None
    teacher: Optional[str] = None
    subject_name: Optional[str] = None
    subject_color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- 考试 ----------
class ExamCreate(BaseModel):
    class_id: int
    name: str = Field(min_length=1, max_length=64)
    exam_type: str = Field(default="monthly", max_length=24)
    date: Optional[_dt.date] = None
    remark: Optional[str] = None


class ExamUpdate(BaseModel):
    name: Optional[str] = None
    exam_type: Optional[str] = None
    date: Optional[_dt.date] = None
    remark: Optional[str] = None


class ExamOut(BaseModel):
    id: int
    class_id: int
    name: str
    exam_type: Optional[str] = "other"
    date: Optional[_dt.date] = None
    remark: Optional[str] = None
    created_at: datetime
    subject_count: int = 0
    student_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ---------- 成绩 ----------
class ScoreCell(BaseModel):
    student_id: int
    scores: dict[int, float] = Field(default_factory=dict)  # subject_id -> score


class ScoreSave(BaseModel):
    exam_id: int
    class_id: int
    rows: list[ScoreCell] = Field(default_factory=list)


class ScoreRankRow(BaseModel):
    student_id: int
    name: str
    student_no: Optional[str] = None
    total: float = 0
    average: float = 0
    rank: int = 0
    subjects: dict[int, Optional[float]] = Field(default_factory=dict)


class ScoreSummary(BaseModel):
    exam_id: int
    exam_name: str
    class_id: int
    subjects: list[dict] = Field(default_factory=list)  # [{id,name,full_score,avg,max,min,pass_rate}]
    rows: list[ScoreRankRow] = Field(default_factory=list)


# ---------- 考勤 ----------
class AttendanceUpdate(BaseModel):
    date: _dt.date
    records: list[dict] = Field(default_factory=list)  # [{student_id,status,note}]


class AttendanceOut(BaseModel):
    student_id: int
    student_name: str
    status: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceDayOut(BaseModel):
    date: _dt.date
    present: int = 0
    late: int = 0
    absent: int = 0
    leave: int = 0
    total: int = 0
    records: list[AttendanceOut] = Field(default_factory=list)
