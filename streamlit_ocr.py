import streamlit as st
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd
import io
import cv2
import re
from pytesseract import Output

# Configuración de página
st.set_page_config(page_title="OCR Tablas", page_icon="📊")

st.title("📊 OCR para Tablas")
st.markdown("Extrae datos tabulares manteniendo la estructura de filas y columnas")

# Cargar imagen
img_file_buffer = st.file_uploader(
    "Cargar imagen de tabla", 
    type=['jpg', 'jpeg', 'png', 'webp', 'bmp']
)

def clean_text(text):
    """Limpia caracteres de borde de tabla y espacios extras"""
    # Eliminar caracteres de borde comunes en tablas
    text = re.sub(r'[\|\─\━\═\─\–\—]', '', text)  # Quitar | y líneas
    text = text.strip()
    # Normalizar espacios múltiples
    text = ' '.join(text.split())
    return text

if img_file_buffer is not None:
    try:
        # Abrir imagen
        image = Image.open(img_file_buffer)
        img_array = np.array(image)
        
        # Preprocesamiento mejorado
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Mejorar contraste
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Mostrar imagen
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 Imagen")
            st.image(image, use_container_width=True)
        
        with st.spinner("🔍 Analizando estructura de tabla..."):
            
            # Configuración optimizada para tablas
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            
            data = pytesseract.image_to_data(
                gray, 
                output_type=Output.DICT, 
                lang='spa',
                config=custom_config
            )
            
            # Filtrar texto válido
            conf_threshold = 35
            items = []
            
            for i in range(len(data['text'])):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                # Limpiar y validar
                text_clean = clean_text(text)
                
                if conf > conf_threshold and text_clean and len(text_clean) > 1:
                    items.append({
                        'text': text_clean,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'height': data['height'][i]
                    })
            
            if not items:
                st.error("No se detectó texto válido")
                st.stop()
            
            # AGRUPAR POR FILAS
            avg_height = np.mean([item['height'] for item in items])
            y_tolerance = avg_height * 0.7
            
            items_sorted = sorted(items, key=lambda x: x['y'])
            rows = []
            current_row = []
            current_y = None
            
            for item in items_sorted:
                if current_y is None:
                    current_y = item['y']
                    current_row.append(item)
                elif abs(item['y'] - current_y) <= y_tolerance:
                    current_row.append(item)
                else:
                    rows.append(sorted(current_row, key=lambda x: x['x']))
                    current_row = [item]
                    current_y = item['y']
            
            if current_row:
                rows.append(sorted(current_row, key=lambda x: x['x']))
            
            # CONSTRUIR TABLA
            if len(rows) > 0:
                # Determinar número de columnas (usar moda o máximo razonable)
                col_counts = [len(row) for row in rows]
                # Filtrar filas con muy pocas celdas (probablemente ruido)
                valid_rows = [row for row in rows if len(row) >= 2]
                
                if not valid_rows:
                    valid_rows = rows
                
                max_cols = max(len(row) for row in valid_rows)
                
                # Crear matriz uniforme
                table_data = []
                for row in valid_rows:
                    row_texts = [cell['text'] for cell in row]
                    # Rellenar o truncar para igualar columnas
                    while len(row_texts) < max_cols:
                        row_texts.append("")
                    table_data.append(row_texts[:max_cols])
                
                # Crear DataFrame con nombres únicos
                if len(table_data) > 0:
                    # Generar headers únicos
                    if len(table_data) > 1:
                        raw_headers = table_data[0]
                        # Asegurar headers únicos
                        headers = []
                        seen = {}
                        for i, h in enumerate(raw_headers):
                            if not h:  # Si está vacío
                                h = f"Col_{i+1}"
                            if h in seen:
                                seen[h] += 1
                                h = f"{h}_{seen[h]}"
                            else:
                                seen[h] = 0
                            headers.append(h)
                        
                        df = pd.DataFrame(table_data[1:], columns=headers)
                    else:
                        df = pd.DataFrame(table_data)
                
                # MOSTRAR RESULTADO
                with col2:
                    st.subheader(f"📋 Tabla detectada ({len(df)} filas, {len(df.columns)} cols)")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # EDICIÓN Y EXPORTACIÓN
                st.markdown("---")
                st.subheader("✏️ Editar y Exportar")
                
                edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                
                col_csv, col_excel = st.columns(2)
                
                with col_csv:
                    csv = edited_df.to_csv(index=False)
                    st.download_button("📥 Descargar CSV", csv, "tabla.csv", "text/csv")
                
                with col_excel:
                    buffer = io.BytesIO()
                    edited_df.to_excel(buffer, index=False, engine='openpyxl')
                    st.download_button("📥 Descargar Excel", buffer.getvalue(), "tabla.xlsx",
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                # Debug
                with st.expander("🔍 Debug - Ver filas detectadas"):
                    for i, row in enumerate(table_data[:10]):  # Mostrar primeras 10
                        st.write(f"Fila {i}: {row}")
                    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Sube una imagen con tabla para comenzar")
    
    with st.expander("💡 Consejos"):
        st.markdown("""
        - Resolución mínima: 150 DPI
        - Evita fotos con ángulo (lo más plano posible)
        - Buena iluminación sin sombras
        - Selecciona el idioma correcto
        """)

st.markdown("---")
st.caption("OCR con Tesseract + OpenCV")
                            
