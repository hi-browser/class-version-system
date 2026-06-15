from pathlib import Path

from app.core.database import SessionLocal
from app.models.class_session import ClassSession


BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "app" / "static" / "uploads"
RESULT_DIR = BASE_DIR / "app" / "static" / "results"


def normalize_path(path: str | None) -> str | None:
    """
    统一数据库里的路径格式，方便比较。
    例如：
    static/uploads/a.jpg
    /static/uploads/a.jpg
    app/static/uploads/a.jpg
    """
    if not path:
        return None

    path = path.replace("\\", "/").lstrip("/")

    if path.startswith("app/static/"):
        path = path.replace("app/static/", "static/", 1)

    return path


def collect_used_files():
    """
    从数据库 class_session 表中收集仍然被引用的图片路径。
    """
    db = SessionLocal()
    used = set()

    try:
        sessions = db.query(ClassSession).all()

        for session in sessions:
            source_path = normalize_path(session.source_path)
            result_path = normalize_path(session.result_path)

            if source_path:
                used.add(source_path)

            if result_path:
                used.add(result_path)

    finally:
        db.close()

    return used


def clean_directory(directory: Path, static_prefix: str, used_files: set[str], dry_run: bool = True):
    """
    清理某个目录下没有被数据库引用的文件。
    """
    if not directory.exists():
        print(f"目录不存在，跳过：{directory}")
        return 0

    deleted_count = 0

    for file_path in directory.iterdir():
        if not file_path.is_file():
            continue

        relative_static_path = f"{static_prefix}/{file_path.name}".replace("\\", "/")

        if relative_static_path not in used_files:
            if dry_run:
                print(f"[预览] 将删除：{file_path}")
            else:
                print(f"[删除] {file_path}")
                file_path.unlink()

            deleted_count += 1

    return deleted_count


def main():
    print("开始扫描数据库中仍然引用的图片...")
    used_files = collect_used_files()

    print(f"数据库中仍然引用的文件数量：{len(used_files)}")
    print()

    print("第一步：预览将要删除的孤儿文件")
    print("-" * 60)

    upload_count = clean_directory(
        UPLOAD_DIR,
        "static/uploads",
        used_files,
        dry_run=True,
    )

    result_count = clean_directory(
        RESULT_DIR,
        "static/results",
        used_files,
        dry_run=True,
    )

    total_count = upload_count + result_count

    print("-" * 60)
    print(f"预览完成，共发现 {total_count} 个孤儿文件。")
    print()

    if total_count == 0:
        print("没有需要清理的文件。")
        return

    confirm = input("确认删除这些文件吗？输入 YES 继续删除：")

    if confirm != "YES":
        print("已取消删除。")
        return

    print()
    print("开始正式删除...")
    print("-" * 60)

    clean_directory(
        UPLOAD_DIR,
        "static/uploads",
        used_files,
        dry_run=False,
    )

    clean_directory(
        RESULT_DIR,
        "static/results",
        used_files,
        dry_run=False,
    )

    print("-" * 60)
    print("清理完成。")


if __name__ == "__main__":
    main()