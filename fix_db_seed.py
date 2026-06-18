import pymysql
from passlib.context import CryptContext
from datetime import date, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
admin_password_hash = pwd_context.hash("admin123")

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="1234",
    database="classroom_vision",
    charset="utf8mb4"
)

try:
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE class_session;")
        cursor.execute("TRUNCATE TABLE course;")
        cursor.execute("TRUNCATE TABLE class_group;")
        cursor.execute("TRUNCATE TABLE behavior_category;")
        cursor.execute("TRUNCATE TABLE users;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        cursor.execute(
            """
            INSERT INTO users(email, name, password_hash, role, is_verified)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("admin@example.com", "系统管理员", admin_password_hash, "admin", True)
        )

        teacher1_pwd = pwd_context.hash("123456")
        cursor.executemany(
            """
            INSERT INTO users(email, name, password_hash, role, is_verified)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                ("zhang@example.com", "张老师", teacher1_pwd, "teacher", True),
                ("li@example.com", "李老师", teacher1_pwd, "teacher", True),
            ]
        )
        teacher_ids = [cursor.lastrowid - 1, cursor.lastrowid]

        cursor.executemany(
            """
            INSERT INTO class_group(course_name, teacher_id, student_count)
            VALUES (%s, %s, %s)
            """,
            [
                ("高等数学", teacher_ids[0], 45),
                ("人工智能基础", teacher_ids[1], 50),
            ]
        )

        today = date.today()
        cursor.executemany(
            """
            INSERT INTO course(class_group_id, date, time_slot, location)
            VALUES (%s, %s, %s, %s)
            """,
            [
                (1, today + timedelta(days=1), 1, "教学楼A301"),
                (1, today + timedelta(days=1), 3, "教学楼A301"),
                (2, today + timedelta(days=2), 2, "教学楼B205"),
                (2, today + timedelta(days=2), 4, "教学楼B205"),
            ]
        )

        cursor.executemany(
            """
            INSERT INTO behavior_category(class_id, code, name_cn, is_positive)
            VALUES (%s, %s, %s, %s)
            """,
            [
                (0, "hand_raising", "举手互动", True),
                (1, "reading", "阅读/看书", True),
                (2, "writing", "低头书写", True),
                (3, "using_phone", "使用手机", False),
                (4, "bowing_head", "低头状态", False),
                (5, "leaning_over_table", "趴桌/疑似睡觉", False),
            ]
        )

    conn.commit()
    print("数据库初始化数据修复完成。")
    print("默认管理员账号: admin@example.com / admin123")
    print("教师账号: zhang@example.com / 123456  |  li@example.com / 123456")
    print("示例排课: 高等数学(张老师) 明天第1/3节 A301 | 人工智能基础(李老师) 后天第2/4节 B205")

finally:
    conn.close()