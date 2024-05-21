from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import requests
from PIL import Image

from . import models, schemas
from .database import SessionLocal, engine
from .helpers import verify_password, read_settings, hex_to_rgb, blend_images

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/image/")
def blend_color_api(
    file_path: str = Query(...),
    blend_mode: str = Query(...),
    url: str = Query(...),
    password: str = Query(...),
):
    if not verify_password(
        password, "$2b$12$iHUeffTptoi5SNlA4VCDq.rJycbpcgB.849eNk73W8R1l2zIiVNl6"
    ):
        return JSONResponse({"deatil": "Not Authorized"}, 400)
    try:
        hex_color_temp, opacity_temp = read_settings(file_path, hex_color, opacity)
        if hex_color == None:
            hex_color = hex_color_temp
        if opacity == None:
            opacity = opacity_temp
        print(hex_color, opacity)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Unable to fetch image from the URL"
            )
        image = Image.open(BytesIO(response.content))
        if image.mode != "RGB":
            image = image.convert("RGB")
        rgb_color = hex_to_rgb(hex_color)
        new_image = blend_images(image, rgb_color, blend_mode, opacity)
        img_byte_array = BytesIO()
        new_image.save(img_byte_array, format="JPEG", quality=100)
        img_byte_array.seek(0)
        return StreamingResponse(img_byte_array, media_type="image/jpeg")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
