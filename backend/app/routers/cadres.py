# -*- coding: utf-8 -*-
"""班干部安排接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import CadreCreate, CadreOut, CadreUpdate, PageResult
from .auth import get_current_user

router = APIRouter(prefix="/api/cadres", tags=["cadres"])


def _to_out(c: models.ClassCadre) -> CadreOut:
    out = CadreOut.model_validate(c)
    out.student_name = c.student.name if c.student else None
    return out


@router.get("", response_model=PageResult)
def list_cadres(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.ClassCadre)
    if class_id:
        query = query.filter(models.ClassCadre.class_id == class_id)
    items = (
        query.options(joinedload(models.ClassCadre.student))
        .order_by(models.ClassCadre.id.asc())
        .all()
    )
    return PageResult(total=len(items), items=[_to_out(c) for c in items])


@router.get("/roles", response_model=dict)
def cadre_roles(_: models.User = Depends(get_current_user)):
    """返回班干部常用职位模板。"""
    return {
        "roles": [
            "班长",
            "副班长",
            "学习委员",
            "纪律委员",
            "体育委员",
            "劳动委员",
            "文艺委员",
            "生活委员",
            "宣传委员",
            "心理委员",
            "电教员",
            "课代表",
            "小组长",
        ]
    }


@router.post("", response_model=CadreOut, status_code=201)
def create_cadre(
    payload: CadreCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    dup = (
        db.query(models.ClassCadre)
        .filter(
            models.ClassCadre.class_id == payload.class_id,
            models.ClassCadre.role == payload.role,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail=f"该班级已设置「{payload.role}」职位")
    if payload.student_id:
        stu = db.query(models.Student).filter(models.Student.id == payload.student_id).first()
        if not stu:
            raise HTTPException(status_code=404, detail="学生不存在")
    cadre = models.ClassCadre(**payload.model_dump())
    db.add(cadre)
    db.commit()
    db.refresh(cadre)
    return _to_out(cadre)


@router.put("/{cadre_id}", response_model=CadreOut)
def update_cadre(
    cadre_id: int,
    payload: CadreUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    cadre = (
        db.query(models.ClassCadre)
        .filter(models.ClassCadre.id == cadre_id)
        .first()
    )
    if not cadre:
        raise HTTPException(status_code=404, detail="班干部不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(cadre, key, value)
    db.commit()
    db.refresh(cadre)
    return _to_out(cadre)


@router.delete("/{cadre_id}", response_model=dict)
def delete_cadre(
    cadre_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    cadre = (
        db.query(models.ClassCadre)
        .filter(models.ClassCadre.id == cadre_id)
        .first()
    )
    if not cadre:
        raise HTTPException(status_code=404, detail="班干部不存在")
    db.delete(cadre)
    db.commit()
    return {"deleted": True}
