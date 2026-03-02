import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract

st.set_page_config(page_title="Img to Text", page_icon="logo.png")



st.title("Extractor de texto de imágenes")

img_file = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file is not None:
    image = Image.open(img_file)
    st.image(image, caption='Imagen cargada', use_column_width=True)
    
    # Procesar imagen con pytesseract
    text = pytesseract.image_to_string(image)
    
    # Mostrar resultado
    st.text_area("Texto extraído", text, height=200)

