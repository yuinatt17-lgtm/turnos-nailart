import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
from datetime import date
from streamlit_extras.let_it_rain import rain 

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Nails Art Natt", page_icon="🦇")

# --- 2. TUS DATOS ---
MI_DIRECCION_GABINETE = "Obispo Piedra Buena y San Martin Los Ralos"
MI_TELEFONO = "381 6914692" 
MI_INSTAGRAM = "@nattdiaz98"

# Título MAGENTA
st.markdown("<h1 style='text-align: center; color: #E6007A;'>💅 Nails Art Natt</h1>", unsafe_allow_html=True)
st.write("Completa el formulario para agendar tu cita.")

# --- 3. CONEXIÓN CON GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# --- 4. CEREBRO ANTI-SUPERPOSICIÓN (VERSIÓN DETECTIVE 🕵️‍♀️) ---
def turno_disponible(hoja, fecha_elegida, hora_elegida):
    # Traemos todos los datos
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    # Si la hoja está vacía de verdad, pase libre
    if df.empty:
        return True, None
    
    # Limpieza de encabezados
    df.columns = [col.strip().capitalize() for col in df.columns]
    
    # ⚠️ TRUCO CLAVE: Filtramos filas que tengan la fecha vacía
    # Esto evita que filas "fantasmas" bloqueen los turnos
    if "Fecha" in df.columns:
        df = df[df["Fecha"].astype(str).str.strip() != ""]

    # Buscamos coincidencias
    coincidencias = df[
        (df["Fecha"].astype(str) == str(fecha_elegida)) & 
        (df["Hora"].astype(str) == str(hora_elegida))
    ]
    
    # Si encontramos algo, devolvemos Falso y el nombre del culpable
    if not coincidencias.empty:
        # Intentamos obtener el nombre, si no existe ponemos "Alguien"
        nombre_ocupante = "Alguien"
        if "Nombre" in df.columns:
            nombre_ocupante = coincidencias.iloc[0]["Nombre"]
        return False, nombre_ocupante
        
    return True, None

# --- 5. EL FORMULARIO ---
with st.form("mi_formulario"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre y Apellido")
        telefono = st.text_input("Teléfono / WhatsApp")
        # LISTA DE SERVICIOS
        servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Semipermanentes", "Retiro", "Press On"])

    with col2:
        fecha = st.date_input("Selecciona la Fecha", min_value=date.today())
        # TUS HORARIOS
        horarios = ["17:00", "19:20", "21:30"]
        hora = st.selectbox("Selecciona la Hora", horarios)
    
    # --- 💅 SECCIÓN ESPECIAL PRESS ON (ARGENTINA 0-9) ---
    datos_press_on = "" 
    
    if servicio == "Press On":
        st.markdown("---")
        st.markdown("### 🖤 Personaliza tus Press On")
        
        # 1. Elección de Forma
        formas_disponibles = [
            "Stiletto", "Coffin", 
            "Almendra Corta", "Almendra Larga", 
            "Cuadrada Corta", "Cuadrada Larga"
        ]
        forma = st.selectbox("Elige la Forma y Largo", formas_disponibles)
        
        st.write("---")
        st.markdown("### 📏 Tus Medidas (Tips del 0 al 9)")
        st.caption("Ingresa el número de Tip para cada dedo.")
        
        # 2. Elección de Medidas (0-9)
        c1, c2, c3, c4, c5 = st.columns(5)
        numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
        with c1: pulgar = st.selectbox("👍 Pulgar", numeros, index=0)
        with c2: indice = st.selectbox("👆 Índice", numeros, index=4)
        with c3: mayor = st.selectbox("🖕 Mayor", numeros, index=3)
        with c4: anular = st.selectbox("💍 Anular", numeros, index=4)
        with c5: menique = st.selectbox("🤙 Meñique", numeros, index=7)
            
        datos_press_on = f" | {forma} | Medidas: {pulgar}-{indice}-{mayor}-{anular}-{menique}"
        st.info("ℹ️ **Nota:** Las Press On requieren 48hs de elaboración.")

    st.divider()
    
    # --- LÓGICA DE DOMICILIO ---
    es_domicilio = st.checkbox("¿Necesitas servicio a domicilio? 🛵")
    direccion_final = "" 
    
    if es_domicilio:
        st.info("ℹ️ Iré a tu casa. Por favor ingresa tu dirección exacta.")
        direccion_input = st.text_input("Tu Dirección (Calle y Número)")
        direccion_final = direccion_input 
    else:
        st.info(f"📍 Te espero en mi domicilio: **{MI_DIRECCION_GABINETE}**")
        direccion_final = "En mi Domicilio (Cliente viene)"

    enviado = st.form_submit_button("CONFIRMAR RESERVA")

# --- 6. LÓGICA DE GUARDADO ---
if enviado:
    if not nombre or not telefono:
        st.warning("⚠️ Por favor completa tu Nombre y Teléfono.")
        st.stop()
    
    if es_domicilio and not direccion_input:
        st.error("⛔ Marcaste servicio a domicilio, pero no escribiste la dirección.")
        st.stop()

    if fecha.weekday() == 6:
        st.error("⛔ Lo sentimos, los Domingos estamos cerrados.")
        st.stop()

    with st.spinner("Revisando disponibilidad..."):
        hoja = conectar_google_sheets()
        if hoja:
            # Usamos la nueva función DETECTIVE que nos devuelve 2 cosas
            esta_libre, nombre_ocupante = turno_disponible(hoja, fecha, hora)
            
            if not esta_libre:
                # AQUI MOSTRAMOS QUIÉN TIENE EL TURNO
                st.error(f"❌ ¡Ups! Ese turno ya está reservado por: {nombre_ocupante}")
                st.info("Por favor elige otro horario.")
            else:
                servicio_guardar = servicio + datos_press_on 
                # Agregamos una columna vacía al final para el "Estado" del calendario
                fila = [nombre, telefono, servicio_guardar, str(fecha), str(hora), direccion_final, ""]
                hoja.append_row(fila)
                
                rain(emoji="🦇", font_size=54, falling_speed=5, animation_length="1")
                
                st.markdown("## 🦇 ¡Turno Agendado con Éxito! 🤘")
                st.success("¡Tu cita ha sido confirmada!")
                
                texto_ubicacion = ""
                if es_domicilio:
                    texto_ubicacion = f"🛵 **Voy a tu Domicilio:** {direccion_final}"
                else:
                    texto_ubicacion = f"📍 **Te espero en:** {MI_DIRECCION_GABINETE}"

                with st.container(border=True):
                    st.markdown(f"""
                    ### 🎫 Comprobante de Turno
                    **Cliente:** {nombre}
                    **Servicio:** {servicio}
                    
                    🗓️ **Fecha:** {fecha}
                    ⏰ **Hora:** {hora}
                    
                    ---
                    {texto_ubicacion}
                    
                    📞 **Mi Contacto:** {MI_TELEFONO}
                    📸 **Instagram:** {MI_INSTAGRAM}
                    
                    *Por favor guarda una captura de esta pantalla.*
                    """)