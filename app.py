import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
from datetime import date

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Nails Art Natt", page_icon="🦇")

# --- 2. TUS DATOS ---
MI_DIRECCION_GABINETE = "Obispo Piedra Buena y Av.San Martin-Los Ralos"
MI_TELEFONO = "3816914692" 
MI_INSTAGRAM = "@nattdiaz98"

# Título
st.title(" Nails Art Natt")
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

# --- 4. CEREBRO ANTI-SUPERPOSICIÓN ---
def turno_disponible(hoja, fecha_elegida, hora_elegida):
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    if df.empty:
        return True
    
    # Normalizamos encabezados
    df.columns = [col.capitalize() for col in df.columns]
    
    coincidencias = df[
        (df["Fecha"].astype(str) == str(fecha_elegida)) & 
        (df["Hora"].astype(str) == str(hora_elegida))
    ]
    
    if not coincidencias.empty:
        return False 
    return True

# --- 5. EL FORMULARIO ---
with st.form("mi_formulario"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre y Apellido")
        telefono = st.text_input("Teléfono / WhatsApp")
        servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Semipermanentes"])

    with col2:
        fecha = st.date_input("Selecciona la Fecha", min_value=date.today())
        horarios = ["17:00", "19:20", "21:30"]
        hora = st.selectbox("Selecciona la Hora", horarios)
    
    st.divider()
    
    # --- NUEVA SECCIÓN: TIPO DE ATENCIÓN ---
    # Usamos radio botones para que sea fácil elegir
    tipo_atencion = st.radio("¿Dónde realizamos el servicio?", ["En Mi Domicilio", "A Domicilio 🛵"])
    
    # Variable para guardar la dirección final
    direccion_cliente = ""
    
    # Solo si elige domicilio, mostramos el campo para escribir dirección
    if tipo_atencion == "A Domicilio 🛵":
        st.info("ℹ️ Por favor ingresa tu dirección exacta (Calle y Número).")
        direccion_input = st.text_input("Dirección del Domicilio")
    else:
        direccion_input = "En Mi Domicilio " # Si va al local, guardamos esto automático

    # Botón para enviar
    enviado = st.form_submit_button("CONFIRMAR RESERVA")

# --- 6. LÓGICA DE GUARDADO ---
if enviado:
    # A. Validaciones básicas
    if not nombre or not telefono:
        st.warning("⚠️ Por favor completa tu Nombre y Teléfono.")
        st.stop()
    
    # B. Validación de Dirección (NUEVO)
    # Si eligió domicilio y NO escribió dirección, frenamos.
    if tipo_atencion == "A Domicilio 🛵" and not direccion_input:
        st.error("⛔ Para ir a domicilio, necesitamos que escribas tu dirección.")
        st.stop()

    # C. Validar Domingo
    if fecha.weekday() == 6:
        st.error("⛔ Lo sentimos, los Domingos estamos cerrados.")
        st.stop()

    # D. Guardado
    with st.spinner("Verificando disponibilidad..."):
        hoja = conectar_google_sheets()
        if hoja:
            libre = turno_disponible(hoja, fecha, hora)
            
            if not libre:
                st.error(f"❌ ¡Ups! El turno del {fecha} a las {hora} ya está ocupado.")
                st.info("Por favor elige otro horario.")
            else:
                # Preparamos el dato de ubicación final
                ubicacion_final = direccion_input
                
                # Guardamos las 6 columnas
                fila = [nombre, telefono, servicio, str(fecha), str(hora), ubicacion_final]
                hoja.append_row(fila)
                
                # ÉXITO GÓTICO 🦇
                st.markdown("## 🦇 ¡Turno Agendado con Éxito! 🤘")
                st.success("¡Tu cita ha sido confirmada!")
                
                # Tarjeta Dinámica (Cambia según si es domicilio o no)
                texto_lugar = ""
                if tipo_atencion == "A Domicilio 🛵":
                    texto_lugar = f"🛵 **Voy a tu Domicilio:** {direccion_input}"
                else:
                    texto_lugar = f"📍 **Te espero en:** {MI_DIRECCION_GABINETE}"

                with st.container(border=True):
                    st.markdown(f"""
                    ### 🎫 Comprobante de Turno
                    **Cliente:** {nombre}
                    **Servicio:** {servicio}
                    
                    🗓️ **Fecha:** {fecha}
                    ⏰ **Hora:** {hora}
                    
                    ---
                    {texto_lugar}
                    
                    📞 **Mi Contacto:** {MI_TELEFONO}
                    📸 **Instagram:** {MI_INSTAGRAM}
                    
                    *Por favor guarda una captura de esta pantalla.*
                    """)