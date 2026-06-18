import pymysql
import sys

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
            AND TABLE_NAME = 'class_group'
            AND COLUMN_NAME = 'course_name'
        """)
        has_course_name = cursor.fetchone()[0] > 0

        need_rebuild = not has_course_name
        if has_course_name:
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'classroom_vision'
                AND TABLE_NAME = 'class_group'
                AND COLUMN_NAME = 'teacher_id'
            """)
            has_teacher_id = cursor.fetchone()[0] > 0
            if not has_teacher_id:
                need_rebuild = True
                print("\n⚠ class_group 表缺少 teacher_id 列，需要重建...")
            else:
                print("- class_group 表已是最新结构，跳过")

        if need_rebuild:
            print("⚠ 正在重建 class_group / course / class_session 表（旧数据将丢失）")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("DROP TABLE IF EXISTS class_session")
            cursor.execute("DROP TABLE IF EXISTS course")
            cursor.execute("DROP TABLE IF EXISTS class_group")
            cursor.execute("""
                CREATE TABLE class_group (
                  id INT PRIMARY KEY AUTO_INCREMENT,
                  course_name VARCHAR(20) NOT NULL,
                  teacher_id INT NOT NULL,
                  student_count INT NOT NULL DEFAULT 0,
                  CONSTRAINT fk_cg_teacher FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE course (
                  id INT PRIMARY KEY AUTO_INCREMENT,
                  class_group_id INT NULL,
                  date DATE NOT NULL,
                  time_slot INT NOT NULL,
                  location VARCHAR(50) NOT NULL,
                  CONSTRAINT fk_course_cg FOREIGN KEY (class_group_id) REFERENCES class_group(id) ON DELETE SET NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE class_session (
                  id INT PRIMARY KEY AUTO_INCREMENT,
                  course_id INT NULL,
                  class_id INT NULL,
                  session_time DATETIME NULL,
                  location VARCHAR(50),
                  source_type VARCHAR(20) NOT NULL,
                  source_path VARCHAR(255) NOT NULL,
                  result_path VARCHAR(255),
                  expected_count INT NOT NULL DEFAULT 0,
                  detected_count INT NOT NULL DEFAULT 0,
                  attendance_rate FLOAT NOT NULL DEFAULT 0,
                  participation_rate FLOAT NOT NULL DEFAULT 0,
                  abnormal_rate FLOAT NOT NULL DEFAULT 0,
                  phone_rate FLOAT NOT NULL DEFAULT 0,
                  head_down_rate FLOAT NOT NULL DEFAULT 0,
                  behavior_json TEXT,
                  trend_json TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  CONSTRAINT fk_session_course FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE SET NULL,
                  CONSTRAINT fk_session_class FOREIGN KEY (class_id) REFERENCES class_group(id) ON DELETE SET NULL
                )
            """)
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("✓ class_group / course / class_session 表已重建")

    conn.commit()
    print("\n数据库迁移完成！")
except Exception as e:
    print(f"\n❌ 迁移失败: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()