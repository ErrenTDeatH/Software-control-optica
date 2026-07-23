import streamlit as st
import os
from datetime import datetime
from utils.config import config
from PIL import Image

def render_setup_wizard():
    """
    Pantalla de bienvenida y configuración inicial para nuevos clientes.
    Simplificada: Solo identidad visual y datos básicos.
    """
    # Centrar el contenido
    st.markdown("""
        <style>
        .setup-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        .setup-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .setup-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #0f172a;
        }
        .setup-subtitle {
            color: #64748b;
            font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
            <div class="setup-header">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
                <div class="setup-title">¡Bienvenido a tu Nuevo Sistema!</div>
                <div class="setup-subtitle">Vamos a configurar tu óptica en un solo paso.</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("setup_form"):
            st.markdown("### 🏢 Información de tu Óptica")
            col1, col2 = st.columns(2)
            
            app_name = col1.text_input("Nombre de la Óptica *", value=config.APP_NAME, help="Ej: Óptica Visión Real")
            owner_ruc = col2.text_input("RUC / Identificación Fiscal *", value=config.OWNER_RUC)
            
            owner_name = col1.text_input("Propietario / Representante Legal", value=config.OWNER_NAME)
            support_phone = col2.text_input("Teléfono de contacto (WhatsApp)", value=config.SUPPORT_PHONE)
            
            st.markdown("### 🎨 Identidad Visual")
            c1, c2 = st.columns([1, 2])
            primary_color = c1.color_picker("Color Principal de tu Marca", value=config.PRIMARY_COLOR)
            
            st.markdown("---")
            st.markdown("### 🖼️ Carga tu Logo")
            logo_file = st.file_uploader("Sube el logo de tu óptica (PNG o JPG)", type=["png", "jpg", "jpeg"])
            
            if logo_file:
                st.image(logo_file, width=200, caption="Previsualización de tu logo")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("✅ COMPLETAR CONFIGURACIÓN Y COMENZAR", use_container_width=True)

            if submit:
                if not app_name or not owner_ruc:
                    st.error("Por favor completa los campos obligatorios (*)")
                else:
                    # Guardar Logo
                    if logo_file:
                        try:
                            # Guardamos el logo reemplazando el existente
                            img = Image.open(logo_file)
                            img.save("logo.png")
                            config.LOGO_PATH = "logo.png"
                        except Exception as e:
                            st.error(f"Error guardando el logo: {e}")

                    # Actualizar Config
                    config.APP_NAME = app_name
                    config.OWNER_RUC = owner_ruc
                    config.OWNER_NAME = owner_name
                    config.SUPPORT_PHONE = support_phone
                    config.PRIMARY_COLOR = primary_color
                    config.STORAGE_MODE = "LOCAL" # Forzado a Local por simplicidad
                    config.FOOTER_TEXT = f"© {datetime.now().year} {app_name} · Sistema de Gestión"
                    config.SETUP_COMPLETED = True
                    
                    config.save_config()
                    st.success("¡Configuración guardada con éxito!")
                    st.balloons()
                    st.rerun()
