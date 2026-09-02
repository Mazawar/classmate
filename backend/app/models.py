# -*- coding: utf-8 -*-
"""
学生管理系统数据模型。
- User:       班主任用户
- ClassModel: 班级
- Student:    学生
- Attendance: 考勤记录
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Date,
    Boolean,
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
    remark: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class_: Mapped[Optional["ClassModel"]] = relationship(
        "ClassModel", back_populates="students"
    )


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "date", name="uq_att_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(16), default="present")  # present/late/absent/leave
    note: Mapped[Optional[str]] = mapped_column(Text, default=None)

    student: Mapped["Student"] = relationship("Student")
