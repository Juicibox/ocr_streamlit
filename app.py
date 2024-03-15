import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract
import pyperclip
from paddleocr import PaddleOCR

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
    text = "\n".join(texts)
    text_area = st.text_area("Texto extraído", text, height=200)

    # Botón para copiar el texto al portapapeles
    if st.button("Copiar texto"):
        try:
            pyperclip.copy(text_area)
            st.success("Texto copiado al portapapeles")
        except pyperclip.PyperclipException:
            st.write("Please copy the following link:")
        
        
            
