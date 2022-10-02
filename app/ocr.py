import pytesseract
import fitz

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

    for i in range(seg_from, seg_to):  # work through our page segment
        page = doc[i]
        # page.get_text("rawdict")  # use any page-related type of work here, eg
        pix = page.get_pixmap(alpha=False, matrix=mat)
        # store away the result somewhere ...
        pix.save("p-%i.png" % i)
        img_file = ("p-%i.png" % i)
        preds = pytesseract.image_to_string(img_file)
        predictions = [x for x in preds.split("\n")]
        return predictions
    # print("Processed page numbers %i through %i" % (seg_from, seg_to - 1))
