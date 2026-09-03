# -*- coding: utf-8 -*-
"""
学生管理系统数据模型（班主任减负系统）。
- User:         班主任用户
- ClassModel:   班级
- Subject:      科目（全校/通用）
- Student:      学生
- ClassCadre:   班干部安排
- Seat:         座位表
- ScheduleItem: 课程表条目
- Exam:         考试
- Score:        成绩
- Attendance:   考勤记录
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Date,
    Boolean,
    Numeric,
    Text,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassModel(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    grade: Mapped[Optional[str]] = mapped_column(String(32), default=None)
    head_teacher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), default=None
    )
    remark: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    head_teacher: Mapped[Optional["User"]] = relationship("User")
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="class_"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[Optional[int]] = mapped_column(ForeignKey("classes.id"), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    student_no: Mapped[Optional[str]] = mapped_column(String(32), default=None)
    gender: Mapped[Optional[str]] = mapped_column(String(8), default=None)  # M / F
    birth_date: Mapped[Optional[date]] = mapped_column(Date, default=None)
    phone: Mapped[Optional[str]] = mapped_column(String(32), default=None)  # 家长电话
    guardian: Mapped[Optional[str]] = mapped_column(String(64), default=None)  # 家长姓名
    address: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    guardian_phone2: Mapped[Optional[str]] = mapped_column(String(32), default=None)  # 备用电话
    remark: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class_: Mapped[Optional["ClassModel"]] = relationship(
        "ClassModel", back_populates="students"
    )


class Subject(Base):
    """科目（全校/通用）。"""
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    short: Mapped[Optional[str]] = mapped_column(String(16), default=None)  # 简称
    color: Mapped[Optional[str]] = mapped_column(String(16), default="#6c9ef5")  # 展示色
    full_score: Mapped[Optional[int]] = mapped_column(Integer, default=100)  # 满分
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassCadre(Base):
    """班干部安排。"""
    __tablename__ = "class_cadres"
    __table_args__ = (UniqueConstraint("class_id", "role", name="uq_cadre_role"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    role: Mapped[str] = mapped_column(String(64))  # 如：班长、学习委员、体育委员
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"))
    note: Mapped[Optional[str]] = mapped_column(Text, default=None)

    class_: Mapped["ClassModel"] = relationship("ClassModel")
    student: Mapped[Optional["Student"]] = relationship("Student")


class Seat(Base):
    """座位表。"""
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("class_id", "row", "col", name="uq_seat"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"))
    row: Mapped[int] = mapped_column(Integer)  # 排（从教室前向后，1 开始）
    col: Mapped[int] = mapped_column(Integer)  # 列（从左到右，1 开始）

    student: Mapped[Optional["Student"]] = relationship("Student")


class ScheduleItem(Base):
    """课程表条目（单节课）。"""
    __tablename__ = "schedule"
    __table_args__ = (
        UniqueConstraint("class_id", "weekday", "period", name="uq_schedule"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)  # 1-7（周一~周日）
    period: Mapped[int] = mapped_column(Integer)   # 第几节课（1 开始）
    subject_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subjects.id"))
    teacher: Mapped[Optional[str]] = mapped_column(String(64), default=None)

    subject: Mapped[Optional["Subject"]] = relationship("Subject")


class Exam(Base):
    """考试。exam_type 用于同类型间比较（周考只和周考比，期中和期末跨比）。"""

    EXAM_TYPES = [
        ("weekly", "周考", "#22d3ee"),
        ("monthly", "月考", "#6c9ef5"),
        ("unit", "单元自测", "#a3e635"),
        ("subject", "单科考试", "#f472b6"),
        ("unified", "统一考试", "#8b5cf6"),
        ("midterm", "期中", "#ffb020"),
        ("final", "期末", "#ff6f6f"),
        ("mock", "模拟考", "#34d399"),
        ("other", "其他", "#94a3b8"),
    ]
    TYPE_MAP = {v: label for v, label, _ in EXAM_TYPES}

    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)  # 如：期中、期末
    exam_type: Mapped[Optional[str]] = mapped_column(String(24), default="other")
    date: Mapped[Optional[date]] = mapped_column(Date, default=None)
    remark: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scores: Mapped[list["Score"]] = relationship(
        "Score", back_populates="exam", cascade="all, delete-orphan"
    )


class Score(Base):
    """成绩。"""
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", "subject_id", name="uq_score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    score: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), default=None)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="scores")
    student: Mapped["Student"] = relationship("Student")
    subject: Mapped["Subject"] = relationship("Subject")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "date", name="uq_att_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(16), default="present")  # present/late/absent/leave
    note: Mapped[Optional[str]] = mapped_column(Text, default=None)

    student: Mapped["Student"] = relationship("Student")
