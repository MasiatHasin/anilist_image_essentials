
import bcrypt, requests
from PIL import Image, ImageOps, ImageEnhance

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