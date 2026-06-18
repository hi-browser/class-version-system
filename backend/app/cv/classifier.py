"""
行为分类器推理模块
加载训练好的 ResNet18/MobileNetV3 分类器，对裁剪人像进行 6 类行为识别
"""

from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms


CLASS_NAMES = {
    0: "hand_raising",
    1: "reading",
    2: "writing",
    3: "using_phone",
    4: "bowing_head",
    5: "leaning_over_table",
}
CLASS_CN = {
    0: "举手互动",
    1: "阅读",
    2: "书写",
    3: "玩手机",
    4: "低头",
    5: "趴桌",
}
NUM_CLASSES = 6
IMG_SIZE = 224


class BehaviorClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.model_path = model_path
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(self, model_path=None):
        path = model_path or self.model_path
        if path is None:
            raise RuntimeError("Model path not set")
        self.model = models.resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, NUM_CLASSES)
        state_dict = torch.load(path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

    def predict_crop(self, crop_bgr):
        """对单张裁剪人像做分类，返回 (class_id, confidence)"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        tensor = self.transform(crop_rgb).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1)
            cls_id = int(probs.argmax(1).item())
            conf = float(probs[0, cls_id].item())
        return cls_id, conf

    def predict_batch(self, crops):
        """批量预测，返回 [(class_id, confidence), ...]"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        if not crops:
            return []
        tensors = []
        for crop in crops:
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            tensor = self.transform(crop_rgb)
            tensors.append(tensor)
        batch = torch.stack(tensors).to(self.device)
        with torch.no_grad():
            outputs = self.model(batch)
            probs = torch.softmax(outputs, dim=1)
            cls_ids = probs.argmax(1).tolist()
            confs = [float(probs[i, cls_id].item()) for i, cls_id in enumerate(cls_ids)]
        return list(zip(cls_ids, confs))
