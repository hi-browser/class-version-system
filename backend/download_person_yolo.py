from pathlib import Path
import shutil
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_DIR = BASE_DIR / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

model = YOLO("yolo11s.pt")

src = Path(model.ckpt_path)
dst = WEIGHTS_DIR / "person_yolo.pt"

shutil.copy(src, dst)

print(f"已保存通用人检测模型到：{dst}")