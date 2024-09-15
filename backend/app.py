from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.image_preprocessing import preprocess_image
from app.ocr_service import detect_text_regions, extract_text_by_region
from app.ner_service import extract_fields
from app.logger import app_logger
import difflib  # To calculate similarity of strings

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route("/")
def server_test():
    return jsonify({"message": "Server is running"})


@app.route('/process-image', methods=['POST'])
def process_image():
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
            _, original_image = preprocess_image(file_path)
            regions = detect_text_regions(original_image)
            lines = extract_text_by_region(regions)
            fields = extract_fields(lines)

            # Validate input data against extracted data
            validation_results = validate_data(
                fields, name_input, university_input)
            app_logger.info("Extraction and validation successful")
            return jsonify(validation_results), 200
        except Exception as e:
            app_logger.error(f"Processing error: {str(e)}")
            return jsonify({"error": "Failed to process image"}), 500


def validate_data(extracted_fields, name_input, university_input):
    # Handle null values for extracted fields
    name_extracted = extracted_fields.get('Name') or "Not Recognised"
    university_extracted = extracted_fields.get(
        'University') or "Not Recognised"
    expiration_extracted = extracted_fields.get(
        'Expiration') or "Not Recognised"

    name_similarity = (
        calculate_similarity(name_input, name_extracted)
        if name_extracted != "Not Recognised" else "Not Recognised"
    )
    university_similarity = (
        calculate_similarity(university_input, university_extracted)
        if university_extracted != "Not Recognised" else "Not Recognised"
    )
    expiration_status = check_expiration(expiration_extracted)

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
        "is_valid_card": determine_overall_validity({
            "name_match": name_similarity,
            "university_match": university_similarity,
            "is_expired": expiration_status
        })
    }
    return results


def calculate_similarity(input_text, extracted_text):
    similarity = difflib.SequenceMatcher(
        None, input_text.lower(), extracted_text.lower()).ratio()
    return round(similarity * 100, 2)


def check_expiration(expiration_date_str):
    # Mark as expired (True) if expiration is "Not Recognised"
    if expiration_date_str == "Not Recognised":
        return True
    try:
        expiration_date = datetime.strptime(expiration_date_str, "%m/%d/%Y")
        return expiration_date < datetime.now()
    except ValueError:
        return True  # If the expiration date is invalid or unrecognized, mark as expired


def determine_overall_validity(validation_results):
    # Mark the card as invalid if any field is "Not Recognised" or expired
    if validation_results['name_match'] == "Not Recognised" or validation_results['university_match'] == "Not Recognised" or validation_results['is_expired']:
        return False

    # Define thresholds for name and university matching
    name_threshold = 70
    university_threshold = 70

    name_valid = validation_results['name_match'] >= name_threshold
    university_valid = validation_results['university_match'] >= university_threshold
    # Check if not expired
    expiration_valid = not validation_results['is_expired']

    # Return true if all checks pass
    return name_valid and university_valid and expiration_valid


if __name__ == "__main__":
    app.run(debug=True)
