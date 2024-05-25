import bcrypt, requests
from PIL import Image, ImageOps
from io import BytesIO
import numpy as np
import time
from PIL import Image
from collections import Counter


def hex_to_rgb(hex_color_code):
    hex_color_code = hex_color_code.lstrip("#")
    return tuple(int(hex_color_code[i : i + 2], 16) for i in (0, 2, 4))


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def calculate_luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def generate_image_helper(image_url, hex_color_code):
    # Fetch the image from the URL
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(image_url, headers=headers)
    if response.status_code != 200:
        raise Exception("Image not found")

    # Open the image
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Convert the image to grayscale
    gray_img = ImageOps.grayscale(img).convert("RGBA")

    # Create an overlay with the given hex color
    overlay_color = hex_to_rgb(hex_color_code) + (255,)
    overlay = Image.new("RGBA", img.size, overlay_color)

    # Blend the grayscale image with the overlay
    blended_img = Image.blend(gray_img, overlay, alpha=0.5)

    # Preserve the original alpha channel
    alpha = img.split()[-1]
    blended_img.putalpha(alpha)

    # Save the result to a BytesIO object
    result_bytes = BytesIO()
    blended_img.save(result_bytes, format="PNG")
    result_bytes.seek(0)

    return result_bytes


def extract_colors_helper(image_url: str, num_colors: int = 5):
    start_time = time.time()
    try:
        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as e:
        print("Error fetching image:", e)
        return None

    end_time = time.time()  # Record the end time
    print("Time taken to fetch image:", end_time - start_time, "seconds")

    image = Image.open(BytesIO(response.content))
    max_dimension = 300  # Change the size as per your requirement

    # Calculate the aspect ratio
    width, height = image.size
    aspect_ratio = width / height

    # Determine the new dimensions while preserving aspect ratio
    if width > height:
        new_width = max_dimension
        new_height = int(max_dimension / aspect_ratio)
    else:
        new_height = max_dimension
        new_width = int(max_dimension * aspect_ratio)

    # Resize the image with the new dimensions
    image = image.resize((new_width, new_height))
    image_array = np.array(image)

    # Flatten the array to (n_pixels, 3) shape where each row represents a pixel
    pixels = image_array.reshape(-1, image_array.shape[-1])

    # Filter out fully transparent pixels if the image has an alpha channel
    if pixels.shape[1] == 4:
        pixels = pixels[pixels[:, 3] > 0]

    # Convert each pixel to a tuple
    pixel_tuples = [tuple(pixel[:3]) for pixel in pixels]

    # Use Counter to count the frequency of each color
    counter = Counter(pixel_tuples)

    # Get the most common colors
    most_common_colors = counter.most_common(num_colors)

    # Extract the colors and convert to hexadecimal
    hex_colors = ["#%02x%02x%02x" % color for color, _ in most_common_colors]

    return " ".join(hex_colors)
