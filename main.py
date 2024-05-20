from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
import requests
from PIL import Image, ImageOps, ImageEnhance
import bcrypt

app = FastAPI()

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def blend_images(image: Image.Image, color: tuple, blend_mode: str, opacity: float) -> Image.Image:
    if blend_mode == 'overlay':
        blended = Image.blend(image, ImageOps.colorize(ImageOps.grayscale(image), (0, 0, 0), color), opacity)
    elif blend_mode == 'color':
        blended = ImageOps.colorize(image, (0, 0, 0), color)
    elif blend_mode == 'soft_light':
        blended = ImageEnhance.Brightness(image).enhance(2.0)
        blended = Image.blend(blended, ImageOps.colorize(ImageOps.grayscale(image), (0, 0, 0), color), opacity)
    else:
        raise ValueError(f"Unsupported blend mode: {blend_mode}")

    return blended

def read_settings(file_path, hex_color, opacity):
    try:
        response = requests.get(file_path)
        if response.status_code == 200:
            lines = response.text.split('\n')  
            lines = response.text.split('\n')   
            color = lines[0].strip()
            opacity = float(lines[1].strip())
            data = {}
            for line in lines[2:]:
                key, value = line.strip().split('=', 1)
                data[key] = value       
            return data[color], opacity
        else:
            return hex_color, opacity
    except FileNotFoundError:
        return hex_color, opacity

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.get("/blend-color/")
def blend_color_api(file_path: str = Query(...), blend_mode: str = Query(...), url: str = Query(...), password: str = Query(...), hex_color: str = None, opacity: str = None):
    if not verify_password(password, '$2b$12$iHUeffTptoi5SNlA4VCDq.rJycbpcgB.849eNk73W8R1l2zIiVNl6'):
        return JSONResponse({"deatil":"Not Authorized"}, 400)
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
            raise HTTPException(status_code=400, detail="Unable to fetch image from the URL")
        image = Image.open(BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
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