import cv2
from PIL import Image
import tkinter as tk
from paddleocr import PaddleOCR, draw_ocr
import os
from matplotlib import pyplot as plt
import streamlit as st
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
    st.image(img, channels="RGB", use_column_width=True)
    st.write("Textos:", texts)

    # Obtener los textos como una cadena concatenada
    text_concatenated = ' '.join(texts)
    st.write('Texto concatenado:', text_concatenated)

    # Realizar la búsqueda en Google
    search_results = list(search(text_concatenated, num_results=5))
    st.write('Resultados de búsqueda:', search_results)

    # Abrir el primer resultado en el navegador web
    if search_results:
        webbrowser.open(search_results[0])

    # Liberar la cámara
    cap.release()

def main():
    st.title("Aplicación de OCR y Búsqueda en Google")
    st.write("Presiona el botón para capturar una imagen y realizar la búsqueda en Google:")
    if st.button("Capturar Imagen"):
        capture_image()


