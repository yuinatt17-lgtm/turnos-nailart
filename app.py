import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials # <--- Esta es la librería moderna
import json

# --- CONFIGURACIÓN ---
st.title("💅 Gestión de Turnos - Nail Art")
st.write("Reserva tu turno y quedará guardado en Google Sheets.")

# --- CONEXIÓN MODERNA ---
def conectar_google_sheets():
    try:
        # 1. Leemos la llave de los Secrets
        info_json = json.loads(st.secrets["google_credentials"]["json_key"])
        
        # 2. Definimos los permisos (Scopes)
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 3. Nos autenticamos con la forma NUEVA
        creds = Credentials.from_service_account_info(info_json, scopes=scope)
        client = gspread.authorize(creds)
        
        # 4. Abrimos la hoja
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error detallado: {e}")
        return None

# --- FORMULARIO ---
col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre del Cliente")
    servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Service", "Esmaltado", "Retiro"])

with col2:
    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")

# --- BOTÓN ---
if st.button("Reservar Turno"):
    if nombre:
        with st.spinner("Guardando en la nube..."):
            hoja = conectar_google_sheets()
            if hoja:
                fila = [nombre, servicio, str(fecha), str(hora)]
                hoja.append_row(fila)
                st.success(f"✅ ¡Listo! Turno agendado para **{nombre}**.")
                st.balloons()
    else:
        st.warning("Escribe un nombre por favor.")

# --- VER TURNOS ---
st.divider()
if st.checkbox("Ver turnos agendados"):
    hoja = conectar_google_sheets()
    if hoja:
        datos = hoja.get_all_records()
        st.dataframe(datos)