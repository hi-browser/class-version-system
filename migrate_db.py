import pymysql

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
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'name'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN name VARCHAR(64) NOT NULL DEFAULT ''
                AFTER email
            """)
            print("✓ users 表已添加 name 列")
        else:
            print("- users.name 列已存在，跳过")

        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'users'
            AND INDEX_NAME = 'uq_email_role'
        """)
        has_uq = cursor.fetchone()[0] > 0

        cursor.execute("""
            SELECT INDEX_NAME FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'email'
            AND NON_UNIQUE = 0
            AND INDEX_NAME != 'uq_email_role'
        """)
        old_indexes = cursor.fetchall()
        for row in old_indexes:
            cursor.execute(f"ALTER TABLE users DROP INDEX {row[0]}")
            print(f"  已删除旧唯一索引: {row[0]}")

        if not has_uq:
            cursor.execute("ALTER TABLE users ADD UNIQUE KEY uq_email_role (email, role)")
            print("✓ users 表已更新为 (email, role) 联合唯一约束")
        elif old_indexes:
            print("✓ users 表旧唯一索引已清理")
        else:
            print("- users.uq_email_role 已存在，跳过")

        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'role'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'teacher'
                AFTER password_hash
            """)
            print("✓ users 表已添加 role 列")
        else:
            print("- users.role 列已存在，跳过")

        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'course'
            AND COLUMN_NAME = 'teacher_id'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE course
                ADD COLUMN teacher_id INT NULL
                AFTER teacher_name,
                ADD CONSTRAINT fk_course_teacher
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
            """)
            print("✓ course 表已添加 teacher_id 列")
        else:
            print("- course.teacher_id 列已存在，跳过")

        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'classroom_vision'
            AND TABLE_NAME = 'class_group'
            AND COLUMN_NAME = 'teacher_id'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE class_group
                ADD COLUMN teacher_id INT NULL
                AFTER grade,
                ADD CONSTRAINT fk_class_teacher
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
            """)
            print("✓ class_group 表已添加 teacher_id 列")
        else:
            print("- class_group.teacher_id 列已存在，跳过")

    conn.commit()
    print("\n数据库迁移完成！")

finally:
    conn.close()