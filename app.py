import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract
import pyperclip
from paddleocr import PaddleOCR

st.set_page_config(page_title="Img to Text", page_icon="logo.png")

# CSS para agregar fondo y estilizar la página
page_bg_img = '''
<style>
body {
    background-image: url("https://www.example.com/fondo.jpg"); /* Cambia esta URL por la de tu imagen */
    background-size: cover;
}
header {
    background-color: rgba(255, 255, 255, 0.8);
    padding: 10px;
    border-radius: 10px;
    text-align: center;
}
.stTextArea, .stFileUploader {
    background-color: rgba(255, 255, 255, 0.8);
    padding: 10px;
    border-radius: 10px;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

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

    
        
        
            
