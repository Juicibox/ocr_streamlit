import streamlit as st
import numpy as np
from PIL import Image
import pytesseract


st.set_page_config(page_title="Img to Text", page_icon="logo.png")


st.logo("logo.png", size="medium")


img_file_buffer = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file_buffer is not None:
    image = Image.open(img_file_buffer)

    # Procesar imagen con pytesseract
    text = pytesseract.image_to_string(image)

    # Mostrar resultado
    st.text_area("Texto extraído", text, height=200)

