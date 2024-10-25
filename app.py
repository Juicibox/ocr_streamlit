import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract
import pyperclip
from paddleocr import PaddleOCR

st.set_page_config(page_title="Img to Text", page_icon="logo.png")


st.title("Extractor de texto de imágenes")

img_file = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file is not None:
    image = Image.open(img_file)
    img_array = np.array(image)
    st.image(image, caption='Imagen cargada', use_column_width=True)
    
    # Procesar imagen con PaddleOCR
    ocr_model = PaddleOCR()
    result = ocr_model.ocr(img_array)
    result = result[0]
    texts = [res[1][0] for res in result]
    
    # Mostrar resultado
    text = " ".join(texts)
    text_area = st.text_area("Texto extraído", text, height=200)

    
        
        
            
