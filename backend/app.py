from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.image_preprocessing import preprocess_image
from app.ocr_service import detect_text_regions, extract_text_by_region
from app.ner_service import extract_fields
from app.logger import app_logger

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
    if file.filename == '':
        app_logger.error('No selected file')
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app_logger.info(f'image saved to {file_path}')

        try:
            _, original_image = preprocess_image(file_path)
            regions = detect_text_regions(original_image)
            lines = extract_text_by_region(regions)
            fields = extract_fields(lines)
            app_logger.info("Extraction successful")
            return jsonify(fields), 200
        except Exception as e:
            app_logger.error(f"processing error: {str(e)}")
            return jsonify({"error": "failed to process image"}), 500


if __name__ == "__main__":
    app.run(debug=True)
