# -*- coding: utf-8 -*-
"""
生成一套逼真的演示数据，让班级管理、成绩、考勤等所有图表/分析有内容可展示。
用法（在 backend 目录下运行）：.venv/bin/python seed_demo.py
会重建业务数据（保留 admin 用户）。仅为演示 / 测试用途。
"""
import random
from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app import models
from app.security import hash_password

random.seed(7)

SUBJECT_DEFS = [
    ("语文", "语", "#ef6da0", 120),
    ("数学", "数", "#6c9ef5", 120),
    ("英语", "英", "#8b5cf6", 120),
    ("物理", "物", "#34d399", 100),
    ("化学", "化", "#ffb020", 100),
    ("生物", "生", "#22d3ee", 100),
    ("历史", "史", "#f472b6", 100),
    ("地理", "地", "#a3e635", 100),
    ("政治", "政", "#ff6f6f", 100),
]

CADRE_TEMPLATE = [
    ("班长", "李雨桐"), ("副班长", "周子昂"), ("学习委员", "陈思颖"),
    ("纪律委员", "赵子墨"), ("体育委员", "孙浩宇"), ("劳动委员", "钱晓燕"),
    ("文艺委员", "林诗涵"),
]

CN_SURNAMES = "王李张刘陈杨黄赵吴周徐孙马朱"
CN_GIVEN_M = ["子轩", "浩宇", "雨泽", "子墨", "俊杰", "嘉懿", "煜城", "鹏飞", "致远", "思远",
              "志强", "天佑", "铭泽", "泽豪", "昊然", "懿轩", "君昊", "晓东", "立轩", "振宇"]
CN_GIVEN_F = ["雨桐", "诗涵", "思颖", "晓燕", "语嫣", "梓萱", "欣妍", "佳琪", "雅静", "思琪",
              "欣怡", "若曦", "静怡", "婉婷", "梦琪", "诗琪", "芷若", "沐宸", "心怡", "乐瑶"]

TEACHERS = ["王芳", "李明", "刘晓慧", "张伟", "陈静", "赵敏", "杨帆", "周虹"]
WEEKDAY_MAIN = ["语文", "数学", "英语"]


def make_name(is_male):
    return random.choice(CN_SURNAMES) + random.choice(CN_GIVEN_M if is_male else CN_GIVEN_F)


def add_demo_data(db: Session):
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(username="admin", password_hash=hash_password("admin123"),
                            nickname="班主任", is_admin=True)
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # 清理旧业务数据（从子表到父表）
    db.query(models.Attendance).delete()
    db.query(models.Score).delete()
    db.query(models.Exam).delete()
    db.query(models.ScheduleItem).delete()
    db.query(models.Seat).delete()
    db.query(models.ClassCadre).delete()
    db.query(models.Student).delete()
    db.query(models.ClassModel).delete()
    db.query(models.Subject).delete()
    db.commit()

    # ---- 科目 ----
    for name, short, color, full in SUBJECT_DEFS:
        db.add(models.Subject(name=name, short=short, color=color, full_score=full))
    db.commit()
    subj_map = {}
    for s in db.query(models.Subject).all():
        subj_map[s.name] = s

    # ---- 班级：三个班 ----
    class_specs = [
        ("初二(1)班", "初二", 42, "学习氛围浓厚"),
        ("初二(2)班", "初二", 44, ""),
        ("初二(3)班", "初二", 46, "重点文艺班"),
    ]
    classes = []
    for cname, grade, count, remark in class_specs:
        c = models.ClassModel(name=cname, grade=grade, remark=remark, head_teacher_id=admin.id)
        db.add(c)
        db.commit()
        db.refresh(c)
        classes.append(c)

    # ---- 学生：每个班生成，性别交替使接近均衡 ----
    student_by_class = {}   # class_id -> [Student]
    no_counter = [0]
    for ci, cls in enumerate(classes):
        count = class_specs[ci][2]
        stus = []
        used_names = set()
        for i in range(count):
            no_counter[0] += 1
            is_male = i % 2 == 0
            # 保证班内不重名
            for _ in range(200):
                name = make_name(is_male)
                if name not in used_names:
                    break
            used_names.add(name)
            bd = date(random.randint(2010, 2012), random.randint(1, 12), random.randint(1, 28))
            stu = models.Student(
                class_id=cls.id,
                student_no=f"2026{ci + 1}{i + 1:02d}",
                name=name,
                gender="M" if is_male else "F",
                birth_date=bd,
                guardian="家长" + name[:2],
                phone=f"1{random.randint(3,9)}{random.randint(100000000,999999999)}",
                guardian_phone2=f"1{random.randint(3,9)}{random.randint(100000000,999999999)}",
                address=f"{random.randint(1,30)}栋{random.randint(101,2501)}",
            )
            db.add(stu)
            stus.append(stu)
        db.commit()
        student_by_class[cls.id] = stus

    # ---- 班干部 ----
    for cls in classes:
        stus = student_by_class[cls.id]
        for role, _ in CADRE_TEMPLATE:
            stu = random.choice(stus)
            db.add(models.ClassCadre(class_id=cls.id, role=role, student_id=stu.id,
                                     note="协助班主任管理班级"))

    # ---- 座位：7 x 7 ----
    for cls in classes:
        stus = student_by_class[cls.id]
        idx = 0
        for row in range(1, 8):
            for col in range(1, 8):
                if idx < len(stus):
                    db.add(models.Seat(class_id=cls.id, student_id=stus[idx].id,
                                       row=row, col=col))
                    idx += 1

    # ---- 课程表：每班周一到周五，每天 6 节（语数英 + 3 门副科随机）----
    for cls in classes:
        extras_pool = [s for s in subj_map.values() if s.name not in ("语文", "数学", "英语")]
        for d in range(5):
            day = [subj_map["语文"], subj_map["数学"], subj_map["英语"]]
            extras = random.sample(extras_pool, min(3, len(extras_pool)))
            day.extend(extras)
            for p, subj in enumerate(day, start=1):
                db.add(models.ScheduleItem(class_id=cls.id, weekday=d + 1, period=p,
                                           subject_id=subj.id, teacher=random.choice(TEACHERS)))
    db.commit()

    # ---- 考试：3 次 + 成绩：每科每人 ----
    dates = [date(2026, 5, 20), date(2026, 9, 20), date(2026, 11, 15)]
    names = ["上学期期中", "上学期期末", "本学期期中"]
    for cls in classes:
        stus = student_by_class[cls.id]
        ability = {s.id: random.gauss(0.62, 0.10) for s in stus}
        for ei, (edate, exam_name) in enumerate(zip(dates, names)):
            exam = models.Exam(class_id=cls.id, name=exam_name, date=edate)
            db.add(exam)
            db.commit()
            db.refresh(exam)
            for st in stus:
                a = ability[st.id] + ei * 0.012 + random.gauss(0, 0.04)
                for subj in subj_map.values():
                    full = subj.full_score or 100
                    score = a * full + random.gauss(0, full * 0.055)
                    if random.random() < 0.04:
                        score -= full * random.uniform(0.25, 0.45)
                    score = round(max(0, min(full, score)), 1)
                    db.add(models.Score(exam_id=exam.id, class_id=cls.id,
                                        student_id=st.id, subject_id=subj.id, score=score))

    # ---- 考勤：最近 60 个自然日（工作日）----
    start = date.today() - timedelta(days=59)
    for delta in range(60):
        d = start + timedelta(days=delta)
        if d.weekday() >= 5:
            continue
        for cls in classes:
            for st in student_by_class[cls.id]:
                r = random.random()
                status = ("absent" if r < 0.02 else "late" if r < 0.06
                          else "leave" if r < 0.09 else "present")
                db.add(models.Attendance(student_id=st.id, date=d, status=status))
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        add_demo_data(db)
        for t in ["classes", "students", "subjects", "class_cadres", "seats",
                  "schedule", "exams", "scores", "attendance"]:
            n = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t}: {n}")
        print("✅ 演示数据生成完成")
    finally:
        db.close()


if __name__ == "__main__":
    main()
