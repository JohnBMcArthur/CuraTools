import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import io


# Function to convert image to grayscale and optionally highlight the range
def process_image(image, lower, upper, highlight=False):
    grayscale_image = ImageOps.grayscale(image)
    grayscale_array = np.array(grayscale_image)

    if highlight:
        highlighted_image = grayscale_image.convert('RGB')
        highlighted_array = np.array(highlighted_image)
        mask = (grayscale_array >= lower) & (grayscale_array <= upper)
        highlighted_array[mask] = [255, 255, 0]  # Highlight in yellow
        return Image.fromarray(highlighted_array)

    return grayscale_image

# Function to count pixels within a grayscale range
def count_pixels_in_range(image, lower, upper):
    grayscale_image = ImageOps.grayscale(image)
    grayscale_array = np.array(grayscale_image)
    in_range = np.sum((grayscale_array >= lower) & (grayscale_array <= upper))
    total_pixels = grayscale_array.size
    return in_range, total_pixels
