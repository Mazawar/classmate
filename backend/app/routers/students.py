# -*- coding: utf-8 -*-
"""学生档案 CRUD 接口。"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import PageResult, StudentCreate, StudentOut, StudentUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/students", tags=["students"])


def _to_out(s: models.Student, db: Optional[Session] = None) -> StudentOut:
    out = StudentOut.model_validate(s)
    out.class_name = s.class_.name if s.class_ else None
    if s.class_id and db is not None:
        seat = (
            db.query(models.Seat)
            .filter(
                models.Seat.class_id == s.class_id,
                models.Seat.student_id == s.id,
            )
            .first()
        )
        if seat:
            out.seat = f"{seat.row}排{seat.col}列"
        cadre = (
            db.query(models.ClassCadre)
            .filter(
                models.ClassCadre.class_id == s.class_id,
                models.ClassCadre.student_id == s.id,
            )
            .first()
        )
        if cadre:
            out.cadre = cadre.role
    return out


@router.get("", response_model=PageResult)
def list_students(
    q: Optional[str] = None,
    class_id: Optional[int] = None,
    gender: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.Student)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Student.name.like(like),
                models.Student.student_no.like(like),
                models.Student.guardian.like(like),
            )
        )
    if class_id:
        query = query.filter(models.Student.class_id == class_id)
    if gender:
        query = query.filter(models.Student.gender == gender)

    total = query.count()
    items = (
        query.options(joinedload(models.Student.class_))
        .order_by(models.Student.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PageResult(total=total, items=[_to_out(s, db) for s in items])


@router.get("/stats", response_model=dict)
def student_stats(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    total = db.query(func.count(models.Student.id)).scalar() or 0
    male = (
        db.query(func.count(models.Student.id))
        .filter(models.Student.gender == "M")
        .scalar()
        or 0
    )
    female = (
        db.query(func.count(models.Student.id))
        .filter(models.Student.gender == "F")
        .scalar()
        or 0
    )
    class_count = db.query(func.count(models.ClassModel.id)).scalar() or 0
    not_in_class = (
        db.query(func.count(models.Student.id))
        .filter(models.Student.class_id.is_(None))
        .scalar()
        or 0
    )
    subject_count = db.query(func.count(models.Subject.id)).scalar() or 0
    cadre_count = db.query(func.count(models.ClassCadre.id)).scalar() or 0
    exam_count = db.query(func.count(models.Exam.id)).scalar() or 0
    # 今日考勤
    today = date.today()
    att_today = (
        db.query(func.count(models.Attendance.id))
        .filter(models.Attendance.date == today)
        .scalar()
        or 0
    )
    return {
        "total_students": total,
        "male": male,
        "female": female,
        "not_in_class": not_in_class,
        "total_classes": class_count,
        "total_subjects": subject_count,
        "total_cadres": cadre_count,
        "total_exams": exam_count,
        "attendance_today": att_today,
    }


@router.post("", response_model=StudentOut, status_code=201)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = models.Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    if student.class_id:
        db.refresh(student.class_)
    return _to_out(student, db)


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = (
        db.query(models.Student)
        .options(joinedload(models.Student.class_))
        .filter(models.Student.id == student_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return _to_out(student, db)


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    if student.class_id:
        db.refresh(student.class_)
    return _to_out(student, db)


@router.delete("/{student_id}", response_model=dict)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(student)
    db.commit()
    return {"deleted": True}
