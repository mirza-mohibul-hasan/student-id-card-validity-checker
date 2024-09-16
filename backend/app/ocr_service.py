import easyocr
import re
from app.image_preprocessing import preprocess_image_nlp
from app.logger import app_logger
reader = easyocr.Reader(['en'])

""" OCR Service for NLP """


def detect_text_regions_nlp(image):
    try:
        app_logger.info(f"Detecting text regions in image: {image}")
        result = reader.readtext(image, detail=1)
        app_logger.info("Text detection completed successfully.")
        return result
    except Exception as e:
        app_logger.error(f"Error during text detection: {str(e)}")
        raise


def extract_text_by_region_nlp(regions):
    # Group texts by their vertical position (y-coordinate) to treat them as lines
    line_dict = {}
    for (bbox, text, prob) in regions:
        top_left = bbox[0][1]  # y-coordinate of top-left corner
        line_dict.setdefault(top_left, []).append(text)

    # Sort lines by the y-coordinate key and join texts within the same line
    sorted_lines = sorted(line_dict.items(), key=lambda item: item[0])
    lines = [' '.join(texts) for _, texts in sorted_lines]
    return lines


def clean_ocr_text_nlp(text):
    cleaned_text = re.sub(
        r'[^\w\s/]', '', text)  # Remove unexpected characters
    return cleaned_text


""" OCR SERVICE FOR YOLO """
