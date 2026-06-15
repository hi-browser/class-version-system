import json
import random
import shutil
from pathlib import Path
from typing import Dict, Any, List

import cv2
import numpy as np

from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.cv.labels import CLASS_CN, CLASS_NAMES, POSITIVE_CLASSES, ABNORMAL_CLASSES, PHONE_CLASSES, HEAD_DOWN_CLASSES

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


class ClassroomAnalyzer:
    def __init__(self):
        self.model = None
        self.model_path = Path(settings.MODEL_PATH)
        self.result_dir = Path(settings.RESULT_DIR)
        self.result_dir.mkdir(parents=True, exist_ok=True)

    def _load_model(self):
        if settings.MOCK_ANALYSIS:
            return None
        if YOLO is None:
            raise RuntimeError("未安装 ultralytics，请先 pip install ultralytics")
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型权重不存在：{self.model_path}")
        if self.model is None:
            self.model = YOLO(str(self.model_path))
        return self.model

    def analyze_file(self, file_path: str, source_type: str, expected_count: int = 0) -> Dict[str, Any]:
        if settings.MOCK_ANALYSIS:
            if source_type == "video":
                return self._mock_video_result(file_path, expected_count)
            return self._mock_image_result(file_path, expected_count)

        if source_type == "video":
            return self.analyze_video(file_path, expected_count)
        return self.analyze_image(file_path, expected_count)

    def analyze_image(self, image_path: str, expected_count: int = 0) -> Dict[str, Any]:
        model = self._load_model()
        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError("图片读取失败")

        results = model.predict(source=image_path, conf=settings.CONF_THRESHOLD, save=False, verbose=False)
        detections = []
        behavior_counts = {str(i): 0 for i in CLASS_NAMES.keys()}

        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                detections.append({
                    "class_id": cls_id,
                    "class_name": CLASS_NAMES.get(cls_id, f"class_{cls_id}"),
                    "name_cn": CLASS_CN.get(cls_id, f"类别{cls_id}"),
                    "confidence": round(conf, 4),
                    "bbox": [x1, y1, x2, y2],
                })
                behavior_counts[str(cls_id)] = behavior_counts.get(str(cls_id), 0) + 1
                self._draw_box(image, x1, y1, x2, y2, CLASS_CN.get(cls_id, str(cls_id)), conf)

        result_path = self._save_result_image(image, image_path)
        return self._build_summary(
            expected_count=expected_count,
            behavior_counts=behavior_counts,
            result_path=result_path,
            detections=detections,
            trend=[]
        )

    def analyze_video(self, video_path: str, expected_count: int = 0) -> Dict[str, Any]:
        model = self._load_model()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("视频读取失败")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        interval = max(1, int(fps * settings.FRAME_INTERVAL_SECONDS))
        frame_index = 0
        trend = []
        total_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
        first_result_path = None

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % interval != 0:
                frame_index += 1
                continue

            temp_path = self.result_dir / f"temp_frame_{Path(video_path).stem}_{frame_index}.jpg"
            cv2.imwrite(str(temp_path), frame)
            results = model.predict(source=str(temp_path), conf=settings.CONF_THRESHOLD, save=False, verbose=False)

            frame_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                    frame_counts[str(cls_id)] = frame_counts.get(str(cls_id), 0) + 1
                    self._draw_box(frame, x1, y1, x2, y2, CLASS_CN.get(cls_id, str(cls_id)), conf)

            for k, v in frame_counts.items():
                total_counts[k] = total_counts.get(k, 0) + v

            frame_total = sum(frame_counts.values())
            time_sec = round(frame_index / fps, 2)
            trend.append({
                "time": time_sec,
                "detected_count": frame_total,
                "participation_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in POSITIVE_CLASSES), frame_total),
                "abnormal_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in ABNORMAL_CLASSES), frame_total),
                "phone_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in PHONE_CLASSES), frame_total),
            })

            if first_result_path is None:
                first_result_path = self._save_result_image(frame, video_path, suffix=f"frame_{frame_index}")

            try:
                temp_path.unlink()
            except Exception:
                pass
            frame_index += 1

        cap.release()

        # 视频的行为总数按抽样帧累加；课堂人数取抽样帧平均检测人数。
        if trend:
            avg_count = round(sum(item["detected_count"] for item in trend) / len(trend))
        else:
            avg_count = 0

        summary = self._build_summary(
            expected_count=expected_count,
            behavior_counts=total_counts,
            result_path=first_result_path,
            detections=[],
            trend=trend
        )
        summary["detected_count"] = avg_count
        summary["attendance_rate"] = self._rate(avg_count, expected_count)
        return summary

    def _build_summary(self, expected_count: int, behavior_counts: Dict[str, int], result_path: str, detections: List[Dict], trend: List[Dict]) -> Dict[str, Any]:
        total = sum(behavior_counts.values())
        positive = sum(behavior_counts.get(str(i), 0) for i in POSITIVE_CLASSES)
        abnormal = sum(behavior_counts.get(str(i), 0) for i in ABNORMAL_CLASSES)
        phone = sum(behavior_counts.get(str(i), 0) for i in PHONE_CLASSES)
        head_down = sum(behavior_counts.get(str(i), 0) for i in HEAD_DOWN_CLASSES)

        behavior_list = []
        for cls_id, code in CLASS_NAMES.items():
            count = behavior_counts.get(str(cls_id), 0)
            behavior_list.append({
                "class_id": cls_id,
                "code": code,
                "name": CLASS_CN.get(cls_id, code),
                "count": count,
                "rate": self._rate(count, total),
            })

        return {
            "detected_count": total,
            "expected_count": expected_count,
            "attendance_rate": self._rate(total, expected_count),
            "participation_rate": self._rate(positive, total),
            "abnormal_rate": self._rate(abnormal, total),
            "phone_rate": self._rate(phone, total),
            "head_down_rate": self._rate(head_down, total),
            "behavior_counts": behavior_list,
            "detections": detections,
            "trend": trend,
            "result_path": result_path,
        }

    def _mock_image_result(self, file_path: str, expected_count: int = 0):
        result_path = self._copy_as_result(file_path)
        total = random.randint(25, 55)
        counts = {
            "0": random.randint(0, 5),
            "1": random.randint(5, 15),
            "2": random.randint(5, 18),
            "3": random.randint(0, 5),
            "4": random.randint(2, 10),
            "5": random.randint(0, 4),
        }
        return self._build_summary(expected_count, counts, result_path, [], [])

    def _mock_video_result(self, file_path: str, expected_count: int = 0):
        result_path = self._copy_as_result(file_path, suffix="mock")
        trend = []
        total_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
        for t in range(0, 60, settings.FRAME_INTERVAL_SECONDS):
            frame_counts = {
                "0": random.randint(0, 5),
                "1": random.randint(5, 15),
                "2": random.randint(5, 18),
                "3": random.randint(0, 5),
                "4": random.randint(2, 10),
                "5": random.randint(0, 4),
            }
            for k, v in frame_counts.items():
                total_counts[k] += v
            total = sum(frame_counts.values())
            trend.append({
                "time": t,
                "detected_count": total,
                "participation_rate": self._rate(frame_counts["0"] + frame_counts["1"] + frame_counts["2"], total),
                "abnormal_rate": self._rate(frame_counts["3"] + frame_counts["4"] + frame_counts["5"], total),
                "phone_rate": self._rate(frame_counts["3"], total),
            })
        summary = self._build_summary(expected_count, total_counts, result_path, [], trend)
        summary["detected_count"] = round(sum(x["detected_count"] for x in trend) / len(trend))
        summary["attendance_rate"] = self._rate(summary["detected_count"], expected_count)
        return summary

    def _get_chinese_font(self, size=20):
        font_candidates = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
        for font_path in font_candidates:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()

    def _draw_chinese_text(self, image, text, position, font_size=20):
        # OpenCV 是 BGR，PIL 是 RGB，需要转换
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_img)
        font = self._get_chinese_font(font_size)

        x, y = position

        # 文字背景
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle(
            [bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2],
            fill=(255, 180, 0)
        )

        # 文字
        draw.text((x, y), text, font=font, fill=(0, 0, 0))

        # 转回 OpenCV BGR
        image[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def _draw_box(self, image, x1, y1, x2, y2, label, conf):
        color = (0, 180, 255)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        text = f"{label} {conf:.2f}"
        text_y = max(5, y1 - 24)
        self._draw_chinese_text(image, text, (x1, text_y), font_size=18)

    def _save_result_image(self, image, source_path: str, suffix="result"):
        p = Path(source_path)
        filename = f"{p.stem}_{suffix}.jpg"
        out = self.result_dir / filename
        cv2.imwrite(str(out), image)
        return f"static/results/{filename}"

    def _copy_as_result(self, source_path: str, suffix="result"):
        p = Path(source_path)
        filename = f"{p.stem}_{suffix}{p.suffix}"
        out = self.result_dir / filename
        shutil.copyfile(p, out)
        return f"static/results/{filename}"

    @staticmethod
    def _rate(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator * 100, 2)


analyzer = ClassroomAnalyzer()
