# streamlit_app.py

import streamlit as st
import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from graph import run_graph_pipeline
# La importación de run_rag_pipeline ya no es necesaria aquí

UPLOAD_DIR = "RAG/Base_de_Conocimientos"

st.title("Asistente Académico de Investigación Científica")
st.write("Sube un documento PDF para analizar, extraer, almacenar y notificar sobre la información más relevante.")

uploaded_file = st.file_uploader("Sube tu PDF", type=["pdf"])

if uploaded_file:
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    full_text = "\n".join([doc.page_content for doc in documents])

    st.info("Ejecutando grafo de agentes para procesar el documento...")
    
    # El grafo ahora se encarga de todo el flujo (extraer, guardar en RAG, enviar email)
    # y nos devuelve el estado final.
    final_state = run_graph_pipeline(full_text)
    
    # Verificamos si se extrajo contenido (lo que significa que el flujo 'Sí' se completó)
    if final_state.get("extracted_content"):
        st.success("¡Proceso completado! El documento es relevante, ha sido almacenado y se ha enviado una notificación por correo.")
        with st.expander("Ver contenido procesado"):
            st.write(final_state["extracted_content"])
    else:
        st.warning("El documento no trata sobre Motion Retargeting. El proceso se detuvo como se esperaba.")