
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
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image
from . ocr import create_picture
from tempfile import NamedTemporaryFile
import shutil
import concurrent.futures
import fitz
from multiprocessing import Pool, cpu_count




class Settings(BaseSettings):
    app_auth_token: str = 'asdasd'
    debug: bool = True
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = True
    
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
        raise HTTPException(detail="Please provide a header", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid TOken", status_code=401)


@app.post("/") # http POST
async def prediction_view(file:UploadFile = File(...), authorization = Header(None), settings:Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    # print(file.filename, ' file......file')
    try:
        suffix = pathlib.Path(file.filename).suffix
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with NamedTemporaryFile(delete=False, suffix=suffix, dir=dir_path) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = pathlib.Path(tmp.name)
            print(tmp_path, 'tmp pathjjjjj')
            doc = fitz.open(tmp_path)
            print(doc, 'dooooooc')
    except:
        os.remove(tmp_path)
        raise HTTPException(detail="Invalid file format", status_code=400)
    try:
        filename = tmp_path
        print(filename, 'file naaaaame')
        # mat = fitz.Matrix(1, 1)  # the rendering matrix: scale down to 20%
        mat = fitz.Matrix(100 / 72, 100 / 72)
        cpu = cpu_count()

        vectors = [(i, cpu, filename, mat) for i in range(cpu)]
        pages_text = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(create_picture, vectors)
            for result in results:
                if result:
                    pages_text.append("".join(result).split('\n'))
            print(pages_text)
    except:
        os.remove(tmp_path)
        raise HTTPException(detail="Error in proccessing the images", status_code=400)

    os.remove(tmp_path)
    return {"results": pages_text, 'tst':'tst'}


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
