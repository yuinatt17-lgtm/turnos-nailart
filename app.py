import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
from datetime import date

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Reserva tu Turno", page_icon="💅")

# --- 2. TUS DATOS (¡EDITA ESTO!) ---
# Aquí es donde tú pones tu info real en VS Code:
MI_DIRECCION = "Obispo Piedra Buena y San Martin - Los Ralos"
MI_TELEFONO = "381 6914692" 
MI_INSTAGRAM = "@nattdiaz98"

# Título de la web
st.title("🦇Nails Art Natt🦇")
st.write("Completa tus datos para agendar tu cita.")

# --- 3. CONEXIÓN CON GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        # Leemos la llave secreta
        json_creds = json.loads(st.secrets["google_credentials"]["json_key"])
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
        client = gspread.authorize(creds)
        
        # Abrimos la hoja (Asegúrate que se llame turnos_db)
        sheet = client.open("turnos_db").sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return None

# --- 4. CEREBRO ANTI-SUPERPOSICIÓN 🧠 ---
def turno_disponible(hoja, fecha_elegida, hora_elegida):
    # Bajamos los datos actuales
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    
    # Si la hoja está vacía, ¡está libre!
    if df.empty:
        return True
    
    # Convertimos a texto para comparar sin errores
    # Buscamos: ¿Existe alguna fila con ESA fecha Y ESA hora?
    coincidencias = df[
        (df["Fecha"].astype(str) == str(fecha_elegida)) & 
        (df["Hora"].astype(str) == str(hora_elegida))
    ]
    
    # Si encontró coincidencias, NO está disponible
    if not coincidencias.empty:
        return False 
    return True

# --- 5. EL FORMULARIO ---
with st.form("mi_formulario"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre y Apellido")
        telefono = st.text_input("Teléfono / WhatsApp")
        servicio = st.selectbox("Servicio" , ["Soft Gel","Capping","Retiro"])

    with col2:
        # Calendario: min_value=date.today() impide elegir ayer
        fecha = st.date_input("Selecciona la Fecha", min_value=date.today())
        
        # Horarios fijos que me pediste
        horarios = ["17:00", "19:20", "21:30"]
        hora = st.selectbox("Selecciona la Hora", horarios)

    # Botón para enviar
    enviado = st.form_submit_button("CONFIRMAR RESERVA")

# --- 6. QUÉ PASA AL TOCAR EL BOTÓN ---
if enviado:
    # A. Validamos que haya escrito nombre y teléfono
    if not nombre or not telefono:
        st.warning("⚠️ Por favor completa tu Nombre y Teléfono.")
        st.stop()

    # B. Validamos que no sea Domingo (0=Lunes, 6=Domingo)
    if fecha.weekday() == 6:
        st.error("⛔ Lo sentimos, los Domingos estamos cerrados.")
        st.stop()

    # C. Proceso de Guardado
    with st.spinner("Verificando disponibilidad..."):
        hoja = conectar_google_sheets()
        if hoja:
            # Verificamos si el lugar está libre
            libre = turno_disponible(hoja, fecha, hora)
            
            if not libre:
                st.error(f"❌ ¡Ups! El turno del {fecha} a las {hora} ya está ocupado.")
                st.info("Por favor elige otro horario.")
            else:
                # D. GUARDAMOS EL TURNO (Las 5 columnas)
                # Cliente | Telefono | Servicio | Fecha | Hora
                fila = [nombre, telefono, servicio, str(fecha), str(hora)]
                hoja.append_row(fila)
                
                # E. ÉXITO Y COMPROBANTE
            # Quitamos los globos y ponemos el estilo metalero
              st.markdown("## 🦇 ¡Turno Agendado con Éxito! 🤘") 
              st.success("¡Tu cita ha sido confirmada!")
            

                
                # Tarjeta bonita para captura
                with st.container(border=True):
                    st.markdown(f"""
                    ### 🎫 Comprobante de Turno
                    **Cliente:** {nombre}
                    **Servicio:** {servicio}
                    
                    🗓️ **Fecha:** {fecha}
                    ⏰ **Hora:** {hora}
                    
                    ---
                    📍 **Lugar:** {MI_DIRECCION}
                    📞 **Contacto:** {MI_TELEFONO}
                    📸 **Instagram:** {MI_INSTAGRAM}
                    
                    *Por favor guarda una captura de esta pantalla.*
                    """)