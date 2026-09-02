# -*- coding: utf-8 -*-
"""数据可视化 / 分析接口（供 ECharts 图表取数）。"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """班级/全局驾驶舱总览：男生女生、班级学生规模等。"""
    classes = db.query(models.ClassModel).all()
    cls_data = []
    for c in classes:
        male = (
            db.query(func.count(models.Student.id))
            .filter(models.Student.class_id == c.id, models.Student.gender == "M")
            .scalar() or 0
        )
        female = (
            db.query(func.count(models.Student.id))
            .filter(models.Student.class_id == c.id, models.Student.gender == "F")
            .scalar() or 0
        )
        cls_data.append({
            "id": c.id,
            "name": c.name,
            "male": male,
            "female": female,
            "total": male + female,
        })
    return {"classes": cls_data}


@router.get("/exam-trend")
def exam_trend(
    class_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """某班历次考试：各科平均分趋势（多根折线）。"""
    exams = (
        db.query(models.Exam)
        .filter(models.Exam.class_id == class_id)
        .order_by(models.Exam.date.asc())
        .all()
    )
    if not exams:
        return {"exams": [], "subjects": []}

    exam_ids = [e.id for e in exams]
    scores = (
        db.query(models.Score, models.Subject.name, models.Subject.full_score)
        .join(models.Subject, models.Subject.id == models.Score.subject_id)
        .filter(models.Score.exam_id.in_(exam_ids))
        .all()
    )
    subj_names = []
    seen = set()
    for _s, sname, _f in scores:
        if sname not in seen:
            seen.add(sname)
            subj_names.append(sname)

    # 按 科×考 平均
    subj_avg = {}  # subj -> {exam_id: avg}
    subj_vals = {}
    for s, sname, f in scores:
        subj_avg.setdefault(sname, {}).setdefault(s.exam_id, [])
        subj_avg[sname][s.exam_id].append(float(s.score))

    # 主科（语数外）纵向对比，其它科目折线过多则略
    main_sub = [n for n in subj_names if n in ("语文", "数学", "英语", "物理")]
    series = []
    for sname in main_sub or subj_names[:5]:
        vals = []
        for e in exams:
            arr = subj_avg.get(sname, {}).get(e.id)
            vals.append(round(sum(arr) / len(arr), 1) if arr else None)
        series.append({"name": sname, "values": vals})

    return {
        "exams": [{"id": e.id, "name": e.name, "date": str(e.date)} for e in exams],
        "series": series,
    }


@router.get("/score-distribution")
def score_distribution(
    exam_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """某次考试单科成绩分布(直方图用的>=x分段)。"""
    subj = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subj:
        raise HTTPException(404, "科目不存在")
    scores = (
        db.query(models.Score.score)
        .filter(models.Score.exam_id == exam_id,
                models.Score.subject_id == subject_id)
        .all()
    )
    full = subj.full_score or 100
    # 分段：及格线按 full*0.6，把区间分 5 或 6 段展示
    vals = [float(s[0]) for s in scores if s[0] is not None]
    n_bins = 6
    bins = []
    step = full / n_bins
    for i in range(n_bins):
        bins.append([i * step, (i + 1) * step, 0])
    for v in vals:
        idx = min(int(v // step), n_bins - 1)
        bins[idx][2] += 1
    dist = [
        {
            "range": f"{int(b[0])}~{int(b[1])}",
            "count": b[2],
            "ratio": round(b[2] / len(vals) * 100, 1) if vals else 0,
        }
        for b in bins
    ]
    avg = round(sum(vals) / len(vals), 1) if vals else 0
    passed = sum(1 for v in vals if v >= full * 0.6)
    return {
        "subject": subj.name,
        "full_score": full,
        "avg": avg,
        "pass_rate": round(passed / len(vals) * 100, 1) if vals else 0,
        "count": len(vals),
        "distribution": dist,
    }


@router.get("/class-avg-compare")
def class_avg_compare(
    exam_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """某次考试各科平均分横向对比（柱状）。"""
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "考试不存在")
    scores = (
        db.query(models.Score, models.Subject.name, models.Subject.full_score, models.Subject.color)
        .join(models.Subject, models.Subject.id == models.Score.subject_id)
        .filter(models.Score.exam_id == exam_id)
        .all()
    )
    agg = {}
    for s, sname, full, color in scores:
        a = agg.setdefault(sname, {"sum": 0.0, "n": 0, "full": full, "color": color})
        a["sum"] += float(s.score or 0)
        a["n"] += 1
    items = [
        {
            "name": k,
            "avg": round(v["sum"] / v["n"], 1) if v["n"] else 0,
            "full": v["full"],
            "color": v["color"],
        }
        for k, v in agg.items()
    ]
    items.sort(key=lambda x: -x["avg"])
    return {"exam_name": exam.name, "items": items}


@router.get("/top-students")
def top_students(
    class_id: int,
    exam_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """某班某次考试总分 Top N。"""
    totals = (
        db.query(
            models.Score.student_id,
            func.sum(models.Score.score).label("total"),
            func.avg(models.Score.score).label("avg"),
        )
        .filter(models.Score.exam_id == exam_id, models.Score.class_id == class_id)
        .group_by(models.Score.student_id)
        .order_by(desc("total"))
        .limit(limit)
        .all()
    )
    stus = {
        s.id: s
        for s in db.query(models.Student)
        .filter(models.Student.id.in_([t[0] for t in totals]))
        .all()
    }
    res = []
    for rank, (sid, total, avg) in enumerate(totals, 1):
        st = stus.get(sid)
        res.append({
            "rank": rank,
            "student_id": sid,
            "name": st.name if st else "?",
            "total": round(float(total), 1),
            "avg": round(float(avg), 1),
        })
    return {"items": res}


@router.get("/student-portrait/{student_id}")
def student_portrait(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """单个学生的完整画像(供点击学生后展示)：基本信息+历次成绩+考勤。"""
    st = (
        db.query(models.Student)
        .options(joinedload(models.Student.class_))
        .filter(models.Student.id == student_id)
        .first()
    )
    if not st:
        raise HTTPException(404, "学生不存在")

    # 职务与座位
    cadre = (
        db.query(models.ClassCadre)
        .filter(models.ClassCadre.student_id == student_id)
        .first()
    )
    seat = (
        db.query(models.Seat)
        .filter(models.Seat.student_id == student_id)
        .first()
    )

    # 每考总分统计
    score_rows = (
        db.query(models.Score, models.Exam)
        .join(models.Exam, models.Exam.id == models.Score.exam_id)
        .filter(models.Score.student_id == student_id)
        .all()
    )
    by_exam = {}
    for sc, ex in score_rows:
        blob = by_exam.setdefault(ex.id, {"exam": ex, "total": 0.0})
        blob["total"] += float(sc.score or 0)

    # 班内总分排名（每个学生只取一次考试的总分，再按考试分别算排名）
    exam_trend = []
    for exid, blob in by_exam.items():
        ex = blob["exam"]
        all_totals = (
            db.query(models.Score.student_id, func.sum(models.Score.score))
            .filter(models.Score.exam_id == exid)
            .group_by(models.Score.student_id)
            .all()
        )
        tot_list = [float(t[1]) for t in all_totals]
        my_total = blob["total"]
        rank = 1 + sum(1 for t in tot_list if my_total < t)
        avg_total = sum(tot_list) / len(tot_list) if tot_list else 0
        exam_trend.append({
            "exam_id": exid,
            "name": ex.name,
            "date": str(ex.date) if ex.date else "",
            "my_total": round(my_total, 1),
            "class_avg": round(avg_total, 1),
            "rank": rank,
            "count": len(tot_list),
        })
    exam_trend.sort(key=lambda x: x["date"])

    # 考勤汇总最近 90 天
    since = date.today() - timedelta(days=90)
    atts = (
        db.query(models.Attendance.status, func.count(models.Attendance.id))
        .filter(models.Attendance.student_id == student_id,
                models.Attendance.date >= since)
        .group_by(models.Attendance.status)
        .all()
    )
    att = {k: v for k, v in atts}

    return {
        "student": {
            "id": st.id,
            "name": st.name,
            "student_no": st.student_no,
            "gender": st.gender,
            "class_name": st.class_.name if st.class_ else None,
            "guardian": st.guardian,
            "phone": st.phone,
            "address": st.address,
            "birth_date": str(st.birth_date) if st.birth_date else None,
        },
        "cadre": cadre.role if cadre else None,
        "seat": f"{seat.row}排{seat.col}列" if seat else None,
        "exam_trend": exam_trend,
        "attendance": {
            "present": att.get("present", 0),
            "late": att.get("late", 0),
            "absent": att.get("absent", 0),
            "leave": att.get("leave", 0),
            "days": sum(att.values()),
        },
    }
