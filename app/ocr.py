from cgitb import reset
import os
import itertools
import pytesseract
import fitz
import concurrent.futures
from multiprocessing import Pool

def create_ocr(filename, mat):
  # the matrix for rendering
    doc = fitz.open(filename)  # open the document
    num_pages = doc.page_count  # get number of pages
    print(num_pages, 'number')
    pages_text = []
    for i in range(num_pages):  # work through our page segment
        page = doc[i]
        print(page, 'pages')
        pix = page.get_pixmap(alpha=False, matrix=mat)
        pix.save("p-%i.png" % i)
        img_file = ("p-%i.png" % i)
        preds = pytesseract.image_to_string(img_file)
        predictions = [x for x in preds.split("\n")]
        pages_text.append("".join(predictions))
        os.remove(img_file)
    return pages_text
    # print("Processed page numbers %i through %i" % (seg_from, seg_to - 1))


def create_picture(vector):
    idx = vector[0]  # this is the segment number we have to process
    filename = vector[2]  # document filename
    mat = vector[3]  # the matrix for rendering
    doc = fitz.open(filename)  # open the document
    pages_text = []
    page = doc[idx]
    pix = page.get_pixmap(alpha=False, matrix=mat)
    pix.save("p-%i.png" % idx)
    img_file = ("p-%i.png" % idx)
    preds = pytesseract.image_to_string(img_file)
    predictions = [x for x in preds.split("\n")]
    pages_text.append("".join(predictions))
    os.remove(img_file)
    return predictions


def execute_concurrently(function, kwargs_list):
    with Pool() as p:
        datas = p.map(function, kwargs_list)
    return("".join(list(itertools.chain.from_iterable(datas))))
