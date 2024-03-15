import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract
from paddleocr import PaddleOCR

st.title("Extractor de texto de imágenes")

img_file = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file_buffer is not None:
    image = Image.open(img_file_buffer)
    img_array = np.array(image)

    # Procesar imagen con PaddleOCR
    ocr_model = PaddleOCR()
    result = ocr_model.ocr(img_array)
    result = result[0]
    texts = [res[1][0] for res in result]
    
    st.write("Texto extraido")
    # Mostrar resultado
    st.write(texts)
