import streamlit as st
from paddleocr import PaddleOCR

logo_path = "logo.png"
st.logo(logo_path, size="medium")

st.set_page_config(
    page_title="Img to Text",
    page_icon=logo_path
)

img_file_buffer = st.file_uploader("Cargar imagen", type=['jpg', 'jpeg', 'png', 'webp', 'bmp'])
if img_file_buffer is not None:
    image = Image.open(img_file_buffer)
    img_array = np.array(image)

    # Procesar imagen con PaddleOCR
    ocr_model = PaddleOCR()
    result = ocr_model.ocr(img_array)
    result = result[0]
    texts = [res[1][0] for res in result]
    

    # Mostrar resultado
    st.write(texts)
