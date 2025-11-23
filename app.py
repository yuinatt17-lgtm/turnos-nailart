import streamlit as st
import pandas as pd
import os

# Nombre del archivo donde guardaremos los datos
ARCHIVO_TURNOS = "turnos.csv"

st.title("💅 Gestión de Turnos - Nail Art")

# --- PARTE 1: EL FORMULARIO ---
st.write("### Nuevo Turno")
col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre del Cliente")
    servicio = st.selectbox("Servicio", ["Soft Gel", "Capping", "Service", "Esmaltado", "Retiro"])

with col2:
    fecha = st.date_input("Fecha")
    hora = st.time_input("Hora")

# Botón para guardar
if st.button("Reservar Turno"):
    if nombre: # Solo guarda si escribieron un nombre
        # 1. Creamos un pequeño paquete de datos (DataFrame)
        nuevo_turno = pd.DataFrame({
            "Cliente": [nombre],
            "Servicio": [servicio],
            "Fecha": [fecha],
            "Hora": [str(hora)] # Convertimos la hora a texto para que no de problemas
        })

        # 2. Guardamos en el archivo CSV (sin borrar lo anterior)
        if not os.path.isfile(ARCHIVO_TURNOS):
            # Si el archivo no existe, lo crea con encabezados
            nuevo_turno.to_csv(ARCHIVO_TURNOS, index=False)
        else:
            # Si ya existe, agrega la información abajo (mode='a')
            nuevo_turno.to_csv(ARCHIVO_TURNOS, mode='a', header=False, index=False)
        
        st.success(f"✅ ¡Listo! Turno guardado para {nombre}.")
    else:
        st.error("⚠️ Por favor, escribe el nombre del cliente.")

# --- PARTE 2: VER LA AGENDA ---
st.divider() # Una línea divisoria visual
st.write("### 📅 Agenda Guardada")

# Si el archivo existe, lo leemos y mostramos la tabla
if os.path.isfile(ARCHIVO_TURNOS):
    df_turnos = pd.read_csv(ARCHIVO_TURNOS)
    st.dataframe(df_turnos, use_container_width=True)
else:
    st.info("Aún no hay turnos guardados.")