import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.title("💅 Gestión de Turnos - Nail Art")
st.write("Reserva tu turno y quedará guardado en Google Sheets.")

# --- CONEXIÓN CON GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        # 1. Recuperamos la llave de la "Caja Fuerte" de Streamlit
        # OJO: Esto debe coincidir con lo que escribiste en Secrets: [google_credentials]
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        
        # 2. Nos identificamos con Google
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        
        # 3. Abrimos la hoja (¡Debe llamarse IGUAL que en tu Drive!)
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google: {e}")
        return None

# --- EL FORMULARIO ---
col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre del Cliente")
    servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Service", "Esmaltado", "Retiro"])

with col2:
    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")

# --- BOTÓN PARA GUARDAR ---
if st.button("Reservar Turno"):
    if nombre:
        with st.spinner("Guardando en la nube..."):
            hoja = conectar_google_sheets()
            if hoja:
                # Preparamos los datos
                fila_nueva = [nombre, servicio, str(fecha), str(hora)]
                
                # ¡El Robot escribe en la hoja!
                hoja.append_row(fila_nueva)
                
                st.success(f"✅ ¡Listo! Turno agendado para **{nombre}**.")
                st.balloons()
    else:
        st.warning("⚠️ Por favor, escribe un nombre.")

# --- VER AGENDA (Opcional) ---
st.divider()
if st.checkbox("Ver turnos agendados"):
    hoja = conectar_google_sheets()
    if hoja:
        # Traemos todos los datos de la hoja
        datos = hoja.get_all_records()
        if datos:
            st.dataframe(datos)
        else:
            st.info("La hoja está vacía.")