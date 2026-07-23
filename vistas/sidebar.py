import streamlit as st
import os
from utils.config import config
from database import registrar_auditoria

def render_sidebar():
    """Renders the main sidebar navigation and user info."""
    with st.sidebar:
        if os.path.exists(config.LOGO_PATH):
            logo_path = config.LOGO_PATH
            st.markdown("<style>[data-testid='stSidebar'] img { filter: brightness(0); padding-bottom: 0px !important; margin-top: -55px !important; }</style>", unsafe_allow_html=True)
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown("""
            <div class="logo-container">
                <p class="logo-hint">📌 Esperando el logo...</p>
                <p style="color:#475569; font-size:12px; margin-top:8px;">
                   Guárdalo como <strong>logo.png</strong> en la carpeta del proyecto.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        # ── NAVEGACIÓN DINÁMICA POR ROLES ────────────────────────
        st.markdown("<p style='color:#475569; font-size:10px; text-transform:uppercase; letter-spacing:1.5px; margin:0 0 10px 0;'>Navegacion</p>", unsafe_allow_html=True)

        _role = st.session_state.user_role
        _accesos = st.session_state.get("user_accesos", ["Inicio", "Pacientes", "Trabajos", "Ventas"])
        
        # Navegacion dinámica basada en permisos
        all_pages = {
            "Inicio":        ("🏠", "Inicio"),
            "Pacientes":     ("👥", "Pacientes"),
            "Citas":         ("📅", "Agendamiento de Citas"),
            "Ventas":        ("🏪", "Registro de Ventas"),
            "Facturación":   ("🧾", "Facturación (SRI)"),
            "Generar Orden": ("📝", "Generar Orden"),
            "Trabajos":      ("📋", "Trabajos"),
            "Inventario":    ("📦", "Inventario"),
            "Contabilidad":  ("💰", "Contabilidad"),
            "Asistente IA":  ("🤖", "Asistente IA Optométrico"),
            "Usuarios":      ("👤", "Gestion de Usuarios"),
            "Configuracion": ("⚙️", "Configuracion"),
        }
        
        pages = {}
        for key, val in all_pages.items():
            # El Administrador ve todo. Otros roles ven solo lo que tienen en 'accesos', excluyendo 'Inicio'.
            if _role == "Administrador":
                pages[key] = val
            elif key in _accesos and key != "Inicio":
                pages[key] = val

        if st.session_state.page not in pages:
            st.session_state.page = "Pacientes" if "Pacientes" in pages else list(pages.keys())[0]

        for key, (icon, label) in pages.items():
            if key in ["Usuarios", "Configuracion"]: continue # Se mueven al pie del sidebar
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

        # ── INFO DEL USUARIO (FILTRADA POR SUCURSAL) ────────────────
        suc_actual = st.session_state.get("sucursal_activa", "Matriz")
        
        # Filtrar dataframes para el resumen
        df_p_view = st.session_state.df_pacientes
        df_h_view = st.session_state.df_historias
        
        if "sucursal" in df_p_view.columns:
            df_p_view = df_p_view[df_p_view["sucursal"] == suc_actual]
        if "sucursal" in df_h_view.columns:
            df_h_view = df_h_view[df_h_view["sucursal"] == suc_actual]
            
        n_pacientes = len(df_p_view)
        n_historias = len(df_h_view)
        
        st.markdown(
            f"<p style='color:#475569; font-size:10px; text-transform:uppercase; letter-spacing:1.5px; margin:0 0 6px 0;'>Resumen ({suc_actual})</p>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        c1.metric("Pacientes", n_pacientes)
        c2.metric("Historias", n_historias)

        st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color:#1e293b; font-size:12px; text-align:center;'>👋 Hola, <b>{st.session_state.user_name}</b><br>"
            f"<span style='color:#64748b; font-size:11px;'>{st.session_state.user_role}</span><br>"
            f"<span style='color:#0ea5e9; font-size:11px; font-weight: bold;'>🏢 {st.session_state.get('sucursal_activa', '')}</span></p>",
            unsafe_allow_html=True
        )
        
        if len(st.session_state.get("sucursales_asignadas", [])) > 1 or st.session_state.get("user_role") == "Administrador":
            if st.button("🏠 Cambiar Sucursal", use_container_width=True):
                st.session_state.sucursal_activa = None
                st.rerun()
                
        # ── BOTONES DE ADMINISTRACIÓN AL FINAL ─────────────────────
        if _role == "Administrador" or "Usuarios" in _accesos or "Configuracion" in _accesos:
            st.markdown("<br>", unsafe_allow_html=True)
            if (_role == "Administrador" or "Usuarios" in _accesos) and st.button("👤 Gestion de Usuarios", key="nav_Usuarios_foot", use_container_width=True):
                st.session_state.page = "Usuarios"
                st.rerun()
            if (_role == "Administrador" or "Configuracion" in _accesos) and st.button("⚙️ Configuracion", key="nav_Config_foot", use_container_width=True):
                st.session_state.page = "Configuracion"
                st.rerun()
                
        if st.button("Cerrar Sesion", use_container_width=True):
            # AUDITORÍA: Cierre de sesión
            registrar_auditoria(
                accion="Cierre de Sesión",
                entidad="Seguridad",
                detalle=f"Usuario '{st.session_state.user_login}' salió del sistema.",
                usuario=st.session_state.user_login,
                nombre_usuario=st.session_state.user_name,
                sucursal=st.session_state.get("sucursal_activa", "N/A")
            )
            for key in ["logged_in","user_role","user_name","user_login","user_cargo","user_registro","user_telefono"]:
                st.session_state.pop(key, None)
            st.rerun()

        # Pie de página en Sidebar (Créditos)
        st.markdown("---")
        st.markdown(
            f"<div style='text-align: center; color: #64748b; font-size: 11px;'>"
            f"© 2026 {config.APP_NAME}<br>"
            f"<a href='https://wa.me/593963241158' style='color:#3b82f6; text-decoration:none;'><b>Diseñado por Anthonny Dev</b></a>"
            f"</div>", 
            unsafe_allow_html=True
        )
