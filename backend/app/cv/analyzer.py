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

    def _detect_frame(self, image: np.ndarray, use_tracking: bool = False) -> tuple:
        model = self._load_model()
        if use_tracking:
            results = model.track(
                source=image,
                conf=settings.CONF_THRESHOLD,
                persist=True,
                tracker="bytetrack.yaml",
                save=False,
                verbose=False,
            )
        else:
            results = model.predict(
                source=image, conf=settings.CONF_THRESHOLD, save=False, verbose=False
            )

        behavior_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
        detections = []

        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                track_id = None
                if use_tracking and box.id is not None:
                    track_id = int(box.id[0].item())

                if cls_id not in CLASS_NAMES:
                    continue

                behavior_counts[str(cls_id)] = behavior_counts.get(str(cls_id), 0) + 1
                det = {
                    "class_id": cls_id,
                    "class_name": CLASS_NAMES.get(cls_id, f"class_{cls_id}"),
                    "name_cn": CLASS_CN.get(cls_id, f"类别{cls_id}"),
                    "confidence": round(conf, 4),
                    "bbox": [x1, y1, x2, y2],
                }
                if track_id is not None:
                    det["track_id"] = track_id
                detections.append(det)

                label = CLASS_CN.get(cls_id, str(cls_id))
                if track_id is not None:
                    label = f"ID{track_id} {label}"
                self._draw_box(image, x1, y1, x2, y2, label, conf)

        return (image, behavior_counts, detections)

    def analyze_file(self, file_path: str, source_type: str, expected_count: int = 0) -> Dict[str, Any]:
        if settings.MOCK_ANALYSIS:
            if source_type == "video":
                return self._mock_video_result(file_path, expected_count)
            return self._mock_image_result(file_path, expected_count)

        if source_type == "video":
            return self.analyze_video(file_path, expected_count)
        return self.analyze_image(file_path, expected_count)

    def analyze_image(self, image_path: str, expected_count: int = 0) -> Dict[str, Any]:
        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError("图片读取失败")

        _, behavior_counts, detections = self._detect_frame(image)

        result_path = self._save_result_image(image, image_path)
        return self._build_summary(
            expected_count=expected_count,
            behavior_counts=behavior_counts,
            result_path=result_path,
            detections=detections,
            trend=[]
        )

    def analyze_video(self, video_path: str, expected_count: int = 0) -> Dict[str, Any]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("视频读取失败")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        interval = max(1, int(fps * settings.FRAME_INTERVAL_SECONDS))
        frame_index = 0
        trend = []
        first_result_path = None
        sampled_frames = 0
        annotated_frames = []

        track_behaviors = {}
        track_max_conf = {}

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % interval != 0:
                frame_index += 1
                continue

            sampled_frames += 1
            frame, frame_counts, frame_dets = self._detect_frame(frame, use_tracking=settings.TRACKING_ENABLED)

            for det in frame_dets:
                tid = det.get("track_id")
                if tid is not None:
                    if tid not in track_behaviors:
                        track_behaviors[tid] = []
                        track_max_conf[tid] = 0
                    track_behaviors[tid].append(det["class_id"])
                    if det["confidence"] > track_max_conf[tid]:
                        track_max_conf[tid] = det["confidence"]

            annotated_frames.append(frame.copy())

            frame_total = sum(frame_counts.values())
            time_sec = round(frame_index / fps, 2)
            trend.append({
                "time": time_sec,
                "detected_count": frame_total,
                "participation_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in POSITIVE_CLASSES), frame_total),
                "abnormal_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in ABNORMAL_CLASSES), frame_total),
                "phone_rate": self._rate(sum(frame_counts.get(str(i), 0) for i in PHONE_CLASSES), frame_total),
                "behaviors": {
                    str(cls_id): frame_counts.get(str(cls_id), 0)
                    for cls_id in CLASS_NAMES.keys()
                },
            })

            if first_result_path is None:
                first_result_path = self._save_result_image(frame, video_path, suffix=f"frame_{frame_index}")

            frame_index += 1

        cap.release()

        result_video_path = None
        if annotated_frames:
            result_video_path = self._save_result_video(annotated_frames, video_path, fps, width, height, frame_repeat=interval)

        if track_behaviors:
            unique_count = len(track_behaviors)
            behavior_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
            for tid, behaviors in track_behaviors.items():
                mode_behavior = max(set(behaviors), key=behaviors.count)
                behavior_counts[str(mode_behavior)] = behavior_counts.get(str(mode_behavior), 0) + 1
        elif trend:
            unique_count = round(sum(item["detected_count"] for item in trend) / len(trend))
            behavior_counts = {str(i): 0 for i in CLASS_NAMES.keys()}
            for item in trend:
                for k, v in item["behaviors"].items():
                    behavior_counts[k] = behavior_counts.get(k, 0) + v
            if sampled_frames > 0:
                for k in behavior_counts:
                    behavior_counts[k] = round(behavior_counts[k] / sampled_frames)
        else:
            unique_count = 0
            behavior_counts = {str(i): 0 for i in CLASS_NAMES.keys()}

        summary = self._build_summary(
            expected_count=expected_count,
            behavior_counts=behavior_counts,
            result_path=first_result_path,
            detections=[],
            trend=trend
        )
        summary["detected_count"] = unique_count
        summary["attendance_rate"] = self._rate(unique_count, expected_count)
        summary["result_video_path"] = result_video_path
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
            "analysis_text": self._generate_analysis(
                expected_count=expected_count,
                detected_count=total,
                attendance_rate=self._rate(total, expected_count),
                participation_rate=self._rate(positive, total),
                abnormal_rate=self._rate(abnormal, total),
                phone_rate=self._rate(phone, total),
                head_down_rate=self._rate(head_down, total),
                behavior_counts=behavior_list,
            ),
        }

    def _generate_analysis(self, expected_count, detected_count, attendance_rate, participation_rate, abnormal_rate, phone_rate, head_down_rate, behavior_counts):
        parts = []

        if attendance_rate >= 90:
            parts.append(f"本次课堂检测到 {detected_count} 人，到课率为 {attendance_rate}%，出勤情况良好。")
        elif attendance_rate >= 75:
            parts.append(f"本次课堂检测到 {detected_count} 人，到课率为 {attendance_rate}%，出勤情况基本正常，但仍有提升空间。")
        else:
            parts.append(f"本次课堂检测到 {detected_count} 人，到课率为 {attendance_rate}%，出勤率偏低，建议重点关注缺勤情况。")

        if participation_rate >= 60:
            parts.append(f"课堂参与率为 {participation_rate}%，学生互动参与度较高。")
        elif participation_rate >= 40:
            parts.append(f"课堂参与率为 {participation_rate}%，学生参与度中等，建议适当增加提问或讨论环节。")
        else:
            parts.append(f"课堂参与率为 {participation_rate}%，课堂活跃度偏低，建议加强互动引导。")

        if abnormal_rate >= 30:
            parts.append(f"异常行为率为 {abnormal_rate}%，课堂分心现象较明显，需重点关注手机使用、低头、趴桌等行为。")
        elif abnormal_rate >= 15:
            parts.append(f"异常行为率为 {abnormal_rate}%，存在一定分心现象，建议加强巡视提醒。")
        else:
            parts.append(f"异常行为率为 {abnormal_rate}%，课堂纪律整体较稳定。")

        if phone_rate > 0:
            parts.append(f"手机使用率为 {phone_rate}%，需留意学生是否在课堂上使用手机。")
        if head_down_rate > 0:
            parts.append(f"低头/趴桌率为 {head_down_rate}%，建议关注后排学生状态。")

        sorted_behaviors = sorted(behavior_counts, key=lambda x: x["count"], reverse=True)
        if sorted_behaviors:
            top = sorted_behaviors[0]
            if top["count"] > 0:
                top_name = top['name']
                parts.append(f"行为分布中「{top_name}」出现最多，共 {top['count']} 次，占比 {top['rate']}%。")

        parts.append("综合建议：关注后排和角落区域学生状态，通过课堂互动、巡视提醒和任务驱动方式提升课堂参与度。")

        return "".join(parts)

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
                "behaviors": {
                    str(cls_id): frame_counts.get(str(cls_id), 0)
                    for cls_id in CLASS_NAMES.keys()
                },
            })
        summary = self._build_summary(expected_count, total_counts, result_path, [], trend)
        summary["detected_count"] = round(sum(x["detected_count"] for x in trend) / len(trend))
        summary["attendance_rate"] = self._rate(summary["detected_count"], expected_count)
        summary["result_video_path"] = None
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

    def _save_result_video(self, frames: list, source_path: str, fps: float, width: int, height: int, frame_repeat: int = 1):
        p = Path(source_path)
        filename = f"{p.stem}_annotated.mp4"
        out = self.result_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(out), fourcc, fps, (width, height))
        for frame in frames:
            for _ in range(frame_repeat):
                writer.write(frame)
        writer.release()
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