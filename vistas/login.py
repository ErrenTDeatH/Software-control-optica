import streamlit as st
import os
import base64
from utils.config import config
from database import cargar_sucursales, registrar_auditoria

def render_login(cargar_usuarios_fn):
    """Renders the login screen and handles authentication."""
    # ── CARGA DE IMAGEN DE FONDO (Base64 / URL) ──────────────
    login_bg_url = getattr(config, "LOGIN_BG_URL", "")
    bg_img_path = getattr(config, "LOGIN_BG_PATH", "login_bg.png")
    bg_style = ""
    
    if login_bg_url:
        bg_style = f"background-image: url('{login_bg_url}');"
    elif os.path.exists(bg_img_path):
        try:
            with open(bg_img_path, "rb") as f:
                bin_str = base64.b64encode(f.read()).decode()
            bg_style = f"background-image: url('data:image/png;base64,{bin_str}');"
        except Exception:
            bg_style = f"background: linear-gradient(135deg, {config.PRIMARY_COLOR} 0%, #0f172a 100%);"
    else:
        bg_style = f"background: linear-gradient(135deg, {config.PRIMARY_COLOR} 0%, #0f172a 100%);"

    # ── ESTILOS ESPECÍFICOS DEL LOGIN ────────────────────────
    st.markdown(f"""
    <style>
    /* Fondo dinámico para el area de login */
    .stApp {{
        {bg_style}
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* Ocultar elementos de navegación estándar */
    [data-testid="stSidebar"] {{ display: none !important; }}
    header {{ visibility: hidden !important; }}
    
    .login-wrapper {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 5vh;
    }}

    .glass-card {{
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 15px 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7) !important;
        width: 100%;
        max-width: 400px;
        height: 50mm !important;
        margin: 0 auto;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center; /* Centrado horizontal */
        overflow: hidden;
    }}

    /* Logo centrado y sin recortes extraños */
    .glass-card img {{
        display: block !important;
        margin: 0 auto 10px auto !important; /* Centrado y con espacio inferior */
        max-height: 120mm !important; /* Ajuste para que quepa con el formulario */
        width: auto !important;
        max-width: 90% !important;
        object-fit: contain !important; /* Ver logo completo */
        filter: brightness(0) invert(1) !important;
        opacity: 0.9;
    }}

    /* Espaciado súper compacto para cumplir los 50mm */
    div[data-testid="stTextInput"] {{ margin-top: -5px !important; }}
    div[kind="primary"] {{ margin-top: 5px !important; }}

    .login-header {{
        text-align: center;
        margin-bottom: 35px;
    }}

    .login-header h2 {{
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        margin-bottom: 8px !important;
        letter-spacing: -0.5px !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5) !important; /* Sombra para legibilidad */
    }}

    /* Etiquetas de los campos (Usuario/Contraseña) */
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stTextInput"] label div p {{
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.8) !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin-bottom: 8px !important;
    }}

    /* Cuadro transparente para agrupar Usuario/Contraseña */
    div[data-testid="stForm"] {{
        background: rgba(0, 0, 0, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        margin-top: 5px !important;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2) !important;
    }}

    /* Personalización de inputs */
    div[data-testid="stTextInput"] > div > div > input {{
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 12px !important;
        color: #1e293b !important; /* Texto oscuro para legibilidad sobre blanco */
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }}

    div[data-testid="stTextInput"] > div > div > input:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }}

    /* Contenedor del botón para asegurar centrado perfecto */
    div.stFormSubmitButton {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 15px !important;
    }}

    /* Botón Premium centrado horizontalmente */
    button[kind="primary"], .stButton > button {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 10px 30px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        margin: 0 auto !important;
        display: block !important;
    }}

    button[kind="primary"]:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 15px 30px -5px rgba(37, 99, 235, 0.4) !important;
    }}
    
    .footer-note {{
        margin-top: 40px;
        color: #475569;
        font-size: 0.8rem;
        text-align: center;
        letter-spacing: 0.5px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── LAYOUT DE LOGIN ──────────────────────────────────────
    _, centered_col, _ = st.columns([1, 1.2, 1])

    with centered_col:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        
        # Carga de Logo en Base64 para inyección HTML
        logo_b64 = ""
        logo_path = config.LOGO_PATH if os.path.exists(config.LOGO_PATH) else ("logo.png" if os.path.exists("logo.png") else None)
        if logo_path:
            try:
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()
            except Exception: pass

        logo_html = f'<img src="data:image/png;base64,{logo_b64}" width="220">' if logo_b64 else ""

        st.markdown(f"""
            <div class="glass-card">
                {logo_html}
        """, unsafe_allow_html=True)
        
        # Formulario sin borde nativo
        with st.form("login_form", border=False):
            usuario = st.text_input("Usuario", placeholder="ej: admin")
            password_inp = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            # Botón centrado horizontalmente al final
            submit_login = st.form_submit_button("Ingresar al Sistema", type="primary")
            
            if submit_login:
                _usuarios_act = cargar_usuarios_fn()
                if usuario in _usuarios_act and _usuarios_act[usuario]["password"] == password_inp:
                    ud = _usuarios_act[usuario]
                    raw_role = str(ud.get("role", ""))
                    
                    if raw_role.startswith("INACTIVO:"):
                        st.error("🚫 Tu cuenta ha sido bloqueada. Contacta al administrador.")
                    else:
                        st.session_state.logged_in   = True
                        st.session_state.user_role   = raw_role.replace("INACTIVO:", "")
                        st.session_state.user_name   = ud.get("nombre", usuario)
                        st.session_state.user_login    = usuario
                        st.session_state.user_cargo    = ud.get("cargo", "Optometrista")
                        st.session_state.user_registro = ud.get("registro", "")
                        st.session_state.user_telefono = ud.get("telefono", "")
                        st.session_state.user_firma    = ud.get("firma_base64", "")
                        st.session_state.user_accesos  = ud.get("accesos", ["Pacientes", "Trabajos", "Ventas"])
                        
                        # AUDITORÍA: Inicio de sesión
                        registrar_auditoria(
                            accion="Inicio de Sesión",
                            entidad="Seguridad",
                            detalle=f"Usuario '{usuario}' ingresó al sistema.",
                            usuario=usuario,
                            nombre_usuario=ud.get("nombre", usuario),
                            sucursal="N/A (Previo a selección)"
                        )
                        
                        # Manejo de sucursales (Administradores siempre tienen todas)
                        assigned_branches = ud.get("sucursales_asignadas")
                        
                        if "Administrador" in raw_role:
                            df_s = cargar_sucursales()
                            if not df_s.empty:
                                assigned_branches = df_s["nombre"].tolist()
                            else:
                                assigned_branches = ["Matriz"]
                        
                        if not assigned_branches:
                            assigned_branches = ["Matriz"]
                        elif isinstance(assigned_branches, str):
                            assigned_branches = [assigned_branches]
                            
                        st.session_state.sucursales_asignadas = assigned_branches
                        
                        if len(assigned_branches) == 1:
                            st.session_state.sucursal_activa = assigned_branches[0]
                        else:
                            st.session_state.sucursal_activa = None
                            
                        st.rerun()
                else:
                    # AUDITORÍA: Intento fallido
                    registrar_auditoria(
                        accion="Intento de Acceso Fallido",
                        entidad="Seguridad",
                        detalle=f"Se intentó ingresar con el usuario '{usuario}' pero la contraseña fue incorrecta.",
                        usuario=usuario,
                        sucursal="N/A"
                    )
                    st.error("Credenciales invalidas. Verifica tu usuario y contrasena.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="footer-note">{config.FOOTER_TEXT}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()
