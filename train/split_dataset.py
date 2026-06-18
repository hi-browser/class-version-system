import argparse
import random
import shutil
from pathlib import Path


def split_dataset(src_dir: str, dst_dir: str, ratio_train: float, ratio_val: float, ratio_test: float, seed: int):
    src = Path(src_dir)
    dst = Path(dst_dir)
    assert abs(ratio_train + ratio_val + ratio_test - 1.0) < 0.001, "Ratios must sum to 1.0"

    # Collect all (image, label) pairs from train and val
    pairs = []
    for split in ("train", "val"):
        img_dir = src / "images" / split
        lbl_dir = src / "labels" / split
        if not img_dir.exists():
            continue
        for img_file in img_dir.iterdir():
            if img_file.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp"):
                continue
            label_file = lbl_dir / f"{img_file.stem}.txt"
            if label_file.exists():
                pairs.append((img_file, label_file))

    print(f"Total image-label pairs: {len(pairs)}")
    random.seed(seed)
    random.shuffle(pairs)

    total = len(pairs)
    n_train = int(total * ratio_train)
    n_val = int(total * ratio_val)

    train_pairs = pairs[:n_train]
    val_pairs = pairs[n_train:n_train + n_val]
    test_pairs = pairs[n_train + n_val:]

    for split_name, split_pairs in [("train", train_pairs), ("val", val_pairs), ("test", test_pairs)]:
        img_out = dst / "images" / split_name
        lbl_out = dst / "labels" / split_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for img, lbl in split_pairs:
            shutil.copy2(img, img_out / img.name)
            shutil.copy2(lbl, lbl_out / lbl.name)
        print(f"  {split_name}: {len(split_pairs)} images")

    # Write new YAML
    yaml_src = src / "scb_dataset3.yaml"
    yaml_content = yaml_src.read_text(encoding="utf-8") if yaml_src.exists() else ""
    yaml_content = yaml_content.replace("path: F:/Dataset/SCB-Dataset3_full_merged", f"path: {dst.as_posix()}")
    yaml_out = dst / "scb_dataset3.yaml"
    yaml_out.write_text(yaml_content, encoding="utf-8")
    print(f"YAML written to {yaml_out}")
    print(f"\nTrain with: python train_yolov8s.py --data {dst}")


def main():
    parser = argparse.ArgumentParser(description="Split dataset into train/val/test")
    parser.add_argument("--src", required=True, help="Source dataset directory")
    parser.add_argument("--dst", required=True, help="Output directory")
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--val", type=float, default=0.1)
    parser.add_argument("--test", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    split_dataset(args.src, args.dst, args.train, args.val, args.test, args.seed)


if __name__ == "__main__":
    main()