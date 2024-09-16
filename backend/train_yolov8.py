from ultralytics import YOLO


def train_yolov8():
    epochs = 100
    image_size = 640
    batch_size = 8
    dataset_path = r"I:\ML Projects\Brain House\ID Verification\backend\data\data.yaml"
    model_path = "yolov8s.pt"  # Adjust model as necessary
    model = YOLO(model_path)
    model.train(data=dataset_path,
                imgsz=image_size,
                batch=batch_size,
                epochs=epochs,
                device=0,
                amp=False,
                plots=True)


if __name__ == "__main__":
    train_yolov8()
