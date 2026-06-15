from pathlib import Path
from collections import Counter
 
label_root = Path(r"E:\BaiduNetdiskDownload\SCB-Dataset3 yolo dataset\0.355k_university_yolo_Dataset\labels")

counter = Counter()

for txt_path in label_root.rglob("*.txt"):
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                counter[int(parts[0])] += 1

print("类别统计：")
for cls_id, count in sorted(counter.items()):
    print(cls_id, count)