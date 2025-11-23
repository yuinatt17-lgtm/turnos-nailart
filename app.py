import streamlit as st
import pandas as pd
import gspread
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Turnos Nail Art", page_icon="💅")
st.title("💅 Gestión de Turnos - Nail Art")
st.write("Reserva tu turno y quedará guardado en mi agenda personal.")

# --- CONEXIÓN ---
def conectar_google_sheets():
    try:
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        client = gspread.service_account_from_dict(json_creds)
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# --- FORMULARIO PÚBLICO (ESTO LO VE TODO EL MUNDO) ---
col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre y Apellido")
    servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Service", "Esmaltado", "Retiro"])

with col2:
    fecha = st.date_input("Fecha del turno")
    hora = st.time_input("Hora del turno")

if st.button("Reservar Turno"):
    if nombre:
        with st.spinner("Guardando..."):
            hoja = conectar_google_sheets()
            if hoja:
                fila = [nombre, servicio, str(fecha), str(hora)]
                hoja.append_row(fila)
                st.success(f"✅ ¡Listo, {nombre}! Tu turno quedó registrado.")
                st.balloons()
    else:
        st.warning("⚠️ Por favor completa tu nombre.")

# --- ZONA PRIVADA (SOLO PARA TI) 🔐 ---
st.divider()
st.write("### 🔐 Administración")

# Aquí pedimos una contraseña. Solo si escribes la correcta, se muestra la lista.
password = st.text_input("Ingresa la clave para ver la agenda:", type="password")

if password == "natali123":  # <--- ¡AQUÍ PUEDES CAMBIAR TU CONTRASEÑA!
    hoja = conectar_google_sheets()
    if hoja:
        datos = hoja.get_all_records()
        st.write("### 📅 Turnos Agendados:")
        st.dataframe(datos)
else:
    st.info("Esta zona es solo para la dueña del negocio.")