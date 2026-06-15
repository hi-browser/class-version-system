import argparse
from pathlib import Path
from collections import Counter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True, help="labels 目录，例如 .../labels")
    args = parser.parse_args()

    label_root = Path(args.labels)
    counter = Counter()
    bad_lines = []

    for txt_path in label_root.rglob("*.txt"):
        for idx, line in enumerate(txt_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                bad_lines.append((str(txt_path), idx, line))
                continue
            try:
                cls_id = int(float(parts[0]))
                nums = [float(x) for x in parts[1:]]
            except ValueError:
                bad_lines.append((str(txt_path), idx, line))
                continue
            counter[cls_id] += 1
            if any(x < 0 or x > 1 for x in nums):
                bad_lines.append((str(txt_path), idx, line))

    print("类别统计：")
    for cls_id, count in sorted(counter.items()):
        print(f"class {cls_id}: {count}")

    print(f"异常行数量：{len(bad_lines)}")
    for item in bad_lines[:20]:
        print(item)

if __name__ == "__main__":
    main()
