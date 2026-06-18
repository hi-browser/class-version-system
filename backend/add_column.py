import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    database="classroom_vision",
)
cur = conn.cursor()
cur.execute(
    "ALTER TABLE class_session ADD COLUMN result_video_path VARCHAR(255) NULL AFTER result_path"
)
conn.commit()
conn.close()
print("OK - column added")