import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
from datetime import date
from streamlit_extras.let_it_rain import rain 

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nails Art Natt", page_icon="💅")

MI_DIRECCION_GABINETE = "Obispo Piedra Buena y San Martin Los Ralos"
MI_TELEFONO = "381 123 4567" 
MI_INSTAGRAM = "@tus_uñas_art"

st.markdown("<h1 style='text-align: center; color: #E6007A;'>💅 Nails Art Natt</h1>", unsafe_allow_html=True)
st.write("Completa el formulario para agendar tu cita.")

# --- 2. CONEXIÓN ---
def conectar_google_sheets():
    try:
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        # Asegúrate de que este nombre coincida con tu archivo (turnos_db o turnos_v2)
        sheet = client.open("turnos_db").sheet1 
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# --- 3. FUNCIÓN DETECTIVE ---
def turno_disponible(hoja, fecha_elegida, hora_elegida):
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    if df.empty: return True, None
    df.columns = [col.strip().capitalize() for col in df.columns]
    if "Fecha" in df.columns:
        df = df[df["Fecha"].astype(str).str.strip() != ""]
    coincidencias = df[(df["Fecha"].astype(str) == str(fecha_elegida)) & (df["Hora"].astype(str) == str(hora_elegida))]
    if not coincidencias.empty:
        nombre = coincidencias.iloc[0]["Nombre"] if "Nombre" in df.columns else "Alguien"
        return False, nombre
    return True, None

# ==========================================
# 🚀 PASO 1: ELEGIR SERVICIO (FUERA DEL FORMULARIO)
# ==========================================
# Al estar afuera, la app se actualiza al instante cuando cambias la opción.
servicio = st.selectbox(
    "✨ ¿Qué servicio te gustaría realizarte?", 
    ["Soft Gel", "Capping", "Semipermanentes", "Retiro", "Press On"]
)

# Variable para guardar los detalles si es Press On
datos_press_on = ""

# Si elige Press On, mostramos las opciones AQUÍ MISMO (antes de reservar)
if servicio == "Press On":
    st.markdown("### 🖤 Personaliza tus Press On")
    st.info("👇 Elige tus formas y medidas antes de reservar el turno.")
    
    col_forma, col_largo = st.columns(2)
    with col_forma:
        forma = st.selectbox("Forma", ["Stiletto", "Coffin", "Almendra", "Cuadrada"])
    with col_largo:
        largo = st.selectbox("Largo", ["Corta", "Mediana", "Larga", "Extra Larga"])

    st.caption("📏 Tus Medidas (Tips del 0 al 9)")
    c1, c2, c3, c4, c5 = st.columns(5)
    numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    with c1: pulgar = st.selectbox("👍 Pulgar", numeros, index=0)
    with c2: indice = st.selectbox("👆 Índice", numeros, index=4)
    with c3: mayor = st.selectbox("🖕 Mayor", numeros, index=3)
    with c4: anular = st.selectbox("💍 Anular", numeros, index=4)
    with c5: menique = st.selectbox("🤙 Meñique", numeros, index=7)
    
    datos_press_on = f" | {forma} {largo} | Medidas: {pulgar}-{indice}-{mayor}-{anular}-{menique}"

st.divider()

# ==========================================
# 🚀 PASO 2: DATOS Y FECHA (DENTRO DEL FORMULARIO)
# ==========================================
with st.form("mi_formulario"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre y Apellido")
        telefono = st.text_input("Teléfono / WhatsApp")
        # El servicio YA NO está aquí, ya lo elegimos arriba

    with col2:
        fecha = st.date_input("Selecciona la Fecha", min_value=date.today())
        horarios = ["17:00", "19:20", "21:30"]
        hora = st.selectbox("Selecciona la Hora", horarios)
    
    # Checkbox Domicilio
    st.markdown("---")
    es_domicilio = st.checkbox("¿Necesitas servicio a domicilio? 🛵")
    direccion_input = ""
    
    if es_domicilio:
        st.warning("⚠️ Recuerda escribir tu dirección abajo.")
        direccion_input = st.text_input("Tu Dirección (Calle y Número)")
    else:
        st.info(f"📍 Te espero en: {MI_DIRECCION_GABINETE}")

    # --- BOTÓN ÚNICO DE CONFIRMACIÓN ---
    enviado = st.form_submit_button("CONFIRMAR RESERVA")

# ==========================================
# 🚀 PASO 3: GUARDADO
# ==========================================
if enviado:
    # Validaciones
    if not nombre or not telefono:
        st.warning("⚠️ Faltan datos: Nombre o Teléfono.")
        st.stop()
    
    if es_domicilio and not direccion_input:
        st.error("⛔ Para ir a domicilio, necesito la dirección.")
        st.stop()

    if fecha.weekday() == 6:
        st.error("⛔ Domingos cerrado.")
        st.stop()
    
    # Preparamos la dirección final
    dir_final = direccion_input if es_domicilio else "En Gabinete"

    with st.spinner("Reservando..."):
        hoja = conectar_google_sheets()
        if hoja:
            libre, ocupante = turno_disponible(hoja, fecha, hora)
            
            if not libre:
                st.error(f"❌ Turno ocupado por: {ocupante}")
            else:
                # Unimos el servicio con los datos de Press On (si los hay)
                servicio_completo = servicio + datos_press_on
                
                fila = [nombre, telefono, servicio_completo, str(fecha), str(hora), dir_final, ""]
                hoja.append_row(fila)
                
                rain(emoji="🦇", font_size=54, falling_speed=5, animation_length="1")
                st.balloons()
                
                st.success("¡Turno Agendado!")
                
                # Comprobante
                with st.container(border=True):
                    st.markdown(f"""
                    ### 🎫 Comprobante
                    **Cliente:** {nombre}
                    **Servicio:** {servicio_completo}
                    🗓️ **{fecha}** a las **{hora}**
                    📍 **Lugar:** {dir_final}
                    """)