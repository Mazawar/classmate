# -*- coding: utf-8 -*-
"""座位表接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import PageResult, SeatOut, SeatSave
from .auth import get_current_user

router = APIRouter(prefix="/api/seats", tags=["seats"])


@router.get("", response_model=PageResult)
def get_seats(
    class_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    items = (
        db.query(models.Seat)
        .filter(models.Seat.class_id == class_id)
        .order_by(models.Seat.row.asc(), models.Seat.col.asc())
        .all()
    )
    out = []
    for s in items:
        o = SeatOut(
            row=s.row,
            col=s.col,
            student_id=s.student_id,
            student_name=s.student.name if s.student else None,
        )
        out.append(o)
    return PageResult(total=len(out), items=out)


@router.put("", response_model=dict)
def save_seats(
    payload: SeatSave,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """整表替换某班级的座位安排。"""
    cls = db.query(models.ClassModel).filter(models.ClassModel.id == payload.class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    db.query(models.Seat).filter(models.Seat.class_id == payload.class_id).delete()
    for item in payload.seats:
        if item.student_id is None:
            continue
        seat = models.Seat(
            class_id=payload.class_id,
            row=item.row,
            col=item.col,
            student_id=item.student_id,
        )
        db.add(seat)
    db.commit()
    return {"saved": len(payload.seats)}
