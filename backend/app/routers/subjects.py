# -*- coding: utf-8 -*-
"""科目管理接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import PageResult, SubjectCreate, SubjectOut, SubjectUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=PageResult)
def list_subjects(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.Subject)
    if q:
        query = query.filter(models.Subject.name.like(f"%{q}%"))
    items = query.order_by(models.Subject.id.asc()).all()
    return PageResult(total=len(items), items=[SubjectOut.model_validate(s) for s in items])


@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(
    payload: SubjectCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    if (
        db.query(models.Subject)
        .filter(models.Subject.name == payload.name)
        .first()
    ):
        raise HTTPException(status_code=400, detail="科目已存在")
    subj = models.Subject(**payload.model_dump())
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return SubjectOut.model_validate(subj)


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="科目不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(subj, key, value)
    db.commit()
    db.refresh(subj)
    return SubjectOut.model_validate(subj)


@router.delete("/{subject_id}", response_model=dict)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="科目不存在")
    db.delete(subj)
    db.commit()
    return {"deleted": True}
