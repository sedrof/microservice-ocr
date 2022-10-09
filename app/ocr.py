import pytesseract
import fitz
import concurrent.futures

def create_picture(vector):
    idx = vector[0]  # this is the segment number we have to process
    cpu = vector[1]  # number of CPUs
    filename = vector[2]  # document filename
    mat = vector[3]  # the matrix for rendering
    doc = fitz.open(filename)  # open the document
    num_pages = doc.page_count  # get number of pages

    # pages per segment: make sure that cpu * seg_size >= num_pages!
    seg_size = int(num_pages / cpu + 1)
    seg_from = idx * seg_size  # our first page number
    seg_to = min(seg_from + seg_size, num_pages)  # last page number
    pages_text = []
    for i in range(seg_to):  # work through our page segment
        page = doc[i]
        # page.get_text("rawdict")  # use any page-related type of work here, eg
        pix = page.get_pixmap(alpha=False, matrix=mat)
        # store away the result somewhere ...
        pix.save("p-%i.png" % i)
        img_file = ("p-%i.png" % i)
        preds = pytesseract.image_to_string(img_file)
        predictions = [x for x in preds.split("\n")]
        pages_text.append("".join(predictions))
        return predictions
    # print("Processed page numbers %i through %i" % (seg_from, seg_to - 1))


def create_ocr(filename, mat):
  # the matrix for rendering
    doc = fitz.open(filename)  # open the document
    num_pages = doc.page_count  # get number of pages
    print(num_pages, 'number')
    pages_text = []
    for i in range(num_pages):  # work through our page segment
        page = doc[i]
        print(page, 'pages')
        # page.get_text("rawdict")  # use any page-related type of work here, eg
        pix = page.get_pixmap(alpha=False, matrix=mat)
        # store away the result somewhere ...
        pix.save("p-%i.png" % i)
        img_file = ("p-%i.png" % i)
        preds = pytesseract.image_to_string(img_file)
        predictions = [x for x in preds.split("\n")]
        pages_text.append("".join(predictions))
    return pages_text
    # print("Processed page numbers %i through %i" % (seg_from, seg_to - 1))


pages_text = []
def execute_concurrently(function, kwargs_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(function, kwargs) for kwargs in kwargs_list]
    for future in concurrent.futures.as_completed(futures):
        # if future.result():
        pages_text.append("".join(future.result()))
            # results.append(future.result())
        # break
    return pages_text