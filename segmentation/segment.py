from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="../yolo_dataset/macro_seg.yaml",
    epochs=10,
    imgsz=640,
    batch=4,
    pretrained=True,
    name="YOLOv8n-macro-seg"
)

metric = model.val()
print(metric)