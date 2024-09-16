import cv2
from app.logger import app_logger

""" Image Preprocess for NLP """


def preprocess_image_nlp(image_path):
    try:
        app_logger.info(f"Starting preprocessing of image: {image_path}")
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        app_logger.info("Image preprocessing completed successfully.")
        return thresh, img
    except Exception as e:
        app_logger.error(f"Error during image preprocessing: {str(e)}")
        raise


""" IMAGE PREPROCESS FOR YOLO """
