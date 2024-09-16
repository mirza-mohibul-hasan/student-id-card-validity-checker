import os
import cv2
from ultralytics import YOLO
import easyocr
import re

# Initialize the EasyOCR Reader for English
reader = easyocr.Reader(['en'])

# Function to remove special characters from the text


def remove_special_characters(text):
    return re.sub(r'[^A-Za-z0-9\s/]', '', text)

# Function to correct common OCR mistakes


def correct_ocr_mistakes(text):
    corrections = {'0': 'O', '1': 'I', '5': 'S'}
    for incorrect, correct in corrections.items():
        text = text.replace(incorrect, correct)
    return text

# Function to clean date formats


def clean_date_format(text):
    return re.sub(r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f'{int(m.group(1)):02}/{int(m.group(2)):02}/{m.group(3)}', text)

# Function to clean OCR text (combining all steps)


def clean_ocr_text(text):
    text = remove_special_characters(text)
    text = correct_ocr_mistakes(text)
    text = clean_date_format(text)
    return text

# Function to crop regions detected by YOLO, apply OCR, and clean text


def extract_text_from_yolo(image_path, model, save_image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image {image_path}")
        return None

    # Run YOLO inference to detect text regions
    results = model.predict(source=image_path, save=False)

    # Dictionary to store texts class-wise
    detected_text = {
        "Expiration": [],
        "Name": [],
        "University": []
    }

    # Iterate through each detected object (bounding boxes + class)
    for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
        x1, y1, x2, y2 = map(int, box)
        class_id = int(cls)

        # Crop the region from the image based on bounding box
        cropped_image = image[y1:y2, x1:x2]

        # Use EasyOCR to extract text from the cropped region
        result = reader.readtext(cropped_image, detail=0)
        if result:
            # Clean the OCR output
            result = [clean_ocr_text(text) for text in result]

            # Store cleaned text based on detected class
            if class_id == 0:  # 'Expiration'
                detected_text["Expiration"].extend(result)
            elif class_id == 1:  # 'Name'
                detected_text["Name"].extend(result)
            elif class_id == 2:  # 'University'
                detected_text["University"].extend(result)

    # Save the image with bounding boxes
    cv2.imwrite(save_image_path, image)
    print(f"Image saved with bounding boxes at {save_image_path}")

    return detected_text

# Main function to process a single image


def main(model_path, image_path, save_image_path):
    # Initialize the YOLO model with trained weights
    model = YOLO(model_path)

    try:
        # Detect text regions using YOLO, extract text using EasyOCR, and save image
        extracted_texts = extract_text_from_yolo(
            image_path, model, save_image_path)

        # Print the extracted texts based on YOLO class
        if extracted_texts:
            print(f"\nImage: {image_path}")
            print("Detected Texts:")
            for label, texts in extracted_texts.items():
                print(f"{label}: {', '.join(texts)}")

    except Exception as e:
        print(f"Failed to process {image_path}: {str(e)}")


if __name__ == "__main__":
    # Path to the trained YOLO model
    model_path = r'runs/detect/train2/weights/best.pt'

    # Path to the single test image
    image_path = r'I:\ML Projects\Brain House\Testing System\testdata\mit.jpg'

    # Path to save the image with bounding boxes
    save_image_path = r'I:\ML Projects\Brain House\ID Verification\backend\dummy_data\LIVE TEST\aiub_detected.jpg'

    # Run the main function
    main(model_path, image_path, save_image_path)
