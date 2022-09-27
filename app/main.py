import pathlib
import os
import io
import uuid
from functools import lru_cache
from fastapi import(
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile
    )
import pytesseract
import fitz
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image
from . ocr import ocr_page
from tempfile import NamedTemporaryFile
import shutil

pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"
class Settings(BaseSettings):
    app_auth_token: str = 'asdasd'
    debug: bool = False
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
DEBUG=settings.debug

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"


app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse) # http GET -> JSON
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", {"request": request, "abc": 123})


def verify_auth(authorization = Header(None), settings:Settings = Depends(get_settings)):
    """
    Authorization: Bearer <token>
    {"authorization": "Bearer <token>"}
    """
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Invalid endpoint", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid endpoint", status_code=401)


@app.post("/") # http POST
async def prediction_view(file:UploadFile = File(...), authorization = Header(None), settings:Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    print(file.filename, ' file......file')
    try:
        suffix = pathlib.Path(file.filename).suffix
        print(suffix, 'suffixxxx')
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = pathlib.Path(tmp.name)
            print(tmp_path, 'tmp pathjjjjj')
            doc = fitz.open(tmp_path)
            mat = fitz.Matrix(400 / 72, 400 / 72)
            img_filenames = []
            i = 0
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img_filenames.append("page-%04i.png" % page.number) 
                pix.pil_save(img_filenames[i], format="png", dpi=(300,300))
                i+=1
            print(img_filenames[1], 'pixxxx')
            file.file.close()
            tmp.close()
            
    except:
        file.file.close()
        tmp.close()
        raise HTTPException(detail="Invalid file format", status_code=400)
    try:
        img = [Image.open(x) for y, x in enumerate(img_filenames)]
    except:
        raise HTTPException(detail="Invalid file", status_code=400)

    # preds = [pytesseract.image_to_string(x) for y, x in enumerate(img)]
    # predictions = [x for x in preds[0].split("\n")]
    predictions = ocr_page(img[0])
    file.file.close()
    tmp.close()
    print(tmp_path, 'in the last....')
    shutil.rmtree(tmp_path)
    return {"results": predictions, 'tst':'tst'}
    # except:
    #     raise HTTPException(detail="Invalid file before last", status_code=400)
    

    # bytes_str = io.BytesIO(await file.read())
    # files = await file.read()
    # print(type(files), ' typeeee')
    # doc = fitz.open(files)
    # page = doc.loadPage(0)
    # pix = page.get_pixmap()
    # output = "outfile.png"
    # pix.save(output)
    # bytes_str = io.BytesIO(pix.read())
    


@app.post("/img-echo/", response_class=FileResponse) # http POST
async def img_echo_view(file:UploadFile = File(...), settings:Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix # .jpg, .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return dest
