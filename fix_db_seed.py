import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    database="classroom_vision",
    charset="utf8mb4"
)

try:
    with conn.cursor() as cursor:
        # 清空已有数据，避免乱码残留
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE class_session;")
        cursor.execute("TRUNCATE TABLE behavior_category;")
        cursor.execute("TRUNCATE TABLE class_group;")
        cursor.execute("TRUNCATE TABLE course;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 插入课程
        cursor.executemany(
            """
            INSERT INTO course(course_name, teacher_name, description)
            VALUES (%s, %s, %s)
            """,
            [
                ("计算机视觉导论", "张老师", "智慧课堂测试课程"),
                ("人工智能基础", "李老师", "课堂行为统计演示课程"),
            ]
        )

        # 插入班级
        cursor.executemany(
            """
            INSERT INTO class_group(class_name, expected_count, major, grade)
            VALUES (%s, %s, %s, %s)
            """,
            [
                ("软件工程2301班", 45, "软件工程", "2023级"),
                ("人工智能2302班", 50, "人工智能", "2023级"),
            ]
        )

        # 插入行为类别
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
    print("数据库中文初始化数据修复完成。")

finally:
    conn.close()