# -*- coding: utf-8 -*-
"""考勤打卡接口。"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import AttendanceDayOut, AttendanceOut, AttendanceUpdate, PageResult
from .auth import get_current_user

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

STATUS_LABEL = {
    "present": "出勤",
    "late": "迟到",
    "absent": "缺勤",
    "leave": "请假",
}


@router.get("/day", response_model=AttendanceDayOut)
def get_day(
    date_str: Optional[str] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """获取某一天某班级的考勤情况。date_str 格式 YYYY-MM-DD，默认今天。"""
    target = date.fromisoformat(date_str) if date_str else date.today()

    query = db.query(models.Student)
    if class_id:
        query = query.filter(models.Student.class_id == class_id)
    students = query.order_by(models.Student.id.asc()).all()

    att_map = {}
    if students:
        records = (
            db.query(models.Attendance)
            .filter(models.Attendance.date == target)
            .all()
        )
        att_map = {a.student_id: a for a in records}

    status_count = {"present": 0, "late": 0, "absent": 0, "leave": 0}
    out_records = []
    for s in students:
        att = att_map.get(s.id)
        status = att.status if att else "present"
        status_count[status] = status_count.get(status, 0) + 1
        out_records.append(
            AttendanceOut(
                student_id=s.id,
                student_name=s.name,
                status=status,
                note=att.note if att else None,
            )
        )

    return AttendanceDayOut(
        date=target,
        total=len(students),
        **status_count,
        records=out_records,
    )


@router.put("", response_model=dict)
def save_day(
    payload: AttendanceUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """保存某天全班考勤。records 不含的默认置为出勤。"""
    existing = {
        r.student_id: r
        for r in db.query(models.Attendance)
        .filter(models.Attendance.date == payload.date)
        .all()
    }
    updated = 0
    for rec in payload.records:
        status = rec.get("status", "present")
        note = rec.get("note")
        sid = rec.get("student_id")
        if sid in existing:
            existing[sid].status = status
            existing[sid].note = note
        else:
            db.add(
                models.Attendance(
                    student_id=sid,
                    date=payload.date,
                    status=status,
                    note=note,
                )
            )
        updated += 1
    db.commit()
    return {"saved": updated}


@router.get("/summary", response_model=dict)
def attendance_summary(
    start: Optional[str] = None,
    end: Optional[str] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """按日期统计考勤，用于趋势图。默认最近 30 天。"""
    today = date.today()
    start_date = date.fromisoformat(start) if start else today - timedelta(days=30)
    end_date = date.fromisoformat(end) if end else today

    query = db.query(models.Attendance).filter(
        models.Attendance.date >= start_date,
        models.Attendance.date <= end_date,
    )
    rows = query.all()

    by_day: dict[str, dict] = {}
    for r in rows:
        d = r.date.isoformat()
        day = by_day.setdefault(d, {"date": d, "present": 0, "late": 0, "absent": 0, "leave": 0})
        day[r.status] = day.get(r.status, 0) + 1

    days = [by_day[k] for k in sorted(by_day.keys())]

    tot = {"present": 0, "late": 0, "absent": 0, "leave": 0}
    for d in days:
        for k in tot:
            tot[k] += d.get(k, 0)
    return {"days": days, "total": tot}
