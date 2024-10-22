import spacy
import re
from app.ocr_service import clean_ocr_text_nlp
nlp = spacy.load("en_core_web_trf")


def extract_fields_nlp(lines):
    name = university = expiration = None
    merged_lines = " ".join(lines)
    merged_lines = clean_ocr_text_nlp(merged_lines)

    doc = nlp(merged_lines)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    for line in lines:
        if re.search(r"University|Institute|College", line, re.I):
            university = line
            break

    for line in lines:
        clean_line = clean_ocr_text_nlp(line)
        date_match = re.search(
            r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{1,2}/\d{2})", clean_line)
        if date_match:
            expiration = date_match.group(0)
            break

    return {"Name": name, "University": university, "Expiration": expiration}
