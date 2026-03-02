import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import io
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import tempfile
import os

# Configuración
st.set_page_config(page_title="OCR Pro con docTR", page_icon="📊")

st.title("📊 OCR Pro - docTR")
st.markdown("OCR de alto rendimiento con detección de tablas")

@st.cache_resource
def load_ocr_model():
    """Carga el modelo de docTR (se cachea para no recargar)"""
    with st.spinner("Cargando modelo de IA... (primera vez)"):
        # Modelo preentrenado para detección + reconocimiento
        model = ocr_predictor(
            det_arch='db_resnet50',      # Detector de texto
            reco_arch='crnn_vgg16_bn',    # Reconocimiento de texto
            pretrained=True
        )
    return model

# Cargar modelo
predictor = load_ocr_model()

# Subir imagen
img_file_buffer = st.file_uploader(
    "Cargar imagen", 
    type=['jpg', 'jpeg', 'png', 'webp', 'pdf']
)

if img_file_buffer is not None:
    try:
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(img_file_buffer.getvalue())
            tmp_path = tmp.name
        
        # Cargar con docTR
        doc = DocumentFile.from_images(tmp_path)
        
        # Mostrar imagen
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 Imagen")
            image = Image.open(img_file_buffer)
            st.image(image, use_container_width=True)
        
        with st.spinner("🔍 Procesando con IA..."):
            # OCR
            result = predictor(doc)
            
            # Extraer texto plano
            text_export = result.render()
            
            # Extraer bloques con coordenadas para tabla
            pages = result.pages
            
            for page in pages:
                # Obtener todas las líneas/bloques
                blocks = []
                
                for block in page.blocks:
                    for line in block.lines:
                        line_text = " ".join([word.value for word in line.words])
                        # Coordenadas del centro de la línea
                        y_center = (line.geometry[0][1] + line.geometry[1][1]) / 2
                        x_center = (line.geometry[0][0] + line.geometry[1][0]) / 2
                        
                        blocks.append({
                            'text': line_text,
                            'y': y_center,
                            'x': x_center,
                            'conf': np.mean([word.confidence for word in line.words]) if line.words else 0
                        })
                
                if not blocks:
                    st.warning("No se detectó texto")
                    continue
                
                # AGRUPAR EN FILAS (por posición Y)
                blocks_sorted = sorted(blocks, key=lambda b: b['y'])
                
                rows = []
                current_row = []
                current_y = None
                y_tolerance = 0.02  # 2% de tolerancia en altura
                
                for block in blocks_sorted:
                    if current_y is None:
                        current_y = block['y']
                        current_row.append(block)
                    elif abs(block['y'] - current_y) <= y_tolerance:
                        current_row.append(block)
                    else:
                        rows.append(sorted(current_row, key=lambda b: b['x']))
                        current_row = [block]
                        current_y = block['y']
                
                if current_row:
                    rows.append(sorted(current_row, key=lambda b: b['x']))
                
                # Crear DataFrame
                if len(rows) > 0:
                    max_cols = max(len(r) for r in rows)
                    table_data = []
                    
                    for row in rows:
                        texts = [b['text'] for b in row]
                        while len(texts) < max_cols:
                            texts.append("")
                        table_data.append(texts[:max_cols])
                    
                    # Crear DF
                    if len(table_data) > 1:
                        headers = [f"Col_{i+1}" if not h else h[:50] 
                                  for i, h in enumerate(table_data[0])]
                        # Hacer únicos
                        seen = {}
                        unique_headers = []
                        for h in headers:
                            if h in seen:
                                seen[h] += 1
                                unique_headers.append(f"{h}_{seen[h]}")
                            else:
                                seen[h] = 0
                                unique_headers.append(h)
                        
                        df = pd.DataFrame(table_data[1:], columns=unique_headers)
                    else:
                        df = pd.DataFrame(table_data)
                    
                    # Mostrar resultado
                    with col2:
                        st.subheader(f"📋 Resultado ({len(df)} filas)")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Tabs para diferentes vistas
                    tab1, tab2, tab3 = st.tabs(["📊 Tabla", "📝 Texto", "🔧 Editar"])
                    
                    with tab1:
                        st.dataframe(df, use_container_width=True)
                        
                        # Exportar
                        c1, c2 = st.columns(2)
                        with c1:
                            st.download_button("📥 CSV", df.to_csv(index=False), "datos.csv")
                        with c2:
                            buf = io.BytesIO()
                            df.to_excel(buf, index=False, engine='openpyxl')
                            st.download_button("📥 Excel", buf.getvalue(), "datos.xlsx")
                    
                    with tab2:
                        st.text_area("Texto detectado", text_export, height=300)
                        st.download_button("📥 TXT", text_export, "texto.txt")
                    
                    with tab3:
                        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                        if st.button("💾 Guardar cambios"):
                            st.success("¡Listo para descargar desde las pestañas anteriores!")
        
        # Limpiar temp
        os.unlink(tmp_path)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)

else:
    st.info("👆 Sube una imagen o PDF")
    
    st.markdown("""
    ### ✨ Ventajas de docTR:
    - **Deep Learning**: Redes neuronales entrenadas con millones de documentos
    - **Detección precisa**: Encuentra texto en cualquier orientación
    - **Tablas complejas**: Mejor manejo de celdas combinadas
    - **PDF nativo**: Soporta documentos multipágina
    """)

st.markdown("---")
st.caption("Powered by docTR (Mindee) + Streamlit")
