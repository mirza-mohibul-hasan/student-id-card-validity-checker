from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.image_preprocessing import preprocess_image_nlp
from app.ocr_service import detect_text_regions_nlp, extract_text_by_region_nlp
from app.ner_service import extract_fields_nlp
from app.logger import app_logger
import difflib
import easyocr
import re
import cv2
from ultralytics import YOLO

reader = easyocr.Reader(['en'])
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route("/")
def server_test():
    return jsonify({"message": "Server is running"})


@app.route('/process-image-nlp', methods=['POST'])
def process_image_nlp():
    if 'image' not in request.files:
        app_logger.error('No image part')
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    name_input = request.form.get('name', '')
    university_input = request.form.get('university', '')

    if file.filename == '':
        app_logger.error('No selected file')
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app_logger.info(f'Image saved to {file_path}')

        try:
            _, original_image = preprocess_image_nlp(file_path)
            regions = detect_text_regions_nlp(original_image)
            lines = extract_text_by_region_nlp(regions)
            fields = extract_fields_nlp(lines)

            # Validate input data against extracted data
            validation_results = validate_data__nlp(
                fields, name_input, university_input)
            app_logger.info("Extraction and validation successful")
            return jsonify(validation_results), 200
        except Exception as e:
            app_logger.error(f"Processing error: {str(e)}")
            return jsonify({"error": "Failed to process image"}), 500


def validate_data__nlp(extracted_fields, name_input, university_input):
    name_extracted = extracted_fields.get('Name') or "Not Recognised"
    university_extracted = extracted_fields.get(
        'University') or "Not Recognised"
    expiration_extracted = extracted_fields.get(
        'Expiration') or "Not Recognised"

    name_similarity = (
        calculate_similarity_nlp(name_input, name_extracted)
        if name_extracted != "Not Recognised" else "Not Recognised"
    )
    university_similarity = (
        calculate_similarity_nlp(university_input, university_extracted)
        if university_extracted != "Not Recognised" else "Not Recognised"
    )
    expiration_status = check_expiration_nlp(expiration_extracted)

    # Determine if the overall card is valid based on these results
    results = {
        "fields": {
            "Name": name_extracted,
            "University": university_extracted,
            "Expiration": expiration_extracted
        },
        "name_match": name_similarity,
        "university_match": university_similarity,
        "is_expired": expiration_status,
        "is_valid_card": determine_overall_validity_nlp({
            "name_match": name_similarity,
            "university_match": university_similarity,
            "is_expired": expiration_status
        })
    }
    return results


def calculate_similarity_nlp(input_text, extracted_text):
    similarity = difflib.SequenceMatcher(
        None, input_text.lower(), extracted_text.lower()).ratio()
    return round(similarity * 100, 2)


def check_expiration_nlp(expiration_date_str):
    if expiration_date_str == "Not Recognised":
        return True
    try:
        expiration_date = datetime.strptime(expiration_date_str, "%m/%d/%Y")
        return expiration_date < datetime.now()
    except ValueError:
        return True  # If the expiration date is invalid or unrecognized, mark as expired


def determine_overall_validity_nlp(validation_results):
    if validation_results['name_match'] == "Not Recognised" or validation_results['university_match'] == "Not Recognised" or validation_results['is_expired']:
        return False

    name_threshold = 70
    university_threshold = 70

    name_valid = validation_results['name_match'] >= name_threshold
    university_valid = validation_results['university_match'] >= university_threshold
    expiration_valid = not validation_results['is_expired']

    return name_valid and university_valid and expiration_valid

# YOLO


def remove_special_characters_yolo(text):
    return re.sub(r'[^A-Za-z0-9\s/]', '', text)


# Function to correct common OCR mistakes
def correct_ocr_mistakes_yolo(text):
    corrections = {'0': 'O', '1': 'I', '5': 'S'}
    for incorrect, correct in corrections.items():
        text = text.replace(incorrect, correct)
    return text


# Function to clean date formats
def clean_date_format_yolo(text):
    return re.sub(r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f'{int(m.group(1)):02}/{int(m.group(2)):02}/{m.group(3)}', text)


# Function to clean OCR text (combining all steps)
def clean_ocr_text_yolo(text):
    text = remove_special_characters_yolo(text)
    text = correct_ocr_mistakes_yolo(text)
    text = clean_date_format_yolo(text)
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
            result = [clean_ocr_text_yolo(text) for text in result]

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


@app.route('/process-image-yolo', methods=['POST'])
def process_image_yolo():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    name_input = request.form.get('name', '')
    university_input = request.form.get('university', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Path to save the image with bounding boxes
        save_image_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 'detected_' + filename)

        # Initialize the YOLO model
        model = YOLO(r'runs/detect/train2/weights/best.pt')

        try:
            # Detect text regions using YOLO, extract text using OCR, and save image
            extracted_texts = extract_text_from_yolo(
                file_path, model, save_image_path)

            # Validate input data against extracted data
            validation_results = validate_data_yolo(
                extracted_texts, name_input, university_input)

            return jsonify(validation_results), 200
        except Exception as e:
            return jsonify({"error": f"Failed to process image: {str(e)}"}), 500


def validate_data_yolo(extracted_fields, name_input, university_input):
    # Handle null values for extracted fields
    name_extracted = ' '.join(
        extracted_fields.get('Name', [])) or "Not Recognised"
    university_extracted = ' '.join(
        extracted_fields.get('University', [])) or "Not Recognised"
    expiration_extracted = ' '.join(
        extracted_fields.get('Expiration', [])) or "Not Recognised"

    name_similarity = (
        calculate_similarity_yolo(name_input, name_extracted)
        if name_extracted != "Not Recognised" else "Not Recognised"
    )
    university_similarity = (
        calculate_similarity_yolo(university_input, university_extracted)
        if university_extracted != "Not Recognised" else "Not Recognised"
    )
    expiration_status = check_expiration_yolo(expiration_extracted)

    # Determine if the overall card is valid based on these results
    results = {
        "fields": {
            "Name": name_extracted,
            "University": university_extracted,
            "Expiration": expiration_extracted
        },
        "name_match": name_similarity,
        "university_match": university_similarity,
        "is_expired": expiration_status,
        "is_valid_card": determine_overall_validity_yolo({
            "name_match": name_similarity,
            "university_match": university_similarity,
            "is_expired": expiration_status
        })
    }
    return results


def calculate_similarity_yolo(input_text, extracted_text):
    if input_text and extracted_text != "Not Recognised":
        similarity = difflib.SequenceMatcher(
            None, input_text.lower(), extracted_text.lower()).ratio()
        return round(similarity * 100, 2)
    return "Not Recognised"


def check_expiration_yolo(expiration_date_str):
    # Mark as expired (True) if expiration is "Not Recognised"
    if expiration_date_str == "Not Recognised":
        return True
    try:
        expiration_date = datetime.strptime(expiration_date_str, "%m/%d/%Y")
        return expiration_date < datetime.now()
    except ValueError:
        return True  # If the expiration date is invalid or unrecognized, mark as expired


def determine_overall_validity_yolo(validation_results):
    # Mark the card as invalid if any field is "Not Recognised" or expired
    if validation_results['name_match'] == "Not Recognised" or validation_results['university_match'] == "Not Recognised" or validation_results['is_expired']:
        return False

    # Define thresholds for name and university matching
    name_threshold = 70
    university_threshold = 70

    name_valid = validation_results['name_match'] >= name_threshold
    university_valid = validation_results['university_match'] >= university_threshold
    expiration_valid = not validation_results['is_expired']

    return name_valid and university_valid and expiration_valid


if __name__ == "__main__":
    app.run(debug=True)
