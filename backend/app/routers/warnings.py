# -*- coding: utf-8 -*-
"""预警中心：成绩下滑 / 考勤异常 / 进步之星。

一次请求算完一个班（或全校）的重点关注名单，班主任打开页面即可看到
"谁需要找来聊聊"。所有统计在 Python 内存中聚合，避免 N+1 查询。
"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/api/warnings", tags=["warnings"])


@router.get("")
def warnings(
    class_id: Optional[int] = None,
    window_days: int = 30,
    absent_threshold: int = 3,   # 近 N 天 迟到+缺勤 >= 阈值 → 考勤预警
    rank_drop: int = 5,          # 相邻两次考试总分排名下滑 >= 阈值 → 成绩预警
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    window_days = max(7, min(window_days, 180))
    rank_drop = max(1, min(rank_drop, 50))
    absent_threshold = max(1, min(absent_threshold, 30))

    # ---- 学生与班级 ----
    stu_q = db.query(models.Student).options(joinedload(models.Student.class_))
    if class_id:
        stu_q = stu_q.filter(models.Student.class_id == class_id)
    students = stu_q.all()
    stu_map = {s.id: s for s in students}

    # ---- 考勤预警（窗口期内一次聚合查询）----
    since = date.today() - timedelta(days=window_days)
    att_q = (
        db.query(
            models.Attendance.student_id,
            models.Attendance.status,
            func.count(models.Attendance.id),
        )
        .filter(models.Attendance.date >= since)
        .group_by(models.Attendance.student_id, models.Attendance.status)
        .all()
    )
    att_agg: dict[int, dict[str, int]] = {}
    for sid, status, cnt in att_q:
        if sid in stu_map:
            att_agg.setdefault(sid, {})[status] = cnt

    attendance_alerts = []
    for sid, agg in att_agg.items():
        absent = agg.get("absent", 0)
        late = agg.get("late", 0)
        if absent + late >= absent_threshold:
            total_days = sum(agg.values())
            st = stu_map[sid]
            attendance_alerts.append({
                "student_id": sid,
                "name": st.name,
                "class_id": st.class_id,
                "class_name": st.class_.name if st.class_ else None,
                "absent": absent,
                "late": late,
                "leave": agg.get("leave", 0),
                "rate": round(agg.get("present", 0) / total_days * 100, 1) if total_days else 100,
            })
    attendance_alerts.sort(key=lambda x: -(x["absent"] * 2 + x["late"]))

    # ---- 成绩趋势（一次取出全部相关成绩）----
    exam_q = db.query(models.Exam).order_by(models.Exam.date.asc().nullslast(), models.Exam.id.asc())
    if class_id:
        exam_q = exam_q.filter(models.Exam.class_id == class_id)
    exams = exam_q.all()
    exams_by_class: dict[int, list] = {}
    for e in exams:
        exams_by_class.setdefault(e.class_id, []).append(e)

    exam_ids = [e.id for e in exams]
    totals: dict[tuple[int, int], float] = {}  # (exam_id, student_id) -> 总分
    if exam_ids:
        rows = (
            db.query(models.Score.exam_id, models.Score.student_id, models.Score.score)
            .filter(models.Score.exam_id.in_(exam_ids), models.Score.score.isnot(None))
            .all()
        )
        for eid, sid, sc in rows:
            if sid in stu_map:
                key = (eid, sid)
                totals[key] = totals.get(key, 0.0) + float(sc)

    # 每场考试的排名（仅班内）
    rank: dict[tuple[int, int], int] = {}  # (exam_id, student_id) -> 名次
    for e in exams:
        entries = sorted(
            ((t, sid) for (eid, sid), t in totals.items() if eid == e.id),
            reverse=True,
        )
        for i, (_t, sid) in enumerate(entries, 1):
            rank[(e.id, sid)] = i

    # 逐学生对比最近两次都有成绩的考试
    attention = []
    rising = []
    for st in students:
        class_exams = exams_by_class.get(st.class_id, [])
        history = [
            (e, totals[(e.id, st.id)], rank[(e.id, st.id)])
            for e in class_exams
            if (e.id, st.id) in totals
        ]
        if len(history) < 2:
            continue
        prev, last = history[-2], history[-1]
        # 名次数字越小越好：last 名次数字变大 = 下滑
        drop = last[2] - prev[2]   # >0 表示名次下滑
        gain = -drop               # >0 表示名次进步
        st_att = att_agg.get(st.id, {})
        att_bad = st_att.get("absent", 0) + st_att.get("late", 0)

        if drop >= rank_drop or att_bad >= absent_threshold:
            reasons = []
            if drop >= rank_drop:
                reasons.append(f"排名 #{prev[2]} → #{last[2]}（下滑 {drop} 名）")
            total_drop = round(last[1] - prev[1], 1)
            if total_drop < 0:
                reasons.append(f"总分 {prev[1]:g} → {last[1]:g}（{total_drop}）")
            if att_bad >= absent_threshold:
                reasons.append(
                    f"近{window_days}天迟到{st_att.get('late', 0)}次/缺勤{st_att.get('absent', 0)}次"
                )
            attention.append({
                "student_id": st.id,
                "name": st.name,
                "class_id": st.class_id,
                "class_name": st.class_.name if st.class_ else None,
                "reasons": reasons,
                "rank_drop": drop,
                "latest_rank": last[2],
                "exam_count": len(history),
                "absent": st_att.get("absent", 0),
                "late": st_att.get("late", 0),
            })

        if gain >= rank_drop:
            rising.append({
                "student_id": st.id,
                "name": st.name,
                "class_id": st.class_id,
                "class_name": st.class_.name if st.class_ else None,
                "rank_gain": gain,
                "from_rank": prev[2],
                "to_rank": last[2],
            })
    attention.sort(key=lambda x: (-x["rank_drop"], -(x["absent"] * 2 + x["late"])))
    rising.sort(key=lambda x: -x["rank_gain"])

    return {
        "window_days": window_days,
        "rank_drop": rank_drop,
        "absent_threshold": absent_threshold,
        "attention": attention,
        "rising": rising[:6],
        "attendance_alerts": attendance_alerts,
        "attention_count": len({a["student_id"] for a in attention}
                               | {a["student_id"] for a in attendance_alerts}),
    }
