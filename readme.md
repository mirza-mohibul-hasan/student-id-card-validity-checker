# YOLO + NLP-Based ID Card Processing System

This project is a Flask-based application that processes ID cards to extract fields like Name, University, and Expiration Date using two approaches: YOLO + OCR and NLP + OCR. The system compares both methods and provides the best result by matching extracted fields with user input.

---

### Table of Contents

1. How the Model Works
2. Data Collection and Preprocessing
3. Model Architecture and Training Process
4. Installation
5. Usage
6. Endpoints
7. License

---

## 1. How the Model Works

This project includes two methods to extract text fields from ID cards:

- **Method 1: Spacy + OCR**:

  - **OCR** reads the text from images.
  - **OpenCV** segments the image into regions.
  - **Spacy** is used for Named Entity Recognition (NER) to detect the fields **Name**, **University**, and **Expiration** from the text.
  - Regular expressions clean the text to fix common OCR mistakes.

- **Method 2: YOLO + OCR**:
  - **YOLO** detects the regions containing **Name**, **University**, and **Expiration**.
  - **EasyOCR** reads the text from the detected regions.
  - Text is cleaned with regular expressions to improve accuracy.

The system compares the results for the selected model for the extracted fields with user-provided inputs like **name** and **university**.

---

## 2. Data Collection and Preprocessing

- **Data Collection**:

  - Data is collected from public sources and synthetic images generated using tools.
  - Google search and synthetic ID generators are used for generating the dataset.

- **Preprocessing**:
  - Images are resized to 640x640 pixels, ensuring consistent input size.
  - OpenCV is used for image preprocessing, including converting images to grayscale and applying adaptive thresholding to enhance text visibility.
  - Data augmentation includes rotation, cropping, grayscale conversion, and noise addition using **Roboflow** to generate more diverse training data.

---

## 3. Model Architecture and Training Process

### 1. YOLO + OCR:

- **YOLOv8** architecture is used for detecting text regions in the image.
- **EasyOCR** is used for reading the text from the regions detected by YOLO.

### 1. NLP + OCR:

- **Spacy**'s large language model (**en_core_web_trf**) is used for Named Entity Recognition (NER) to identify the fields Name, University, and Expiration Date.
- **EasyOCR** reads the full text from the image, which is then cleaned and processed using **Spacy**.

### 3. Training Process:

- The **YOLO** model is trained on a custom dataset using **Roboflow** for image annotation and augmentation.
- The **Spacy** model is pre-trained, so no additional training is needed for text recognition and entity extraction.

---

## 4. Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/student-id-card-validity-checker
cd student-id-card-validity-checker
```

### Step 2: Set up the environment

You can use either Conda or PIP to set up the environment.
For Conda:

```bash
conda create --name id_card_env python=3.8
conda activate id_card_env
conda env update -f environment.yml
```

For pip:

```bash
python3 -m venv id_card_env
source id_card_env/bin/activate
pip install -r requirements.txt

```

### Step 3: Install Spacy and download the required model

```bash
pip install spacy
python -m spacy download en_core_web_trf
```

## 5. Usage

### Step 1: Run the Flask app

cd backend

```bash
python app.py
```

### Step 2: Run Frontend

cd frontend

```bash
npm install
npm run dev
```

## 6. Endpoints

/process-image-nlp OR /process-image-nlp(POST):

- Upload an image to extract Name, University, and Expiration.
- Input: Image file, and optionally the name and university for comparison.
- Output: JSON response with extracted fields and comparison results.
