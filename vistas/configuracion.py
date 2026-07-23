import streamlit as st
import pandas as pd
import base64
from database import cargar_sucursales, guardar_sucursal, eliminar_sucursal, cargar_auditoria, obtener_resumen_dia
from utils.firma_sri import cargar_config_empresa, guardar_config_empresa, validar_config_sri, dias_para_vencimiento_firma

def render_configuracion():
    st.title("⚙️ Configuración del Sistema")
    
    if "suc_msg" in st.session_state:
        st.toast(st.session_state.pop("suc_msg"))

    tabs_names = ["🏢 Gestión de Sedes", "👤 Mi Perfil", "🎨 Personalización Visual", "🏛️ Emisor y SRI"]
    is_admin = st.session_state.get("user_role") == "Administrador"
    if is_admin:
        tabs_names.append("📋 Auditoría")

    st_tabs = st.tabs(tabs_names)
    tab1 = st_tabs[0]
    tab2 = st_tabs[1]
    tab_custom = st_tabs[2]
    tab_sri = st_tabs[3]
    
    with tab1:
        st.subheader("Locales y Sucursales")
        st.info("Aquí puedes definir las direcciones y teléfonos de cada local para que aparezcan en los certificados PDF.")
        
        df_suc = cargar_sucursales()
        
        with st.expander("➕ Añadir Nueva Sede", expanded=False):
            with st.form("form_nueva_sede", clear_on_submit=True):
                c1, c2 = st.columns(2)
                n_nombre = c1.text_input("Nombre de la Sede", placeholder="Ej: Sucursal Centro")
                n_ciudad = c2.text_input("Ciudad", value="Quito")
                n_direccion = st.text_input("Dirección Exacta", placeholder="Av. Principal y Calle Secundaria")
                n_telefono = st.text_input("Teléfono de la Sede", placeholder="02-XXXX-XXX")
                
                if st.form_submit_button("💾 Guardar Sede", type="primary"):
                    if n_nombre and n_direccion:
                        success, msg = guardar_sucursal({
                            "nombre": n_nombre,
                            "direccion": n_direccion,
                            "telefono": n_telefono,
                            "ciudad": n_ciudad
                        })
                        if success:
                            st.session_state["suc_msg"] = f"✅ Sede '{n_nombre}' guardada correctamente."
                            st.rerun()
                        else:
                            st.error(f"❌ Error al guardar: {msg}")
                    else:
                        st.error("Nombre y Dirección son obligatorios.")

        if not df_suc.empty:
            for _, row in df_suc.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style='background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; margin-bottom: 10px;'>
                        <h4 style='margin:0; color:#1e293b;'>🏢 {row['nombre']}</h4>
                        <p style='margin:5px 0; font-size:14px; color:#64748b;'>📍 {row['direccion']} — {row['ciudad']}</p>
                        <p style='margin:0; font-size:13px; color:#94a3b8;'>📞 {row.get('telefono', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c2:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_suc_{row['id']}"):
                                e_nombre = st.text_input("Nombre", value=row['nombre'])
                                e_ciudad = st.text_input("Ciudad", value=row.get('ciudad', 'Quito'))
                                e_direccion = st.text_input("Dirección", value=row['direccion'])
                                e_telefono = st.text_input("Teléfono", value=row.get('telefono', ''))
                                
                                if st.form_submit_button("Actualizar"):
                                    success, msg = guardar_sucursal({
                                        "id": row['id'],
                                        "nombre": e_nombre,
                                        "direccion": e_direccion,
                                        "telefono": e_telefono,
                                        "ciudad": e_ciudad
                                    })
                                    if success:
                                        st.session_state["suc_msg"] = f"✅ Sede '{e_nombre}' actualizada con éxito."
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {msg}")
                    with c3:
                        if st.button("🗑️ Eliminar", key=f"del_suc_{row['id']}", use_container_width=True):
                            eliminar_sucursal(row['id'])
                            st.success("Sede eliminada.")
                            st.rerun()
        else:
            st.warning("No hay sedes registradas. Por favor añade la 'Matriz' primero.")

    with tab2:
        st.subheader("Información del Usuario")
        st.write(f"**Usuario:** {st.session_state.get('user_login')}")
        st.write(f"**Nombre:** {st.session_state.get('user_name')}")
        st.write(f"**Rol:** {st.session_state.get('user_role')}")
        st.write(f"**Cargo:** {st.session_state.get('user_cargo')}")

    with tab_custom:
        st.subheader("🎨 Personalización de Apariencia")
        st.info("Sube una imagen para cambiar el fondo de pantalla o el logotipo del sistema.")

        col_bg, col_logo = st.columns(2)
        with col_bg:
            st.markdown("### 🖼️ Imagen de Fondo")
            bg_file = st.file_uploader("Seleccionar imagen de fondo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="upload_bg")
            if bg_file:
                with open("main_bg.png", "wb") as f:
                    f.write(bg_file.read())
                st.success("✅ Fondo de pantalla actualizado con éxito.")
                st.rerun()

        with col_logo:
            st.markdown("### 👁️ Logo del Sistema")
            logo_file = st.file_uploader("Seleccionar logotipo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="upload_logo")
            if logo_file:
                with open("logo.png", "wb") as f:
                    f.write(logo_file.read())
                st.success("✅ Logotipo actualizado con éxito.")
                st.rerun()

    # ══════════════════════════════════════════════════════════
    # TAB: EMISOR Y FIRMA ELECTRÓNICA SRI
    # ══════════════════════════════════════════════════════════
    with tab_sri:
        sucursal_act = st.session_state.get("sucursal_activa", "Matriz")
        cfg = cargar_config_empresa(sucursal_act)

        # Alerta de vencimiento de firma
        dias_venc = dias_para_vencimiento_firma(cfg)
        if dias_venc is not None:
            if dias_venc < 0:
                st.error(f"⛔ **Certificado de firma VENCIDO** hace {abs(dias_venc)} días. Renuévalo urgente.")
            elif dias_venc <= 30:
                st.warning(f"⚠️ El certificado vence en **{dias_venc} días**. Planifica su renovación.")
            else:
                st.success(f"✅ Certificado vigente por {dias_venc} días más.")

        st.markdown("""
            <div style='background:#eff6ff; border-left:5px solid #2563eb; border-radius:6px; padding:15px 20px; margin-bottom:20px;'>
                <b style='color:#1e40af;'>🏛️ Datos del Emisor y Facturación Electrónica SRI</b><br>
                <span style='font-size:13px; color:#3730a3;'>
                    Configura aquí los datos legales del establecimiento y sube tu certificado <b>.p12</b>
                    para emitir facturas electrónicas autorizadas por el SRI.
                </span>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("📄 Datos del Emisor")
        with st.form("form_emisor_sri"):
            s1, s2 = st.columns(2)
            ruc         = s1.text_input("RUC del Emisor*", value=cfg.get("ruc", ""), placeholder="1724219463001")
            razon       = s2.text_input("Razón Social*", value=cfg.get("razon_social", ""), placeholder="GUATO ANTHONNY")

            s3, s4 = st.columns(2)
            comercial   = s3.text_input("Nombre Comercial", value=cfg.get("nombre_comercial", ""), placeholder="HAPPY VISION")
            actividad   = s4.text_input("Actividad Económica", value=cfg.get("actividad_economica", ""), placeholder="Servicios de Optometría")

            s5, s6 = st.columns(2)
            dir_matriz  = s5.text_input("Dirección Matriz*", value=cfg.get("direccion_matriz", ""))
            telefono    = s6.text_input("Teléfono", value=cfg.get("telefono", ""))

            s7, s8 = st.columns(2)
            email_inst  = s7.text_input("Email Institucional", value=cfg.get("email", ""))
            regimen     = s8.selectbox("Régimen Tributario",
                                       ["General", "RIMPE Emprendedor", "RIMPE Negocio Popular (RISE)"],
                                       index=["General", "RIMPE Emprendedor", "RIMPE Negocio Popular (RISE)"].index(
                                           cfg.get("regimen", "General")) if cfg.get("regimen") in ["General", "RIMPE Emprendedor", "RIMPE Negocio Popular (RISE)"] else 0)

            st.divider()
            st.markdown("**⚙️ Configuración de Comprobantes**")
            c1, c2, c3, c4 = st.columns(4)
            estab      = c1.text_input("Establecimiento", value=cfg.get("establecimiento", "001"), max_chars=3)
            pto_emision = c2.text_input("Punto Emisión", value=cfg.get("punto_emision", "001"), max_chars=3)
            secuencial  = c3.number_input("Secuencial Actual", value=int(cfg.get("secuencial_actual", 1)), min_value=1, step=1)
            ambiente    = c4.selectbox("Ambiente SRI",
                                       ["PRUEBAS", "PRODUCCION"],
                                       index=0 if cfg.get("ambiente_sri", "PRUEBAS") == "PRUEBAS" else 1,
                                       help="PRUEBAS = sin valor legal. PRODUCCION = facturas reales.")

            st.divider()
            st.markdown("**🔐 Firma Electrónica (.p12)**")
            st.caption("El archivo .p12 es tu certificado de firma electrónica emitido por BCE, Security Data, ANF u otra entidad autorizada.")

            if cfg.get("firma_p12_b64"):
                st.info("✅ Ya tienes un certificado cargado. Sube uno nuevo solo si quieres reemplazarlo.")

            fe1, fe2 = st.columns(2)
            archivo_p12 = fe1.file_uploader("Certificado .p12 o .pfx",
                                             type=["p12", "pfx"],
                                             key="upload_p12",
                                             help="Archivo de firma electrónica emitido por la entidad certificadora")
            password_p12 = fe2.text_input("Contraseña del certificado",
                                          type="password",
                                          value="" if not cfg.get("firma_password") else "●●●●●●●●",
                                          key="pwd_p12",
                                          placeholder="Contraseña del .p12")
            vigencia_p12 = st.date_input("Fecha de Vencimiento del Certificado",
                                          value=None,
                                          key="vig_p12",
                                          help="Fecha en que vence el certificado .p12")

            guardado = st.form_submit_button("💾 Guardar Configuración SRI", type="primary", use_container_width=True)

        if guardado:
            datos_guardar = {
                "sucursal": sucursal_act,
                "ruc": ruc.strip(),
                "razon_social": razon.strip(),
                "nombre_comercial": comercial.strip() or razon.strip(),
                "actividad_economica": actividad.strip(),
                "direccion_matriz": dir_matriz.strip(),
                "telefono": telefono.strip(),
                "email": email_inst.strip(),
                "regimen": regimen,
                "establecimiento": estab.strip().zfill(3),
                "punto_emision": pto_emision.strip().zfill(3),
                "secuencial_actual": int(secuencial),
                "ambiente_sri": ambiente,
                "actualizado_por": st.session_state.get("user_login", "admin")
            }

            # Procesar archivo .p12 si se subió
            if archivo_p12 is not None:
                datos_guardar["firma_p12_b64"] = base64.b64encode(archivo_p12.getvalue()).decode()

            # Contraseña (solo si cambió)
            if password_p12 and password_p12 != "●●●●●●●●":
                datos_guardar["firma_password"] = password_p12

            if vigencia_p12:
                datos_guardar["firma_vigente_hasta"] = str(vigencia_p12)

            if not datos_guardar.get("ruc") or not datos_guardar.get("razon_social"):
                st.error("⚠️ RUC y Razón Social son obligatorios.")
            else:
                ok = guardar_config_empresa(datos_guardar)
                if ok:
                    st.success("✅ Configuración SRI guardada correctamente.")
                    # Validar inmediatamente
                    cfg_nueva = cargar_config_empresa(sucursal_act)
                    es_valida, errores = validar_config_sri(cfg_nueva)
                    if es_valida:
                        st.success("✅ Configuración completa. Puedes emitir facturas electrónicas.")
                    else:
                        st.warning("⚠️ Configuración incompleta:\n" + "\n".join(f"• {e}" for e in errores))
                else:
                    st.error("Error al guardar. Verifica la conexión a Supabase.")

        # PROBAR CONEXIÓN SRI (ambiente PRUEBAS)
        st.markdown("---")
        st.markdown("**🔬 Verificación de Configuración**")
        col_test1, col_test2 = st.columns(2)
        with col_test1:
            if st.button("🔍 Validar Configuración Actual", use_container_width=True):
                cfg_act = cargar_config_empresa(sucursal_act)
                es_valida, errores = validar_config_sri(cfg_act)
                if es_valida:
                    st.success("✅ Todo listo para facturar electrónicamente.")
                    amb = cfg_act.get("ambiente_sri", "PRUEBAS")
                    st.info(f"Ambiente activo: **{amb}** {'🟡' if amb == 'PRUEBAS' else '🟢'}")
                else:
                    for err in errores:
                        st.error(err)
        with col_test2:
            st.markdown("""
                <div style='background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:12px; font-size:13px;'>
                <b>¿Qué necesita el cliente?</b><br>
                ☑ RUC activo en SRI<br>
                ☑ Autorización para emisión electrónica en SRI<br>
                ☑ Certificado .p12 de entidad certificadora<br>
                ☑ Contraseña del certificado<br>
                </div>
            """, unsafe_allow_html=True)

    if is_admin:
        with st_tabs[4]:
            st.subheader("📋 Registro de Auditoría")
            tabs_admin = st.tabs(["📊 Auditoría de Cambios", "👤 Control de Sesiones"])
            
            with tabs_admin[0]:
                st.info("Registro inmutable de cambios en Pacientes, Historias, Inventario y Laboratorio.")
                
                # RESUMEN CONTABLE GLOBAL (TODAS LAS SEDES)
                df_s = cargar_sucursales()
                sedes = df_s["nombre"].tolist() if not df_s.empty else ["Matriz"]
                hoy = pd.Timestamp.now().strftime("%Y-%m-%d")
                
                t_ventas = 0
                t_gastos = 0
                for s in sedes:
                    res = obtener_resumen_dia(s, hoy)
                    t_ventas += (res["Efectivo"] + res["Tarjeta"] + res["Transferencia"])
                    t_gastos += res["Gastos"]
                
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("💰 Ventas Globales (Hoy)", f"${t_ventas:.2f}")
                c_m2.metric("📉 Gastos Globales (Hoy)", f"${t_gastos:.2f}")
                c_m3.metric("📈 Utilidad Bruta", f"${t_ventas - t_gastos:.2f}")
                st.markdown("---")
                
                df_auditoria = cargar_auditoria(limit=2000)
                if not df_auditoria.empty:
                    # Filtrar para NO mostrar seguridad aquí
                    df_cambios = df_auditoria[df_auditoria["entidad"] != "Seguridad"]
                    
                    if "fecha_hora" in df_cambios.columns:
                        df_cambios["fecha_hora"] = pd.to_datetime(df_cambios["fecha_hora"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    c1, c2 = st.columns(2)
                    filtro_usr = c1.selectbox("Filtrar por Usuario", ["Todos"] + df_cambios["usuario"].unique().tolist(), key="f_usr_aud")
                    filtro_acc = c2.selectbox("Filtrar por Acción", ["Todas"] + df_cambios["accion"].unique().tolist(), key="f_acc_aud")
                    
                    df_view = df_cambios.copy()
                    if filtro_usr != "Todos": df_view = df_view[df_view["usuario"] == filtro_usr]
                    if filtro_acc != "Todas": df_view = df_view[df_view["accion"] == filtro_acc]
                    
                    st.dataframe(df_view[["fecha_hora", "nombre_usuario", "accion", "entidad", "detalle", "sucursal"]], use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay registros de cambios.")

            with tabs_admin[1]:
                st.info("Registro de accesos al sistema (Inicios de sesión, salidas e intentos fallidos).")
                if not df_auditoria.empty:
                    # Filtrar para mostrar SOLO seguridad aquí
                    df_sesiones = df_auditoria[df_auditoria["entidad"] == "Seguridad"]
                    
                    if "fecha_hora" in df_sesiones.columns:
                        df_sesiones["fecha_hora"] = pd.to_datetime(df_sesiones["fecha_hora"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    st.dataframe(df_sesiones[["fecha_hora", "usuario", "accion", "detalle", "sucursal"]], use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay registros de sesiones.")
