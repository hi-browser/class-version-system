import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="scb_dataset3.yaml 路径")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="0")
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project="runs/scb",
        name="scb_yolo",
    )

if __name__ == "__main__":
    main()
