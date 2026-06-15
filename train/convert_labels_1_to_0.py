import argparse
import shutil
from pathlib import Path

YAML_TEXT = '''path: {path}
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

def convert_file(src_txt: Path, dst_txt: Path):
    lines_out = []
    for line in src_txt.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        cls_id = int(float(parts[0]))
        new_cls = cls_id - 1
        if new_cls < 0:
            raise ValueError(f"{src_txt} 中出现小于 1 的类别：{cls_id}，请确认是否已经转换过")
        lines_out.append(" ".join([str(new_cls)] + parts[1:]))
    dst_txt.parent.mkdir(parents=True, exist_ok=True)
    dst_txt.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="将 YOLO 标签类别从 1~6 转为 0~5，并复制图片目录")
    parser.add_argument("--src", required=True, help="原始数据集根目录，包含 images/labels")
    parser.add_argument("--dst", required=True, help="转换后的输出目录")
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    if dst.exists():
        raise FileExistsError(f"输出目录已存在：{dst}。为避免覆盖，请删除后重试或换一个目录。")

    shutil.copytree(src / "images", dst / "images")
    for txt in (src / "labels").rglob("*.txt"):
        rel = txt.relative_to(src / "labels")
        convert_file(txt, dst / "labels" / rel)

    yaml_path = dst / "scb_dataset3.yaml"
    yaml_path.write_text(YAML_TEXT.format(path=str(dst).replace("\\", "/")), encoding="utf-8")

    print("转换完成：", dst)
    print("YAML 文件：", yaml_path)

if __name__ == "__main__":
    main()
