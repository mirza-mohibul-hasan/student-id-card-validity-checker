from image_preprocessing import preprocess_image
from ocr_service import detect_text_regions, extract_text_by_region
from ner_service import extract_fields
from logger import app_logger


def main(image_path):
    _, original_image = preprocess_image(image_path)
    regions = detect_text_regions(original_image)
    lines = extract_text_by_region(regions)

    fields = extract_fields(lines)
    print("\nExtracted Fields:")
    print(fields)


if __name__ == "__main__":
    image_path = r"I:\ML Projects\Brain House\Testing System\data\test\mit.jpg"
    main(image_path)
