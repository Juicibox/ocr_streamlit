import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract

st.title("Extractor de texto de imágenes")

img_file = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file is not None:
    image = Image.open(img_file)
    img_array = np.array(image)
    text = pytesseract.image_to_string(image)
    st.write(text)

