import cv2
from ultralytics import YOLO


def extract_text_from_yolo(image_path, model_path):
    # Ensure model_path is correctly formatted
    # Use raw string or double slashes
    model = YOLO(
        r'I:\\ML Projects\\Brain House\\ID Verification\\backend\\models\\modelv1.pt')
    results = model.predict(image_path)

    # Assuming you want the pandas format for easier manipulation
    return results.pandas().xyxy[0]
