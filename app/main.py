
import pathlib
import os
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
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from . ocr import *
from .helpers import *
from tempfile import NamedTemporaryFile
import shutil
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from mangum import Mangum


ACCESS_ID = 'DO006YU2K49CFPYZZ6FT'
SECRET_KEY = 'u9heysFpujtYAZxxzM+l+sD0MOuhmneHyA1vvv+IZ7E'


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
handler = Mangum(app)

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



@app.post("/")
async def extract_text_from_pdf(file: UploadFile):
    text = ""
    suffix = pathlib.Path(file.filename).suffix
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with NamedTemporaryFile(delete=False, suffix=suffix, dir=dir_path) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = pathlib.Path(tmp.name)

    images = await extract_images_from_pdf(tmp_path)
    with ThreadPoolExecutor() as executor:
        results = [executor.submit(extract_text_from_image, image) for image in images]
        for f in concurrent.futures.as_completed(results):
            text += f.result()
    os.remove(tmp_path)
    text = text.replace("\n", "")

    results_obj = add_data_to_object(text)[0]
    results_array = add_data_to_object(text)[1]
    
    # return {"invoiceDetails": text}
    return {"invoiceDetails": results_obj,"meterDetails": results_array}


