import argparse
import subprocess
import sys
from pathlib import Path


def run_pipeline(dataset_dir: str, output_dir: str, epochs: int, batch: int, imgsz: int, device: str):
    dataset = Path(dataset_dir)
    output = Path(output_dir)
    script_dir = Path(__file__).parent

    # Step 1: Deduplicate
    print("=" * 60)
    print("Step 1: Deduplicating dataset...")
    print("=" * 60)
    subprocess.run(
        [sys.executable, str(script_dir / "deduplicate_dataset.py"), "--src", str(dataset), "--threshold", "6", "--workers", "8"],
        check=True,
    )

    # Step 2: Train
    print("=" * 60)
    print("Step 2: Training YOLOv8s...")
    print("=" * 60)
    from ultralytics import YOLO

    yaml_path = dataset / "scb_dataset3.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"Dataset YAML not found: {yaml_path}")

    model = YOLO("yolov8s.pt")
    model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=str(output),
        name="yolov8s_scb",
        patience=20,
        cos_lr=True,
        warmup_epochs=3,
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )

    # Step 3: Copy best.pt to weights/
    best_pt = output / "yolov8s_scb" / "weights" / "best.pt"
    weights_dir = Path("weights")
    weights_dir.mkdir(exist_ok=True)
    if best_pt.exists():
        import shutil
        shutil.copy2(best_pt, weights_dir / "scb_yolo.pt")
        print(f"Copied best.pt to {weights_dir / 'scb_yolo.pt'}")


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8s with deduplication")
    parser.add_argument("--data", required=True, help="Dataset root (contains scb_dataset3.yaml)")
    parser.add_argument("--output", default="train/runs", help="Output directory for training runs")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="0")
    parser.add_argument("--skip-dedup", action="store_true", help="Skip deduplication step")
    args = parser.parse_args()

    if not args.skip_dedup:
        run_pipeline(args.data, args.output, args.epochs, args.batch, args.imgsz, args.device)
    else:
        from ultralytics import YOLO
        dataset = Path(args.data)
        yaml_path = dataset / "scb_dataset3.yaml"
        model = YOLO("yolov8s.pt")
        model.train(
            data=str(yaml_path),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            project=args.output,
            name="yolov8s_scb",
            patience=20,
            cos_lr=True,
            warmup_epochs=3,
        )


if __name__ == "__main__":
    main()