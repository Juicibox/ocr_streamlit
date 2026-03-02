import streamlit as st
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd
import io
import cv2
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

if img_file_buffer is not None:
    try:
        # Abrir y preprocesar imagen
        image = Image.open(img_file_buffer)
        img_array = np.array(image)
        
        # Convertir a escala de grises si es necesario
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # Mostrar imagen
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 Imagen")
            st.image(image, use_container_width=True)
        
        with st.spinner("🔍 Analizando estructura de tabla..."):
            
            # OBTENER DATOS CON POSICIONES
            data = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='spa')
            
            # Filtrar solo texto con confianza alta
            conf_threshold = 40
            items = []
            
            for i in range(len(data['text'])):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > conf_threshold and text:
                    items.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': conf
                    })
            
            if not items:
                st.error("No se detectó texto en la imagen")
                st.stop()
            
            # AGRUPAR POR FILAS (usando coordenada Y)
            # Calcular tolerancia dinámica basada en altura promedio
            avg_height = np.mean([item['height'] for item in items])
            y_tolerance = avg_height * 0.6  # 60% de la altura como tolerancia
            
            # Ordenar por Y y agrupar en filas
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
                    # Guardar fila anterior ordenada por X
                    rows.append(sorted(current_row, key=lambda x: x['x']))
                    current_row = [item]
                    current_y = item['y']
            
            # No olvidar la última fila
            if current_row:
                rows.append(sorted(current_row, key=lambda x: x['x']))
            
            # DETECTAR COLUMNAS
            # Usar la primera fila (headers) para encontrar límites de columnas
            if len(rows) > 0:
                # Calcular número máximo de columnas
                max_cols = max(len(row) for row in rows)
                
                # Crear matriz de datos
                table_data = []
                for row in rows:
                    row_texts = [cell['text'] for cell in row]
                    # Rellenar si faltan celdas
                    while len(row_texts) < max_cols:
                        row_texts.append("")
                    table_data.append(row_texts[:max_cols])  # Truncar si sobran
                
                # Crear DataFrame
                if len(table_data) > 1:
                    # Primera fila como header
                    headers = table_data[0]
                    # Limpiar headers vacíos
                    headers = [f"Col_{i}" if not h else h for i, h in enumerate(headers)]
                    
                    df = pd.DataFrame(table_data[1:], columns=headers)
                else:
                    df = pd.DataFrame(table_data)
                
                # MOSTRAR RESULTADO
                with col2:
                    st.subheader("📋 Tabla detectada")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # OPCIONES DE EDICIÓN Y DESCARGA
                st.markdown("---")
                st.subheader("✏️ Editar y Exportar")
                
                # Editor
                edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                
                col_csv, col_excel = st.columns(2)
                
                with col_csv:
                    csv = edited_df.to_csv(index=False)
                    st.download_button(
                        "📥 Descargar CSV",
                        csv,
                        "tabla.csv",
                        "text/csv"
                    )
                
                with col_excel:
                    buffer = io.BytesIO()
                    edited_df.to_excel(buffer, index=False, engine='openpyxl')
                    st.download_button(
                        "📥 Descargar Excel",
                        buffer.getvalue(),
                        "tabla.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Vista previa del texto plano (para verificar)
                with st.expander("🔍 Ver texto crudo (debug)"):
                    st.text(pytesseract.image_to_string(gray, lang='spa'))
                    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Sube una imagen con tabla para comenzar")
    
    # Ejemplo
    with st.expander("💡 Consejos para mejores resultados"):
        st.markdown("""
        - **Resolución**: Mínimo 150 DPI, ideal 300 DPI
        - **Contraste**: Texto negro sobre fondo blanco funciona mejor
        - **Bordes**: Tablas con líneas visibles se detectan mejor
        - **Idioma**: Selecciona el idioma correcto (spa/español)
        - **Limpieza**: Evita sombras o reflejos en la imagen
        """)

st.markdown("---")
st.caption("OCR con Tesseract + OpenCV")
