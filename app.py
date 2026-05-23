import streamlit as st
from google import genai
import os
import json
from dotenv import load_dotenv

from db import save_message, get_history, init_db
from cache import get_vocabulary, add_vocabulary, increment_error_count, get_error_count

load_dotenv()
init_db()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.set_page_config(
    page_title="AI Language Tutor",
    page_icon="🎓",
    layout="wide"
)

# --- BARRA LATERAL: Progreso del Estudiante (Usando Redis) ---
st.sidebar.title("📊 Tu Progreso")

st.sidebar.subheader("❌ Errores Corregidos")
errores = get_error_count()
st.sidebar.metric(label="Total de tropiezos", value=errores)

st.sidebar.subheader("📖 Vocabulario Aprendido")
vocabulario = get_vocabulary()

if vocabulario:
    for palabra, significado in vocabulario.items():
        st.sidebar.markdown(f"**{palabra}**: {significado}")
else:
    st.sidebar.caption("Aún no has aprendido palabras nuevas en esta sesión.")

if st.sidebar.button("Limpiar historial de progreso"):
    import redis
    r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    r.flushdb()
    st.sidebar.success("¡Progreso reiniciado!")
    st.restart()


# --- CUERPO PRINCIPAL ---
st.title("🎓 Tutor de Idiomas Inteligente")
st.subheader("Practica inglés (o cualquier idioma) y recibe feedback en tiempo real.")

history = get_history()

for role, message in history:
    with st.chat_message(role):
        st.markdown(message)

prompt = st.chat_input("Escribe tu mensaje en el idioma que estás aprendiendo...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    save_message("user", prompt)

    with st.spinner("El tutor está analizando tu mensaje..."):
        # Definimos las instrucciones del sistema para guiar el comportamiento de Gemini 2.5 Flash
        system_instruction = """
        Eres un tutor de idiomas nativo, empático y altamente calificado. Tu objetivo es ayudar al usuario a mejorar su fluidez y gramática.
        
        Sigue estrictamente estas reglas en cada respuesta:
        1. Responde a lo que el usuario te dice de forma natural en el idioma que se está practicando.
        2. Si el usuario cometió un error gramatical o de vocabulario, corrígelo amablemente al final de tu respuesta usando el formato: [CORRECCION: explicación breve].
        3. Identifica una palabra avanzada, modismo (idiom) o vocabulario útil que haya surgido en la conversación y que el usuario deba aprender. Devuélvela SIEMPRE al final de tu respuesta en formato JSON estricto, así:
        [DATA: {"palabra": "palabra_en_ingles", "significado": "explicación en español"}]
        Si no hay palabra relevante, no incluyas el bloque [DATA:].
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction
            }
        )
        
        full_response_text = response.text

        # --- PROCESAMIENTO DE METADATOS (Redis) ---
        # 1. Detectar si hubo corrección de errores
        if "[CORRECCION:" in full_response_text:
            increment_error_count()

        # 2. Extraer vocabulario si Gemini lo envió en el formato solicitado
        text_to_show = full_response_text
        if "[DATA:" in full_response_text:
            try:
                # Separamos el texto limpio del JSON de datos
                parts = full_response_text.split("[DATA:")
                text_to_show = parts[0].strip()
                json_str = parts[1].split("]")[0].strip()
                
                data = json.loads(json_str)
                if "palabra" in data and "significado" in data:
                    add_vocabulary(data["palabra"], data["significado"])
            except Exception as e:
                # Si falla el parseo, dejamos el texto tal cual para no romper la app
                text_to_show = full_response_text

    with st.chat_message("assistant"):
        st.markdown(text_to_show)

    save_message("assistant", text_to_show)
    
    # Forzar refresco de Streamlit para actualizar la barra lateral con los datos de Redis
    st.rerun()
