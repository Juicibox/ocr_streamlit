import streamlit as st
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd
import io

# Configuración de página
st.set_page_config(page_title="Img to Text & Tables", page_icon="📝")

# Título y logo
st.title("📝 OCR - Texto y Tablas")
st.markdown("Extrae texto plano o datos tabulares de tus imágenes")

# Cargar imagen
img_file_buffer = st.file_uploader(
    "Cargar imagen", 
    type=['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'pdf']
)

if img_file_buffer is not None:
    try:
        # Abrir imagen
        image = Image.open(img_file_buffer)
        
        # Mostrar imagen cargada
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 Imagen original")
            st.image(image, use_container_width=True)
        
        # Opciones de extracción
        st.subheader("⚙️ Opciones de extracción")
        modo = st.radio(
            "Selecciona el modo:",
            ["Texto plano", "Tabla (datos estructurados)", "Ambos"]
        )
        
        with st.spinner("Procesando con OCR..."):
            
            # MODO 1: TEXTO PLANO
            if modo in ["Texto plano", "Ambos"]:
                text = pytesseract.image_to_string(image)
                
                with col2:
                    st.subheader("📄 Texto extraído")
                    st.text_area("Resultado", text, height=300)
                    
                    # Botón copiar (workaround con código)
                    st.code(text, language="text")
                    
                    # Descargar como TXT
                    st.download_button(
                        label="📥 Descargar TXT",
                        data=text,
                        file_name="texto_extraido.txt",
                        mime="text/plain"
                    )
            
            # MODO 2: TABLA
            if modo in ["Tabla (datos estructurados)", "Ambos"]:
                st.markdown("---")
                st.subheader("📊 Extracción de Tabla")
                
                # Intentar extraer como tabla
                # Pytesseract puede intentar detectar tablas con config especial
                custom_config = r'--oem 3 --psm 6'
                
                # Obtener datos con bounding boxes
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Procesar para detectar filas/columnas por posición
                n_boxes = len(data['text'])
                rows = {}
                
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 30:  # Filtrar por confianza
                        text_item = data['text'][i].strip()
                        if text_item:
                            # Agrupar por posición Y (aproximado para filas)
                            y_pos = data['top'][i]
                            row_key = round(y_pos / 20) * 20  # Tolerancia de 20px
                            
                            if row_key not in rows:
                                rows[row_key] = []
                            rows[row_key].append({
                                'text': text_item,
                                'x': data['left'][i]
                            })
                
                # Ordenar filas y columnas
                if rows:
                    table_data = []
                    for y in sorted(rows.keys()):
                        row = sorted(rows[y], key=lambda x: x['x'])
                        table_data.append([cell['text'] for cell in row])
                    
                    # Crear DataFrame (intentar detectar header)
                    if len(table_data) > 1:
                        # Primera fila como header opcional
                        use_header = st.checkbox("Usar primera fila como encabezados", value=True)
                        
                        if use_header:
                            df = pd.DataFrame(table_data[1:], columns=table_data[0])
                        else:
                            df = pd.DataFrame(table_data)
                    else:
                        df = pd.DataFrame(table_data)
                    
                    # Mostrar tabla
                    st.dataframe(df, use_container_width=True)
                    
                    # Opciones de descarga
                    col_csv, col_excel = st.columns(2)
                    
                    with col_csv:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar CSV",
                            data=csv,
                            file_name="tabla_extraida.csv",
                            mime="text/csv"
                        )
                    
                    with col_excel:
                        excel_buffer = io.BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            label="📥 Descargar Excel",
                            data=excel_data,
                            file_name="tabla_extraida.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # Editar tabla manualmente si es necesario
                    st.markdown("**✏️ ¿Necesitas corregir algo?**")
                    edited_df = st.data_editor(df, num_rows="dynamic")
                    
                else:
                    st.warning("No se detectaron datos tabulares claros. Intenta con el modo 'Texto plano'.")
                    
    except Exception as e:
        st.error(f"❌ Error al procesar la imagen: {str(e)}")
        st.info("💡 Consejo: Asegúrate de que la imagen sea clara y el texto sea legible.")

else:
    # Estado vacío
    st.info("👆 Sube una imagen para comenzar")
    
    # Ejemplo de uso
    with st.expander("💡 Consejos para mejores resultados"):
        st.markdown("""
        - Usa imágenes con buena iluminación
        - Evita ángulos extremos
        - Para tablas, asegúrate de que las líneas sean visibles
        - El formato PNG o JPG de alta calidad funciona mejor
        """)

# Footer
st.markdown("---")
st.caption("Powered by Tesseract OCR + Streamlit")
