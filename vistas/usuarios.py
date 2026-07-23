"""
vistas/usuarios.py — Gestión de Usuarios (solo Administrador)
Permite crear/eliminar optometristas con sus datos para el certificado en Supabase.
"""
import os
import streamlit as st
import base64
from database import supabase

def _cargar_usuarios() -> dict:
    """Carga los usuarios desde Supabase y los retorna como diccionario."""
    if not supabase: return {}
    try:
        res = supabase.table("usuarios").select("*").execute()
        if res.data:
            # Convertir a formato dict con username como key
            return {row["username"]: row for row in res.data}
    except Exception as e:
        print(f"Error cargando usuarios: {e}")
    return {}

def _guardar_usuarios(data: dict):
    """Guarda/Actualiza múltiples usuarios en Supabase."""
    if not supabase: return
    try:
        records = []
        for username, udata in data.items():
            record = udata.copy()
            record["username"] = username
            records.append(record)
        if records:
            supabase.table("usuarios").upsert(records).execute()
    except Exception as e:
        print(f"Error guardando usuarios: {e}")

def _guardar_usuario(username: str, data: dict):
    """Guarda/Actualiza un solo usuario en Supabase."""
    if not supabase: return
    try:
        record = data.copy()
        record["username"] = username
        supabase.table("usuarios").upsert(record).execute()
    except Exception as e:
        print(f"Error guardando usuario: {e}")

def _eliminar_usuario(username: str):
    """Elimina un usuario de Supabase."""
    if not supabase: return
    try:
        supabase.table("usuarios").delete().eq("username", username).execute()
    except Exception as e:
        print(f"Error eliminando usuario: {e}")


def render_usuarios():
    # Solo el admin puede ver esta página
    if st.session_state.get("user_role") != "Administrador":
        st.error("Acceso restringido. Solo el Administrador puede gestionar usuarios.")
        return

    st.markdown("""
    <div class="page-header">
        <h1>👤 Gestión de Usuarios</h1>
        <p>Crea y administra los optometristas y vendedores (Supabase)</p>
    </div>
    """, unsafe_allow_html=True)

    usuarios = _cargar_usuarios()
    
    # ── CREAR NUEVO USUARIO ────────────────────────────────────────
    if not st.session_state.get("mostrando_crear_usuario", False):
        if st.button("➕ Nuevo Usuario", type="primary", use_container_width=True):
            st.session_state["mostrando_crear_usuario"] = True
            st.rerun()
    else:
        st.markdown("<div class='section-title'>➕ Registro de Nuevo Usuario</div>", unsafe_allow_html=True)
        with st.form("form_nuevo_usuario", clear_on_submit=True):
            nc1, nc2 = st.columns(2)
            nu_username = nc1.text_input("Nombre de usuario (login) *", placeholder="ej: anthonny")
            nu_password = nc2.text_input("Contraseña *", type="password", placeholder="••••••••")

            st.markdown("### 🔑 Permisos de Acceso")
            nu_accesos = st.multiselect(
                "Selecciona a qué módulos puede entrar este usuario:",
                options=["Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inventario", "Contabilidad", "Usuarios", "Configuracion"],
                default=["Pacientes", "Generar Orden", "Trabajos", "Ventas"]
            )
            st.divider()

            st.markdown("### 👤 Datos Personales y Profesionales")
            nd1, nd2, nd3 = st.columns(3)
            nu_nombre   = nd1.text_input("Nombre Completo *", placeholder="Opt. Juan Pérez")
            nu_cargo    = nd2.text_input("Cargo / Título", placeholder="Optometrista", value="Optometrista")
            nu_role     = nd3.selectbox("Rol en el sistema", ["Vendedor", "Optometrista", "Administrador"])

            ne1, ne2, ne3 = st.columns(3)
            nu_registro  = ne1.text_input("N° Registro Profesional SENESCYT", placeholder="OP-2024-XXXX")
            nu_telefono  = ne2.text_input("Teléfono", placeholder="+593 98 765 4321")
            nu_email     = ne3.text_input("Correo Electrónico", placeholder="nombre@optica.com")
            nu_activo    = st.checkbox("Activo (Permitir acceso)", value=True)

            from database import cargar_sucursales
            df_suc_db = cargar_sucursales()
            sucursales_disponibles = df_suc_db["nombre"].tolist() if not df_suc_db.empty else ["Matriz"]
            
            st.caption("Asignación de Sucursales")
            nu_sucursales = st.multiselect(
                "¿A qué sucursales tendrá acceso este usuario?",
                options=sucursales_disponibles,
                default=["Matriz"]
            )

            st.divider()
            st.markdown("### 🎨 Identidad Visual (para certificados PDF)")
            fi_col, lo_col = st.columns(2)
            with fi_col:
                st.caption("✍️ Firma del profesional (PNG recomendado, fondo blanco/transparente)")
                nu_firma = st.file_uploader(
                    "Subir imagen de firma",
                    type=["png", "jpg", "jpeg"],
                    key="firma_upload"
                )
            with lo_col:
                st.caption("🏥 Logo del establecimiento (aparecerá en los informes PDF)")
                nu_logo = st.file_uploader(
                    "Subir logotipo",
                    type=["png", "jpg", "jpeg"],
                    key="logo_upload_usr"
                )

            colb1, colb2 = st.columns([1, 1])
            submitted = colb1.form_submit_button("✅ Crear Usuario", type="primary", use_container_width=True)
            if colb2.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state["mostrando_crear_usuario"] = False
                st.rerun()

            if submitted:
                if not nu_username.strip() or not nu_password.strip() or not nu_nombre.strip():
                    st.error("⚠️ Usuario, contraseña y nombre son obligatorios.")
                elif nu_username.strip() in usuarios:
                    st.error(f"⚠️ El usuario '{nu_username}' ya existe.")
                else:
                    firma_b64 = None
                    if nu_firma is not None:
                        try:
                            firma_b64 = base64.b64encode(nu_firma.getvalue()).decode()
                        except Exception as e:
                            st.warning(f"No se pudo procesar la firma: {e}")
                    
                    logo_b64 = None
                    if nu_logo is not None:
                        try:
                            logo_b64 = base64.b64encode(nu_logo.getvalue()).decode()
                        except Exception as e:
                            st.warning(f"No se pudo procesar el logo: {e}")

                    new_user = {
                        "password":  nu_password.strip(),
                        "role":      nu_role if nu_activo else f"INACTIVO:{nu_role}",
                        "nombre":    nu_nombre.strip(),
                        "cargo":     nu_cargo.strip() or "Optometrista",
                        "registro":  nu_registro.strip(),
                        "telefono":  nu_telefono.strip(),
                        "email":     nu_email.strip(),
                        "sucursales_asignadas": nu_sucursales,
                        "accesos":   nu_accesos,
                        "firma_base64": firma_b64,
                        "logo_base64": logo_b64
                    }
                    
                    _guardar_usuario(nu_username.strip(), new_user)
                    # También guardar logo como archivo global si se sube
                    if nu_logo is not None:
                        try:
                            nu_logo.seek(0)
                            with open("logo.png", "wb") as f:
                                f.write(nu_logo.read())
                        except Exception:
                            pass
                    # AUDITORÍA: Creación de usuario
                    from database import registrar_auditoria
                    registrar_auditoria(
                        accion="Crear Usuario",
                        entidad="Usuario",
                        detalle=f"Nuevo usuario: {nu_username.strip()} | Nombre: {nu_nombre.strip()} | Rol: {nu_role} | SENESCYT: {nu_registro.strip()}",
                        usuario=st.session_state.get("user_login", ""),
                        nombre_usuario=st.session_state.get("user_name", ""),
                        sucursal=st.session_state.get("sucursal_activa", "")
                    )
                    st.session_state["mostrando_crear_usuario"] = False
                    st.success(f"✅ Usuario **{nu_nombre.strip()}** creado exitosamente.")
                    st.rerun()

    st.markdown("---")
    # ── LISTA DE USUARIOS ──────────────────────────────────────────
    st.markdown("<div class='section-title'>Usuarios registrados</div>", unsafe_allow_html=True)

    for username, data in usuarios.items():
        is_main_admin = username == "admin"
        with st.container():
            c1, c2, c3, c4 = st.columns([2.5, 2, 2, 1.2])
            is_active = not str(data.get("role", "")).startswith("INACTIVO:")
            display_role = str(data.get("role", "")).replace("INACTIVO:", "")
            
            c1.markdown(
                f"**{data.get('nombre', username)}**  \n"
                f"<span style='font-size:12.5px;color:#334155;font-weight:500;'>👤 `{username}` · {display_role}</span>",
                unsafe_allow_html=True
            )
            
            if not is_active:
                c1.markdown("<span style='background:#fee2e2;color:#b91c1c;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;'>🚫 ACCESO BLOQUEADO</span>", unsafe_allow_html=True)
            else:
                c1.markdown("<span style='background:#dcfce7;color:#15803d;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;'>✅ ACTIVO</span>", unsafe_allow_html=True)
            c2.caption(f"🏷️ {data.get('cargo', '—')}")
            c3.caption(f"📋 Reg: {data.get('registro', '—')}")
            
            # Mostrar sucursales asignadas
            sucursales_txt = ", ".join(data.get("sucursales_asignadas", ["Matriz"]))
            st.caption(f"🏢 **Sucursales:** {sucursales_txt}")
            
            with c4:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✏️", key=f"btn_edit_{username}", help="Editar datos"):
                        st.session_state["edit_usr_target"] = username
                with b2:
                    is_myself = username == st.session_state.get("user_login")
                    if not is_main_admin and not is_myself:
                        if st.button("🗑️", key=f"btn_del_{username}", help="Eliminar usuario"):
                            _eliminar_usuario(username)
                            # AUDITORÍA: Eliminación de usuario
                            from database import registrar_auditoria
                            registrar_auditoria(
                                accion="Eliminar Usuario",
                                entidad="Usuario",
                                detalle=f"Usuario eliminado: {username} | Nombre: {data.get('nombre','')}",
                                usuario=st.session_state.get("user_login", ""),
                                nombre_usuario=st.session_state.get("user_name", ""),
                                sucursal=st.session_state.get("sucursal_activa", "")
                            )
                            st.success(f"Usuario '{username}' eliminado.")
                            st.rerun()
                    elif is_myself:
                        st.caption("🔒 Tú")

            # --- FORMULARIO DE EDICIÓN ---
            if st.session_state.get("edit_usr_target") == username:
                with st.form(f"form_edit_{username}"):
                    st.markdown("#### ✏️ Editando: `{username}`")
                    
                    st.markdown("### 🔑 Permisos de Acceso")
                    current_accesos = data.get("accesos", ["Pacientes", "Trabajos", "Ventas"])
                    en_accesos = st.multiselect(
                        "Selecciona a qué módulos puede entrar este usuario:",
                        options=["Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inventario", "Contabilidad", "Usuarios", "Configuracion"],
                        default=[a for a in current_accesos if a in ["Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inventario", "Contabilidad", "Usuarios", "Configuracion"]]
                    )
                    st.divider()

                    e1, e2, e3 = st.columns([1, 1, 1])
                    en_username = e1.text_input("Usuario (Login)", value=username)
                    en_nombre = e2.text_input("Nombre Completo", value=data.get("nombre", ""))
                    
                    # Limpiar rol para el selectbox
                    raw_role = data.get("role", "Optometrista")
                    current_clean_role = str(raw_role).replace("INACTIVO:", "")
                    en_role   = e3.selectbox("Rol", ["Vendedor", "Optometrista", "Administrador"], 
                                           index=0 if current_clean_role=="Vendedor" else (1 if current_clean_role=="Optometrista" else 2))
                    
                    e3_2, e4 = st.columns(2)
                    en_cargo    = e3_2.text_input("Cargo / Título", value=data.get("cargo", ""))
                    en_registro = e4.text_input("N° Registro Profesional", value=data.get("registro", ""))
                    
                    e5, e6, e7 = st.columns([1, 1, 1])
                    en_telefono = e5.text_input("Teléfono", value=data.get("telefono", ""))
                    en_password = e6.text_input("Nueva Contraseña", type="password", placeholder="Dejar vacío...")
                    
                    is_currently_active = not str(raw_role).startswith("INACTIVO:")
                    en_activo   = e7.checkbox("Permitir acceso al sistema", value=is_currently_active)
                    
                    from database import cargar_sucursales
                    df_suc_db = cargar_sucursales()
                    sucursales_disponibles = df_suc_db["nombre"].tolist() if not df_suc_db.empty else ["Matriz"]
                    
                    current_sucursales = data.get("sucursales_asignadas", ["Matriz"])
                    en_sucursales = st.multiselect(
                        "Sucursales asignadas",
                        options=sucursales_disponibles,
                        default=[s for s in current_sucursales if s in sucursales_disponibles]
                    )

                    st.markdown("---")
                    en_firma = st.file_uploader("Nueva firma", type=["png", "jpg", "jpeg"], key=f"edit_firma_{username}")

                    eb1, eb2 = st.columns([1, 1])
                    if eb1.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                        new_user = en_username.strip()
                        data["nombre"]   = en_nombre.strip()
                        data["role"]     = en_role if en_activo else f"INACTIVO:{en_role}"
                        data["cargo"]    = en_cargo.strip()
                        data["registro"] = en_registro.strip()
                        data["telefono"] = en_telefono.strip()
                        data["sucursales_asignadas"] = en_sucursales
                        data["accesos"] = en_accesos
                        if en_password.strip():
                            data["password"] = en_password.strip()
                        
                        if en_firma is not None:
                            try:
                                data["firma_base64"] = base64.b64encode(en_firma.getvalue()).decode()
                            except: pass
                        
                        # Si cambió el login, borramos el viejo primero
                        if new_user != username:
                            from database import supabase
                            if supabase:
                                supabase.table("usuarios").delete().eq("username", username).execute()
                            username = new_user
                        
                        _guardar_usuario(username, data)
                        # AUDITORÍA: Edición de usuario
                        from database import registrar_auditoria
                        registrar_auditoria(
                            accion="Editar Usuario",
                            entidad="Usuario",
                            detalle=f"Usuario editado: {username} | Nombre: {data.get('nombre','')} | Rol: {data.get('role','')}",
                            usuario=st.session_state.get("user_login", ""),
                            nombre_usuario=st.session_state.get("user_name", ""),
                            sucursal=st.session_state.get("sucursal_activa", "")
                        )
                        # Actualizar sesion si el editado es el usuario activo
                        if st.session_state.get("user_login") == username:
                            st.session_state.user_name     = data["nombre"]
                            st.session_state.user_role     = data["role"]
                            st.session_state.user_cargo    = data["cargo"]
                            st.session_state.user_registro = data["registro"]
                            st.session_state.user_telefono = data["telefono"]
                            if data.get("firma_base64"):
                                st.session_state["user_firma"] = data["firma_base64"]

                        st.session_state["edit_usr_target"] = None
                        st.success(f"Usuario '{username}' actualizado.")
                        st.rerun()
                        
                    if eb2.form_submit_button("❌ Cancelar", use_container_width=True):
                        st.session_state["edit_usr_target"] = None
                        st.rerun()
            st.divider()

