import pytesseract


pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"

def ocr_page(page: str):
    preds = pytesseract.image_to_string(page)
    predictions = [x for x in preds.split("\n")]
    return predictions