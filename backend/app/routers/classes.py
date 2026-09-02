# -*- coding: utf-8 -*-
"""班级 CRUD 接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import ClassCreate, ClassOut, ClassUpdate, PageResult
from .auth import get_current_user

router = APIRouter(prefix="/api/classes", tags=["classes"])


def _to_out(c: models.ClassModel) -> ClassOut:
    out = ClassOut.model_validate(c)
    out.student_count = len(c.students)
    return out


@router.get("", response_model=PageResult)
def list_classes(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.ClassModel)
    if q:
        query = query.filter(models.ClassModel.name.like(f"%{q}%"))
    items = query.order_by(models.ClassModel.id.desc()).all()
    return PageResult(total=len(items), items=[_to_out(c) for c in items])


@router.post("", response_model=ClassOut, status_code=201)
def create_class(
    payload: ClassCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    if db.query(models.ClassModel).filter(models.ClassModel.name == payload.name).first():
        raise HTTPException(status_code=400, detail="班级名已存在")
    cls = models.ClassModel(**payload.model_dump())
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return _to_out(cls)


@router.get("/{class_id}", response_model=ClassOut)
def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    cls = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    return _to_out(cls)


@router.put("/{class_id}", response_model=ClassOut)
def update_class(
    class_id: int,
    payload: ClassUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    cls = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(cls, key, value)
    db.commit()
    db.refresh(cls)
    return _to_out(cls)


@router.delete("/{class_id}", response_model=dict)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    cls = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    db.delete(cls)
    db.commit()
    return {"deleted": True}
