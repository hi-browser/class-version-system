import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    model = YOLO(args.weights)
    model.predict(source=args.source, conf=args.conf, save=True, show=False)

if __name__ == "__main__":
    main()
