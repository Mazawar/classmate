# -*- coding: utf-8 -*-
"""数据导出接口（家长通讯录 CSV 等）。"""
import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/contacts")
def export_contacts(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """导出家长通讯录为 CSV。"""
    query = db.query(models.Student).order_by(models.Student.id.asc())
    if class_id:
        query = query.filter(models.Student.class_id == class_id)
    students = query.all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["学号", "姓名", "性别", "班级", "家长姓名", "联系电话1", "联系电话2", "住址"]
    )
    for s in students:
        writer.writerow(
            [
                s.student_no or "",
                s.name,
                "男" if s.gender == "M" else "女" if s.gender == "F" else "",
                s.class_.name if s.class_ else "",
                s.guardian or "",
                s.phone or "",
                s.guardian_phone2 or "",
                s.address or "",
            ]
        )

    csv_data = "\ufeff" + buf.getvalue()  # BOM 便于 Excel 识别中文
    filename = f"contacts_{'class' + str(class_id) if class_id else 'all'}.csv"
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/students")
def export_students(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """导出学生完整档案为 CSV。"""
    query = db.query(models.Student).order_by(models.Student.id.asc())
    if class_id:
        query = query.filter(models.Student.class_id == class_id)
    students = query.all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["学号", "姓名", "性别", "生日", "班级", "家长", "电话", "备用电话", "住址", "备注"])
    for s in students:
        writer.writerow(
            [
                s.student_no or "",
                s.name,
                "男" if s.gender == "M" else "女" if s.gender == "F" else "",
                s.birth_date.isoformat() if s.birth_date else "",
                s.class_.name if s.class_ else "",
                s.guardian or "",
                s.phone or "",
                s.guardian_phone2 or "",
                s.address or "",
                s.remark or "",
            ]
        )

    csv_data = "\ufeff" + buf.getvalue()
    filename = f"students_{'class' + str(class_id) if class_id else 'all'}.csv"
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
