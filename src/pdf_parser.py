import fitz  # PyMuPDF
import io
from PIL import Image

def pdf_to_images(pdf_path, dpi=120, optimize=False):
    """
    Convert PDF pages to a list of PIL Images.
    If optimize=True, only converts select pages. 
    By default (optimize=False), it converts every single page of the PDF.
    Using 120 DPI maintains sharp drawing text while conserving token space.
    """
    doc = fitz.open(pdf_path)
    images = []
    
    if optimize:
        pages_to_load = [0]
        if len(doc) > 1:
            pages_to_load.append(1)
        if len(doc) > 2:
            last_idx = len(doc) - 1
            if last_idx not in pages_to_load:
                pages_to_load.append(last_idx)
    else:
        pages_to_load = range(len(doc))
    
    for page_num in pages_to_load:
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))
        images.append(image)
        
    doc.close()
    return images
