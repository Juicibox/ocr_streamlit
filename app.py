import streamlit as st  
import numpy as np
from PIL import Image
import pytesseract
from paddleocr import PaddleOCR

st.title("Extractor de texto de imágenes")

img_file = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file is not None:
    image = Image.open(img_file)
    st.image(image, caption='Imagen cargada', use_column_width=True)  # Mostrar la imagen cargada

    img_array = np.array(image)
    if img_array is not None:  # Verificar si la imagen se cargó correctamente como un array numpy
        text = pytesseract.image_to_string(image)
        st.write("Texto extraído:")
        st.write(text)

        ocr_model = PaddleOCR()
        result = ocr_model.ocr(img_array)
        result = result[0]
        texts = [res[1][0] for res in result]
    

    # Mostrar resultado
        st.write(texts)
    else:
        st.error("Error al cargar la imagen. Por favor, inténtalo de nuevo.")
