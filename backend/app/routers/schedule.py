# -*- coding: utf-8 -*-
"""课程表接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import PageResult, ScheduleCreate, ScheduleOut, ScheduleUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _to_out(s: models.ScheduleItem) -> ScheduleOut:
    out = ScheduleOut.model_validate(s)
    if s.subject:
        out.subject_name = s.subject.name
        out.subject_color = s.subject.color
    return out


@router.get("", response_model=dict)
def get_schedule(
    class_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    items = (
        db.query(models.ScheduleItem)
        .filter(models.ScheduleItem.class_id == class_id)
        .options(joinedload(models.ScheduleItem.subject))
        .order_by(
            models.ScheduleItem.weekday.asc(),
            models.ScheduleItem.period.asc(),
        )
        .all()
    )
    # 组织成 周 x 节 的网格
    grid = [[None for _ in range(10)] for _ in range(7)]  # 最多10节
    max_period = 0
    for it in items:
        grid[it.weekday - 1][it.period - 1] = _to_out(it)
        max_period = max(max_period, it.period)
    return {
        "total": len(items),
        "items": [_to_out(s) for s in items],
        "grid": grid,
        "max_period": max_period,
        "weekday_names": WEEKDAY_NAMES,
    }


@router.post("", response_model=ScheduleOut, status_code=201)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    dup = (
        db.query(models.ScheduleItem)
        .filter(
            models.ScheduleItem.class_id == payload.class_id,
            models.ScheduleItem.weekday == payload.weekday,
            models.ScheduleItem.period == payload.period,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail="该节课已设置课程")
    item = models.ScheduleItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.put("/{item_id}", response_model=ScheduleOut)
def update_schedule(
    item_id: int,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    item = (
        db.query(models.ScheduleItem)
        .filter(models.ScheduleItem.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="课程不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.delete("/{item_id}", response_model=dict)
def delete_schedule(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    item = (
        db.query(models.ScheduleItem)
        .filter(models.ScheduleItem.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="课程不存在")
    db.delete(item)
    db.commit()
    return {"deleted": True}
