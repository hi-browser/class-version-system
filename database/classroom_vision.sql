SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS classroom_vision DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE classroom_vision;

DROP TABLE IF EXISTS class_session;
DROP TABLE IF EXISTS behavior_category;
DROP TABLE IF EXISTS class_group;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(128) NOT NULL,
  name VARCHAR(64) NOT NULL DEFAULT '',
  password_hash VARCHAR(256) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'teacher',
  is_verified BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  UNIQUE KEY uq_email_role (email, role)
);

CREATE TABLE course (
  id INT PRIMARY KEY AUTO_INCREMENT,
  course_name VARCHAR(100) NOT NULL,
  teacher_name VARCHAR(100),
  teacher_id INT NULL,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_course_teacher FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE class_group (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_name VARCHAR(100) NOT NULL,
  expected_count INT NOT NULL DEFAULT 0,
  major VARCHAR(100),
  grade VARCHAR(50),
  teacher_id INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_class_teacher FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE behavior_category (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_id INT NOT NULL UNIQUE,
  code VARCHAR(50) NOT NULL,
  name_cn VARCHAR(50) NOT NULL,
  is_positive BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE class_session (
  id INT PRIMARY KEY AUTO_INCREMENT,
  course_id INT NULL,
  class_id INT NULL,
  session_time DATETIME NULL,
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
);

INSERT INTO course(course_name, teacher_name, description) VALUES
('计算机视觉导论', '张老师', '智慧课堂测试课程'),
('人工智能基础', '李老师', '课堂行为统计演示课程');

INSERT INTO class_group(class_name, expected_count, major, grade) VALUES
('软件工程2301班', 45, '软件工程', '2023级'),
('人工智能2302班', 50, '人工智能', '2023级');

INSERT INTO behavior_category(class_id, code, name_cn, is_positive) VALUES
(0, 'hand_raising', '举手互动', TRUE),
(1, 'reading', '阅读/看书', TRUE),
(2, 'writing', '低头书写', TRUE),
(3, 'using_phone', '使用手机', FALSE),
(4, 'bowing_head', '低头状态', FALSE),
(5, 'leaning_over_table', '趴桌/疑似睡觉', FALSE);