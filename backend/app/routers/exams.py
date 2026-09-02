# -*- coding: utf-8 -*-
"""考试与成绩接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..schemas import (
    ExamCreate,
    ExamOut,
    ExamUpdate,
    PageResult,
    ScoreRankRow,
    ScoreSave,
    ScoreSummary,
)
from .auth import get_current_user

router = APIRouter(prefix="/api/exams", tags=["exams"])


def _exam_to_out(e: models.Exam) -> ExamOut:
    out = ExamOut.model_validate(e)
    subjects = set()
    students = set()
    for s in e.scores:
        subjects.add(s.subject_id)
        students.add(s.student_id)
    out.subject_count = len(subjects)
    out.student_count = len(students)
    return out


@router.get("", response_model=PageResult)
def list_exams(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.Exam)
    if class_id:
        query = query.filter(models.Exam.class_id == class_id)
    items = query.order_by(desc(models.Exam.id)).all()
    return PageResult(total=len(items), items=[_exam_to_out(e) for e in items])


@router.post("", response_model=ExamOut, status_code=201)
def create_exam(
    payload: ExamCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    exam = models.Exam(**payload.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return _exam_to_out(exam)


@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(exam, key, value)
    db.commit()
    db.refresh(exam)
    return _exam_to_out(exam)


@router.delete("/{exam_id}", response_model=dict)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    db.delete(exam)
    db.commit()
    return {"deleted": True}


@router.post("/score", response_model=dict, status_code=201)
def save_scores(
    payload: ScoreSave,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == payload.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    # 删除该考试旧成绩
    db.query(models.Score).filter(models.Score.exam_id == payload.exam_id).delete()
    count = 0
    for cell in payload.rows:
        for subject_id, score in cell.scores.items():
            if score is None:
                continue
            rec = models.Score(
                exam_id=payload.exam_id,
                class_id=payload.class_id,
                student_id=cell.student_id,
                subject_id=subject_id,
                score=float(score),
            )
            db.add(rec)
            count += 1
    db.commit()
    return {"saved": count}


@router.get("/{exam_id}/summary", response_model=ScoreSummary)
def exam_summary(
    exam_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    scores = (
        db.query(models.Score)
        .filter(models.Score.exam_id == exam_id)
        .options(joinedload(models.Score.student), joinedload(models.Score.subject))
        .all()
    )

    # 按学生/科目聚合
    students_map: dict[int, models.Student] = {}
    stu_subjects: dict[int, dict[int, float]] = {}
    subject_meta: dict[int, dict] = {}
    for s in scores:
        students_map[s.student_id] = s.student
        stu_subjects.setdefault(s.student_id, {})[s.subject_id] = (
            float(s.score) if s.score is not None else None
        )
        meta = subject_meta.setdefault(
            s.subject_id,
            {
                "id": s.subject_id,
                "name": s.subject.name,
                "color": s.subject.color,
                "full_score": s.subject.full_score,
                "values": [],
            },
        )
        if s.score is not None:
            meta["values"].append(float(s.score))

    # 生成排名行
    rows = []
    for sid, subj_scores in stu_subjects.items():
        vals = [v for v in subj_scores.values() if v is not None]
        total = sum(vals)
        avg = round(total / len(vals), 1) if vals else 0
        rows.append(
            ScoreRankRow(
                student_id=sid,
                name=students_map[sid].name,
                student_no=students_map[sid].student_no,
                total=round(total, 1),
                average=avg,
                subjects=subj_scores,
            )
        )
    # 按总分排名
    rows.sort(key=lambda r: r.total, reverse=True)
    for i, r in enumerate(rows):
        r.rank = i + 1

    # 科目统计
    subject_stats = []
    for subj_id, meta in subject_meta.items():
        vals = meta["values"]
        avg = round(sum(vals) / len(vals), 1) if vals else 0
        full = meta["full_score"]
        passed = sum(1 for v in vals if v >= (full or 100) * 0.6)
        subject_stats.append(
            {
                "id": subj_id,
                "name": meta["name"],
                "color": meta["color"],
                "full_score": full,
                "avg": avg,
                "max": round(max(vals), 1) if vals else None,
                "min": round(min(vals), 1) if vals else None,
                "pass_rate": round(passed / len(vals) * 100, 1) if vals else 0,
            }
        )

    return ScoreSummary(
        exam_id=exam.id,
        exam_name=exam.name,
        class_id=exam.class_id,
        subjects=subject_stats,
        rows=rows,
    )
