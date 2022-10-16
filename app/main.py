
import pathlib
import logging
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
from . ocr import create_ocr, create_picture, execute_concurrently, create_ocr
from .helpers import *
from tempfile import NamedTemporaryFile
import shutil
import fitz

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
    except:
        os.remove(tmp_path)
        raise HTTPException(detail="Invalid file format", status_code=400)
    try:
        filename = tmp_path
        # mat = fitz.Matrix(1, 1)  # the rendering matrix: scale down to 20%
        mat = fitz.Matrix(100 / 30, 100 / 30)
        cpu = int(2)
    except:
        os.remove(tmp_path)
        raise HTTPException(detail="Error in proccessing the images", status_code=400)
    try:
        vectors = [(i, cpu, filename, mat) for i in range(2)]
        # print(vectors)
        # results = create_ocr(filename, mat)
        results = execute_concurrently(create_picture, vectors)
    except:
        os.remove(tmp_path)
        raise HTTPException(detail=logging.error("Exception occurred", exc_info=True), status_code=400)

    try:
        total_amount = total_amount_func(results)
        meter_no = meter_no_func(results)
        inv_ref = inv_ref_func(results)
        due_date = due_date_func(results)
        invoice_date = invoice_date_func(results)
        total_water_usage = total_water_usage_func(results)
        description = description_func(results)
        this_reading = this_reading_func(results)
        last_reading = last_reading_func(results)
        consumption = consumption_func(results)
        print(total_amount, 'totaaaaaal')
        print(meter_no, 'meter_no')
        print(inv_ref, 'inv_ref')
        print(due_date, 'due_date')
        print(invoice_date, 'invoice_date')
        print(total_water_usage, 'total_water_usage')
        print(description, 'description')
        print(this_reading, 'this_reading')
        print(last_reading, 'last_reading')
        print(consumption, 'consumption_func')
    except:
        os.remove(tmp_path)
        raise HTTPException(detail=logging.error("Exception occurred while fetching data", exc_info=True), status_code=400)

    os.remove(tmp_path)
    return {"results": results, 'tst':'tst'}





