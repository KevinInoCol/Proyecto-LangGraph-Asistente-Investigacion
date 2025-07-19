### CÓDIGO MODIFICADO: RAG/rag.py ###

import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client
# Importamos la clase Document para crear un documento a partir de texto
from langchain_core.documents import Document

load_dotenv()

# La función ahora recibe el contenido directamente
def run_rag_pipeline(content: str):
    
    print("************ SUPABASE **************")
    print("---SUBIENDO CONTENIDO EN SUPABASE---")

    # Paso 1: Document Loader (ahora creamos un documento en memoria a partir del texto)
    documents = [Document(page_content=content)]

    # Paso 2: Document Splitting (Dividir en chunks)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Paso 3: Convertir de Chunks a Embeddings
    embedding_model = OpenAIEmbeddings(model='text-embedding-ada-002')

    # Paso 4: Supabase Vector Store
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    client = create_client(supabase_url, supabase_key)

    vectorstore = SupabaseVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        client=client,
        table_name="documents_langgraph_asistente_de_investigacion",
        query_name="match   _documents_langgraph_asistente_de_investigacion",
    )

    print("---CONTENIDO ALMACENADO EN SUPABASE---")