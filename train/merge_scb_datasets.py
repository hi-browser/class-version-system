import argparse
import shutil
from pathlib import Path

def copy_split(src_root: Path, dst_root: Path, split: str, prefix: str):
    img_dir = src_root / "images" / split
    lab_dir = src_root / "labels" / split
    if not img_dir.exists():
        return
    for img in img_dir.iterdir():
        if img.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue
        new_name = f"{prefix}_{img.name}"
        shutil.copy2(img, dst_root / "images" / split / new_name)
        label = lab_dir / f"{img.stem}.txt"
        if label.exists():
            shutil.copy2(label, dst_root / "labels" / split / f"{Path(new_name).stem}.txt")

def main():
    parser = argparse.ArgumentParser(description="合并多个已经转换为 0-based 的 SCB YOLO 数据集")
    parser.add_argument("--srcs", nargs="+", required=True, help="多个数据集根目录")
    parser.add_argument("--dst", required=True)
    args = parser.parse_args()

    dst = Path(args.dst)
    for split in ["train", "val"]:
        (dst / "images" / split).mkdir(parents=True, exist_ok=True)
        (dst / "labels" / split).mkdir(parents=True, exist_ok=True)

    for i, src in enumerate(args.srcs, start=1):
        copy_split(Path(src), dst, "train", f"d{i}")
        copy_split(Path(src), dst, "val", f"d{i}")

    yaml_text = f'''path: {str(dst).replace("\\", "/")}
train: images/train
val: images/val

nc: 6
names:
  0: hand_raising
  1: reading
  2: writing
  3: using_phone
  4: bowing_head
  5: leaning_over_table
'''
    (dst / "scb_dataset3.yaml").write_text(yaml_text, encoding="utf-8")
    print("合并完成：", dst)

if __name__ == "__main__":
    main()
