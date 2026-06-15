from ultralytics import YOLO

model = YOLO("weights/person_yolo.pt")

image_path = r"F:\Dataset\SCB-Dataset3\0.671k_university_yolo_Dataset\images\train\40030299.jpg"

results = model.predict(
    source=image_path,
    conf=0.10,
    classes=[0],   # COCO 中 person 的类别编号是 0
    save=True
)

for result in results:
    person_count = len(result.boxes)
    print(f"检测到人数：{person_count}")