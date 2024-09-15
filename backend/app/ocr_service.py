import easyocr
from image_preprocessing import preprocess_image
from logger import app_logger
reader = easyocr.Reader(['en'])


def detect_text_regions(image):
    try:
        app_logger.info(f"Detecting text regions in image: {image}")
        result = reader.readtext(image, detail=1)
        app_logger.info("Text detection completed successfully.")
        return result
    except Exception as e:
        app_logger.error(f"Error during text detection: {str(e)}")
        raise


def extract_text_by_region(regions):
    # Group texts by their vertical position (y-coordinate) to treat them as lines
    line_dict = {}
    for (bbox, text, prob) in regions:
        top_left = bbox[0][1]  # y-coordinate of top-left corner
        line_dict.setdefault(top_left, []).append(text)

    # Sort lines by the y-coordinate key and join texts within the same line
    sorted_lines = sorted(line_dict.items(), key=lambda item: item[0])
    lines = [' '.join(texts) for _, texts in sorted_lines]
    return lines
