import cv2
import streamlit as st
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr
import os
from googlesearch import search
import webbrowser

# Inicializar el objeto PaddleOCR
ocr = PaddleOCR(lang='es')

def capture_image():
    cap = cv2.VideoCapture(0)
    font_path = os.path.join('font', 'latin.ttf')
    ret, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = ocr.ocr(img)
    result = result[0]
    boxes = [res[0] for res in result]
    scores = [res[1][1] for res in result]
    texts = [res[1][0] for res in result]
    plt.figure(figsize=(15,15))
    annotated = draw_ocr(img, boxes, texts, scores, font_path=font_path)
    plt.imshow(annotated)

    text_concatenated = ' '.join(texts)
    print('Texto concatenado:', text_concatenated)

    # Realizar la búsqueda en Google
    search_results = list(search(text_concatenated, num_results=5))
    print('Resultados de búsqueda:', search_results)

    # Abrir el primer resultado en el navegador web
    if search_results:
        webbrowser.open(search_results[0])

    # Liberar la cámara
    cap.release()
    
def main():
    st.title("Aplicación de OCR y Búsqueda en Google")

    if st.button("Realizar Escaneo"):
        capture_image()

if __name__ == "__main__":
    main()




