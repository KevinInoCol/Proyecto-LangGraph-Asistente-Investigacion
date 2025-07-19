### CÓDIGO MODIFICADO: graph.py ###

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from RAG.rag import run_rag_pipeline
from utils.enviar_correo import send_notification_email_smtp

# --- Carga de Modelos y Claves ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Usaremos el mismo modelo para ambos agentes
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", # Usamos 1.5 Flash que es excelente para tareas de extracción
    temperature=0.0 # Ponemos temperatura 0 para que sea determinístico y siga instrucciones
)

# --- Agente 1: Filtro (El que ya tenías) ---
filter_agent_runnable = create_react_agent(
    model=model,
    tools=[],
    prompt="""
    Eres un experto en investigación científica. Tu tarea es analizar el contenido de un documento.
    Responde únicamente 'Sí' si el texto trata sobre motion retargeting, transferencia de movimiento de humano hacia robot, o técnicas de animación para robots.
    En cualquier otro caso responde solo 'No'. No des explicaciones, solo responde Sí o No.
    """
)

# --- Agente 2: Extractor de Información Clave (Nuevo Agente) ---
extraction_agent_runnable = create_react_agent(
    model=model,
    tools=[],
    prompt="""
    Eres un experto en procesar documentos académicos para una base de datos de conocimiento (RAG).
    Tu tarea es extraer la información más relevante de un paper científico.
    
    1.  Extrae el TÍTULO, los AUTORES y el ABSTRACT.
    2.  Luego, extrae el contenido esencial de las secciones de INTRODUCCIÓN, METODOLOGÍA y CONCLUSIÓN.
    3.  Combina toda esta información en un único bloque de texto, bien estructurado y limpio.
    
    El resultado final debe ser solo el texto extraído, sin frases como "Aquí está el resumen:" o cualquier otra conversación.
    Este texto se usará directamente para crear embeddings, así que la calidad y relevancia son cruciales.
    """
)


# --- Definición del Estado del Grafo ---
# El estado es el "cerebro" de nuestro grafo. Guarda la información mientras pasa de un nodo a otro.
class AgentState(TypedDict):
    original_text: str  # El texto completo del PDF
    filter_decision: str  # La decisión del primer agente ('Sí' o 'No')
    extracted_content: str # El contenido limpio del segundo agente
    # `add_messages` es una función especial que LangGraph usa para gestionar el historial de chat de los agentes.
    messages: Annotated[list, add_messages]


# --- Definición de los Nodos del Grafo ---
# Cada nodo es una función que ejecuta un agente y modifica el estado.

def run_filter_agent(state: AgentState):
    """Ejecuta el agente de filtro y actualiza el estado con su decisión."""
    print("---EJECUTANDO AGENTE DE FILTRO---")
    agent_input = {"messages": [HumanMessage(content=state["original_text"])]}
    result = filter_agent_runnable.invoke(agent_input)
    decision = result['messages'][-1].content
    return {"filter_decision": decision}

def run_extraction_agent(state: AgentState):
    """Ejecuta el agente de extracción y actualiza el estado con el contenido limpio."""
    print("---EJECUTANDO AGENTE DE EXTRACCIÓN---")
    agent_input = {"messages": [HumanMessage(content=state["original_text"])]}
    result = extraction_agent_runnable.invoke(agent_input)
    extracted_text = result['messages'][-1].content
    return {"extracted_content": extracted_text}

# --- NUEVO NODO: Ejecutar la pipeline RAG ---
def rag_pipeline_node(state: AgentState):
    """Ejecuta la pipeline RAG para guardar el contenido en Supabase."""
    print("---INICIANDO NODO DE PIPELINE RAG---")
    run_rag_pipeline(state["extracted_content"])
    # Este nodo no necesita modificar el estado, solo ejecuta una acción.
    return {}

# --- NUEVO NODO: Enviar notificación por correo ---
def send_email_node(state: AgentState):
    """Ejecuta el envío del correo de notificación."""
    print("---INICIANDO NODO DE ENVÍO DE CORREO---")
    send_notification_email_smtp()
    # Este nodo tampoco modifica el estado.
    return {}

# --- Definición del Borde Condicional ---
# Esta función decide a qué nodo ir después del filtro.
def should_continue(state: AgentState):
    """Decide si continuar con la extracción o terminar el proceso."""
    print(f"---DECISIÓN DEL FILTRO: {state['filter_decision']}---")
    if "sí" in state["filter_decision"].lower():
        # Si la decisión es 'Sí', vamos al nodo de extracción.
        return "extract_node"
    else:
        # Si es 'No', terminamos el grafo.
        return END


# ----------------------------- Construcción del Grafo ------------------------------
workflow = StateGraph(AgentState)

# 1. Añadir los nodos al grafo
workflow.add_node("filter_node", run_filter_agent)
workflow.add_node("extract_node", run_extraction_agent)
workflow.add_node("rag_node", rag_pipeline_node) # NUEVO NODO
workflow.add_node("email_node", send_email_node) # NUEVO NODO

# 2. Definir el punto de entrada
workflow.set_entry_point("filter_node")

# 3. Añadir el borde condicional desde el filtro
workflow.add_conditional_edges(
    "filter_node",
    should_continue,
    {
        "extract_node": "extract_node",
        END: END
    }
)

# 4. Añadir las aristas (edges) secuenciales para el flujo exitoso
workflow.add_edge("extract_node", "rag_node")
workflow.add_edge("rag_node", "email_node")
workflow.add_edge("extract_node", END)

# 5. Compilar el grafo en un objeto ejecutable
app = workflow.compile()


# --- Función Principal que llamará Streamlit ---
def run_graph_pipeline(text: str) -> dict:
    """
    Ejecuta el grafo completo.
    Ahora devuelve el estado final completo para que Streamlit pueda inspeccionarlo.
    """
    initial_state = {
        "original_text": text,
        "messages": []
    }
    # Invocamos el grafo y devolvemos el estado final
    final_state = app.invoke(initial_state)
    return final_state