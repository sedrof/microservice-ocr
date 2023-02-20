from cgitb import reset
import cv2
import numpy as np
import pytesseract
import fitz


def extract_text_from_image(pix):
    bytes = np.frombuffer(pix.samples, dtype=np.uint8)
    img = bytes.reshape(pix.height, pix.width, pix.n)
    img = cv2.resize(img, None, fx=3.5, fy=3.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text = pytesseract.image_to_string(thresh)
    print(text)
    return text


async def extract_images_from_pdf(pdf_path):
    images = []
    pdf_reader = fitz.open(pdf_path)
    for page in pdf_reader:
        pix = page.get_pixmap()
        pix.save("page-%i.png" % page.number)
        images.append(pix)
    return images