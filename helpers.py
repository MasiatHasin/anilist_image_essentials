import bcrypt, requests
from PIL import Image
from fastapi import HTTPException
from io import BytesIO
from sklearn.cluster import KMeans
import numpy as np
import time
import cv2
from PIL import Image
from collections import Counter
from sqlalchemy.orm import Session


def hex_to_bgr(hex_code: str):
    # Remove the '#' character
    hex_code = hex_code.lstrip("#")
    # Convert hex color code to BGR format
    bgr = tuple(int(hex_code[i : i + 2], 16) for i in (4, 2, 0))
    return bgr


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def calculate_luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def generate_image_helper(image_url, hex_color_code):

    # Add headers for fetching the image from Imgur
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(image_url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Image not found")

    # Convert the image to a NumPy array in memory
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)

    # Read the image from the array
    img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise HTTPException(status_code=400, detail="Error reading image")

    hh, ww = img.shape[:2]

    # Convert hex color code to BGR format
    color_bgr = hex_to_bgr(hex_color_code)

    # Define color image
    color_img = np.full((hh, ww, 3), color_bgr, dtype=np.uint8)

    # Check if the image is colored
    if len(img.shape) == 2:
        # The image is grayscale, convert to BGRA
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif len(img.shape) == 3:
        if img.shape[2] == 3:
            # The image is colored without transparency, convert to grayscale with alpha channel
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == 4:
            # The image is colored with transparency, convert the color channels to grayscale
            bgr_img = img[:, :, :3]
            gray_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
            img[:, :, :3] = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    # Overlay blending mode
    result = cv2.addWeighted(img[:, :, :3], 0.5, color_img, 0.5, 0)

    # If the original image had an alpha channel, add it back
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = alpha

    # Encode the result to PNG format in memory
    _, buffer = cv2.imencode(".png", result)
    result_bytes = BytesIO(buffer)

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
    pixels = image_array.reshape(-1, 3)

    # Define the number of dominant colors you want to extract
    # Use KMeans clustering to find the dominant colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)

    # Get the cluster centers (which represent the dominant colors)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # Convert RGB values to hexadecimal color codes
    hex_colors = ["#%02x%02x%02x" % tuple(color) for color in dominant_colors]

    return " ".join(hex_colors)
