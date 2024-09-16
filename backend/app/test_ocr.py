from app.image_preprocessing import preprocess_image
from app.ocr_service import detect_text_regions_nlp, extract_text_by_region
from app.logger import app_logger


def main(image_path):
    _, original_image = preprocess_image(image_path)
    regions = detect_text_regions_nlp(original_image)
    lines = extract_text_by_region(regions)

    app_logger.info("\nExtracted Lines from OCR:")
    print("\nExtracted Lines from OCR:")
    for line in lines:
        print(line)
    app_logger.info(lines)


if __name__ == "__main__":
    image_path = r"I:\ML Projects\Brain House\Testing System\data\test\aiub_test.jpg"
    main(image_path)
