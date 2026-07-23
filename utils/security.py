import subprocess
import hashlib
import os

def get_hardware_id():
    """
    Obtiene el número de serie de la placa base (Windows).
    """
    try:
        # Comando para Windows (Baseboard Serial Number)
        cmd = "wmic baseboard get serialnumber"
        output = subprocess.check_output(cmd, shell=True).decode().split('\n')
        serial = output[1].strip()
        if not serial or "To be filled" in serial:
            # Fallback a UUID del sistema si el serial de la placa no está disponible
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True).decode().split('\n')
            serial = output[1].strip()
        return serial
    except Exception:
        return "HARDWARE_ID_NOT_FOUND"

def is_license_valid(licensed_uuid):
    """
    Verifica la validez de la licencia usando un hash salteado.
    La semilla debe ser la misma que en generador_licencias.py
    """
    if not licensed_uuid:
        return False
    
    SECRET_SEED = "OPTICA_WHITE_LABEL_2024_PRO_SECRET"
    current_id = get_hardware_id()
    
    # Generar el hash esperado
    raw_key = f"{current_id}-{SECRET_SEED}"
    expected_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    return licensed_uuid == expected_hash

def show_lock_screen():
    """
    Muestra una pantalla de bloqueo premium con formulario de activación.
    """
    import streamlit as st
    import json
    from utils.config import config
    
    st.set_page_config(page_title="Activación Requerida", page_icon="🔐")
    
    hw_id = get_hardware_id()
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        }}
        .lock-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            color: white;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            padding: 40px;
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 550px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .hw-box {{
            background: rgba(0, 0, 0, 0.4);
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #38bdf8;
            font-family: monospace;
            color: #38bdf8;
            font-size: 18px;
            margin: 20px 0;
            user-select: all;
        }}
        </style>
        <div class="lock-container">
            <div class="card">
                <h1 style='margin-bottom:10px;'>🛡️ Sistema Protegido</h1>
                <p style='color:#94a3b8; font-size:15px;'>
                    Esta copia de <b>{config.APP_NAME}</b> no está activada en este equipo.<br>
                    Envíe el siguiente ID al desarrollador para obtener su llave.
                </p>
                <div style='font-size:11px; color:#64748b;'>ID DE EQUIPO (HAGA CLIC PARA COPIAR):</div>
                <div class="hw-box">{hw_id}</div>
                <p style='font-size:13px; color:#cbd5e1; margin-bottom:5px;'>Ingrese su Clave de Activación:</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Formulario de activación de Streamlit (fuera del HTML para que funcione el input)
    with st.container():
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            key_input = st.text_input("Clave", label_visibility="collapsed", placeholder="Pega tu clave aquí...")
            if st.button("🚀 ACTIVAR SISTEMA AHORA", use_container_width=True, type="primary"):
                if is_license_valid(key_input):
                    # Guardar permanentemente en app_config.json
                    try:
                        with open("app_config.json", "r", encoding="utf-8") as f:
                            conf = json.load(f)
                        conf["LICENSED_UUID"] = key_input
                        with open("app_config.json", "w", encoding="utf-8") as f:
                            json.dump(conf, f, indent=4)
                        st.success("✅ ¡Sistema activado correctamente! Reiniciando...")
                        import time
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.error("❌ La clave ingresada no es válida para este equipo.")
            
            st.markdown(f"""
                <div style='text-align:center; margin-top:20px;'>
                    <a href="https://wa.me/593963241158?text=Hola%20Anthonny,%20necesito%20activar%20mi%20óptica.%20ID:{hw_id}" 
                       style='color:#25d366; text-decoration:none; font-weight:bold; font-size:14px;'>
                       💬 Contactar Soporte por WhatsApp
                    </a>
                </div>
            """, unsafe_allow_html=True)
    st.stop()
