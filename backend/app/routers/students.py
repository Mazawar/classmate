# -*- coding: utf-8 -*-
"""学生档案 CRUD 接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import PageResult, StudentCreate, StudentOut, StudentUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/students", tags=["students"])


def _to_out(s: models.Student) -> StudentOut:
    out = StudentOut.model_validate(s)
    out.class_name = s.class_.name if s.class_ else None
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
    return PageResult(total=total, items=[_to_out(s) for s in items])


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
    return {
        "total_students": total,
        "male": male,
        "female": female,
        "not_in_class": not_in_class,
        "total_classes": class_count,
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
    return _to_out(student)


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
    return _to_out(student)


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
    return _to_out(student)


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
