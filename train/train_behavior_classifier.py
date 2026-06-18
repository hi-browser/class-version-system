"""
训练行为分类器 (ResNet18)
从 SCB 数据集中裁剪每个人框，按需加载，大幅提速
"""

import argparse
from pathlib import Path
from collections import Counter

import cv2
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm

CLASS_NAMES = {
    0: "hand_raising", 1: "reading", 2: "writing",
    3: "using_phone", 4: "bowing_head", 5: "leaning_over_table",
}
NUM_CLASSES = len(CLASS_NAMES)
IMG_SIZE = 224


class BehaviorCropDataset(Dataset):
    """按需加载版：只扫描标注文件，不预加载图片"""

    def __init__(self, image_dir, label_dir, transform=None):
        self.transform = transform
        self.image_dir = Path(image_dir)
        self.label_dir = Path(label_dir)
        self.annotations = []

        for img_path in sorted(self.image_dir.glob("*")):
            if img_path.suffix.lower() not in (".png", ".jpg", ".jpeg"):
                continue
            label_path = self.label_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                continue
            with open(label_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    cls_id = int(parts[0])
                    xc, yc, bw, bh = [float(x) for x in parts[1:5]]
                    self.annotations.append((str(img_path), cls_id, xc, yc, bw, bh))

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_path, cls_id, xc, yc, bw, bh = self.annotations[idx]
        img = cv2.imread(img_path)
        if img is None:
            return torch.zeros(3, IMG_SIZE, IMG_SIZE), 0
        h, w = img.shape[:2]
        x1 = max(0, int((xc - bw / 2) * w))
        y1 = max(0, int((yc - bh / 2) * h))
        x2 = min(w, int((xc + bw / 2) * w))
        y2 = min(h, int((yc + bh / 2) * h))
        if x2 - x1 < 10 or y2 - y1 < 10:
            x2, y2 = min(x1 + 10, w), min(y1 + 10, h)
        crop = img[y1:y2, x1:x2]
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        if self.transform:
            crop = self.transform(crop)
        return crop, cls_id


def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    return transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def train_epoch(model, loader, criterion, optimizer, device, scaler=None):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in tqdm(loader, desc="Train"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        if scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Eval"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += images.size(0)
    return total_loss / total, correct / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="F:/Dataset/SCB-Dataset3_full_merged")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--device", default="0")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    data_root = Path(args.data)
    device = torch.device(f"cuda:{args.device}" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"
    print(f"Device: {device}  AMP: {use_amp}")

    train_set = BehaviorCropDataset(
        data_root / "images" / "train", data_root / "labels" / "train",
        get_transforms(train=True),
    )
    val_set = BehaviorCropDataset(
        data_root / "images" / "val", data_root / "labels" / "val",
        get_transforms(train=False),
    )
    print(f"Samples: train={len(train_set)}  val={len(val_set)}")

    train_loader = DataLoader(train_set, batch_size=args.batch, shuffle=True,
                              num_workers=args.workers, pin_memory=True)
    val_loader = DataLoader(val_set, batch_size=args.batch, shuffle=False,
                            num_workers=args.workers, pin_memory=True)

    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    best_acc = 0.0
    save_dir = Path("runs/behavior_classifier")
    save_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, scaler)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        print(f"Epoch {epoch:2d}/{args.epochs}  "
              f"Train Loss={train_loss:.4f} Acc={train_acc:.4f}  "
              f"Val Loss={val_loss:.4f} Acc={val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), save_dir / "best.pt")
            print(f"  -> Saved best (acc={best_acc:.4f})")

    model.eval()
    traced = torch.jit.trace(model, torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(device))
    traced.save(str(save_dir / "classifier.pt"))
    print(f"\nDone! Best val acc: {best_acc:.4f}")
    print(f"Saved to: {save_dir}")


if __name__ == "__main__":
    main()