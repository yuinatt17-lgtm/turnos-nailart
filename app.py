import streamlit as st
import pandas as pd
import gspread
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.title("💅 Gestión de Turnos - Nail Art")
st.write("Reserva tu turno y quedará guardado en Google Sheets.")

# --- CONEXIÓN DIRECTA (SOLUCIÓN AL ERROR) ---
def conectar_google_sheets():
    try:
        # 1. Recuperamos la llave de los Secrets
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        
        # 2. Usamos el método directo de gspread (ESTO EVITA EL ERROR 200)
        client = gspread.service_account_from_dict(json_creds)
        
        # 3. Abrimos la hoja
        # Asegúrate de que tu hoja se llame turnos_db
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error al conectar: {e}")
        return None

# --- FORMULARIO ---
col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre del Cliente")
    servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Service", "Esmaltado", "Retiro"])

with col2:
    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")

# --- BOTÓN DE GUARDAR ---
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
        st.warning("⚠️ Escribe un nombre por favor.")

# --- VER TURNOS ---
st.divider()
if st.checkbox("Ver turnos agendados"):
    hoja = conectar_google_sheets()
    if hoja:
        datos = hoja.get_all_records()
        st.dataframe(datos)